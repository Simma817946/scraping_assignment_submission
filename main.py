import csv
import json
import logging
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from processing.cleaning import clean_record
from processing.deduplication import find_duplicates
from processing.validation import validate_record
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"
CSV_PATH = OUTPUT_DIR / "final_dataset.csv"
SUMMARY_PATH = OUTPUT_DIR / "summary_report.json"
LOG_PATH = LOG_DIR / "scraper.log"

COLUMNS = [
    "source", "source_url", "name_or_title", "category", "price",
    "rating", "author", "tags", "description", "scraped_at"
]


def configure_logging():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger()
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(LOG_PATH, mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def run_source(name, scraper):
    try:
        return scraper.scrape()
    except Exception:
        logging.getLogger(__name__).exception("Unexpected failure in %s scraper", name)
        return []
    finally:
        scraper.close()


def process_records(raw_records, source_name):
    logger = logging.getLogger(__name__)
    cleaned = []
    rejected = Counter()

    for raw in raw_records:
        record = clean_record(raw)
        problems = validate_record(record)
        if problems:
            rejected.update(problems)
            logger.warning("Rejected %s record: %s", source_name, problems)
        else:
            cleaned.append(record)

    unique, duplicates = find_duplicates(cleaned)
    for record in duplicates:
        logger.warning("Duplicate removed from %s: %s", source_name, record.get("name_or_title"))
    return cleaned, unique, duplicates, dict(rejected)


def write_csv(records):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def write_summary(summary):
    with open(SUMMARY_PATH, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4, ensure_ascii=False)


def main():
    configure_logging()
    logger = logging.getLogger(__name__)
    started_clock = time.perf_counter()
    started_at = datetime.now(timezone.utc)
    timestamp = started_at.isoformat()

    logger.info("=== Scraping assignment started ===")
    books_raw = run_source("Books to Scrape", BooksScraper())
    quotes_raw = run_source("Quotes to Scrape", QuotesScraper())

    for record in books_raw + quotes_raw:
        record["scraped_at"] = timestamp

    books_cleaned, books_unique, books_dupes, books_rejected = process_records(books_raw, "Books to Scrape")
    quotes_cleaned, quotes_unique, quotes_dupes, quotes_rejected = process_records(quotes_raw, "Quotes to Scrape")

    final_records = books_unique + quotes_unique
    write_csv(final_records)

    ended_at = datetime.now(timezone.utc)
    duration = round(time.perf_counter() - started_clock, 3)
    rejected_total = (len(books_raw) - len(books_cleaned)) + (len(quotes_raw) - len(quotes_cleaned))
    duplicate_total = len(books_dupes) + len(quotes_dupes)
    expected_final = len(books_raw) + len(quotes_raw) - rejected_total - duplicate_total

    summary = {
        "run": {
            "started_at_utc": started_at.isoformat(),
            "ended_at_utc": ended_at.isoformat(),
            "duration_seconds": duration,
        },
        "records": {
            "collected_per_source": {
                "Books to Scrape": len(books_raw),
                "Quotes to Scrape": len(quotes_raw),
            },
            "after_cleaning_per_source": {
                "Books to Scrape": len(books_cleaned),
                "Quotes to Scrape": len(quotes_cleaned),
            },
            "rejected_per_source": {
                "Books to Scrape": len(books_raw) - len(books_cleaned),
                "Quotes to Scrape": len(quotes_raw) - len(quotes_cleaned),
            },
            "rejected_by_reason": {
                "Books to Scrape": books_rejected,
                "Quotes to Scrape": quotes_rejected,
            },
            "duplicates_detected_per_source": {
                "Books to Scrape": len(books_dupes),
                "Quotes to Scrape": len(quotes_dupes),
            },
            "duplicates_detected_total": duplicate_total,
            "final_record_count": len(final_records),
        },
        "reconciliation": {
            "expected_final_count": expected_final,
            "actual_final_count": len(final_records),
            "matches": expected_final == len(final_records),
        },
        "outputs": {
            "csv": "output/final_dataset.csv",
            "summary": "output/summary_report.json",
            "log": "logs/scraper.log",
        },
    }
    write_summary(summary)
    logger.info("Final records: %d", len(final_records))
    logger.info("=== Scraping assignment completed ===")


if __name__ == "__main__":
    main()
