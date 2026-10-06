# Python Web Scraping Interview Assignment

## Overview

This project implements the required ETL pipeline for Books to Scrape and Quotes to Scrape:

`Scrape -> Clean -> Validate -> Deduplicate -> Consolidate -> Save`

## Python

The assignment requires Python 3.10-3.12. **Use Python 3.11 or 3.12 for the final submission.**

Check with:

```text
python --version
```

## Installation - Windows

From the project folder:

```text
py -3.11 -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `py -3.11` is unavailable, install Python 3.11/3.12 first. The assignment reference explicitly requires that range; do not submit using Python 3.8.5 unless the recruiter confirms it is acceptable.

## Run tests

```text
python -m pytest -q
```

Tests cover cleaning, validation, and duplicate detection without requiring internet access.

## Run the complete assignment

```text
python main.py
```

This creates:

```text
output/final_dataset.csv
output/summary_report.json
logs/scraper.log
```

## Source structure

### Books to Scrape

- Record: `article.product_pod`
- Title: `h3 > a` / `title` attribute
- Price: `p.price_color`
- Rating: class on `p.star-rating`
- URL: `h3 > a[href]`
- Next page: `li.next > a`

### Quotes to Scrape

- Record: `div.quote`
- Text: `span.text`
- Author: `small.author`
- Tags: `a.tag`
- Next page: `li.next > a`

## Pagination

Pagination is dynamic. Each scraper reads the `Next` link, converts the relative link with `urljoin`, and continues until no next link exists. Page numbers are not hard-coded.

## Common data model

```text
source
source_url
name_or_title
category
price
rating
author
tags
description
scraped_at
```

Source-specific fields that do not exist are left empty. Book category and description are not taken from the listing page, so this implementation does not guess them.

For quotes, `source_url` is the page where the quote appeared.

## Cleaning

- Collapse whitespace and non-breaking spaces.
- Remove surrounding quotation marks from quote text.
- Convert `£51.77` to `51.77`.
- Convert word ratings such as `Three` to `3`.
- Lowercase, sort, and join tags with `;`.
- Validate HTTP/HTTPS URLs.

## Validation

Records are rejected if:

- source is unknown;
- name/title is missing;
- source URL is not HTTP/HTTPS;
- price is invalid or negative;
- rating is not an integer from 1 to 5.

Reasons are recorded in the summary and warnings are written to the log.

## Deduplication

Duplicates are removed.

Books use `source + name_or_title`.

Quotes use `source + author + first 50 characters of name_or_title`.

The fingerprint input is lowercased, punctuation is removed, whitespace is collapsed, and SHA-256 is used for the fingerprint. Thus spacing and capitalization differences do not create separate records.

The real sites are expected to have unique records, so zero duplicates in a normal run is acceptable. Unit tests deliberately create duplicates to prove the logic.

## Error handling

A shared Requests session provides a User-Agent, timeout, retries for 429/500/502/503/504, and approximately 0.5 seconds between requests. Missing elements are checked before use. A malformed record is skipped. If a source page ultimately fails, that source stops gracefully and the other source still runs.

## Outputs

`output/final_dataset.csv`: consolidated valid unique records.

`output/summary_report.json`: counts per source, rejected reasons, duplicate counts, final count, timing, and reconciliation.

`logs/scraper.log`: requests, page progress, warnings, errors, and completion information.

## Assumptions / limitations

1. The public practice websites remain accessible.
2. Their HTML structure remains compatible with the selectors.
3. Category and description are left empty for books because the listing page does not expose them directly.
4. Quotes use the page URL as `source_url`.
5. A modest delay is used to avoid aggressive requests.
6. Internet access is required for the full scraper run.

## Submission checklist

Include:

```text
scrapers/
processing/
tests/
output/final_dataset.csv
output/summary_report.json
logs/scraper.log
main.py
requirements.txt
README.md
AI_USAGE.md
```

Do not include `venv/`, `__pycache__/`, or `.pyc` files.

## Interview answers

**Why Requests + BeautifulSoup?** Both sites are server-rendered HTML. A browser automation tool would add unnecessary overhead.

**How does pagination work?** The scraper follows `li.next > a` until there is no next link.

**How are missing fields handled?** Selectors are checked before reading them. Non-applicable fields remain empty rather than being invented.

**How are failures handled?** Requests retries temporary HTTP errors; failures are logged; one source does not prevent the other from running.

**How are duplicates detected?** Identifying fields are normalized and hashed with SHA-256.

**How did you verify it?** Unit tests cover cleaning, validation and deduplication; the full run is checked by comparing the CSV row count with the JSON reconciliation.
