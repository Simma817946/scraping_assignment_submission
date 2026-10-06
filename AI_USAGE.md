# AI_USAGE.md

## Tool used

**ChatGPT**

## Purpose

AI assistance was used because the assignment explicitly allows AI. It was used for:

- understanding the requirements;
- planning the project structure;
- designing Requests + BeautifulSoup pagination;
- cleaning and validation ideas;
- duplicate-detection strategy;
- unit-test ideas;
- documentation and interview preparation;
- debugging and reviewing edge cases.

## Representative prompts

1. `Create a clean Python project structure for a medium-level web scraping assignment using Requests and BeautifulSoup, with separate scraping, processing, tests, output and logging layers.`
2. `Show how to implement dynamic pagination by following li.next > a instead of hard-coding page numbers.`
3. `Create reusable functions for whitespace cleanup, price conversion, rating conversion, tag normalization, URL validation and record validation.`
4. `Create pytest tests that prove duplicate detection ignores capitalization and whitespace differences.`

## AI-assisted areas

AI assisted with the initial architecture, code patterns, tests, error-handling ideas, and documentation. The final implementation was reviewed against the supplied assignment requirements.

## Review / corrections

The supplied reference document contains a placeholder in the summary-report code section, so the final project implements the complete summary writer itself.

The assignment requires Python 3.10-3.12. Therefore, Python 3.11 or 3.12 should be used for the submission even if an older Python installation is available on the development computer.

The implementation intentionally leaves book category and description empty instead of inventing data from an unrelated source.

## Verification

Run:

```text
python -m pytest -q
python main.py
```

Then verify that:

- both sources appear in the CSV;
- prices are numeric when present;
- ratings are 1-5 when present;
- source URLs are present;
- summary counts reconcile with the CSV;
- logs contain page progress and any errors/warnings.

## Candidate responsibility

AI is a development assistant. The candidate remains responsible for understanding and explaining every submitted part of the code, especially scraping, pagination, cleaning, validation, deduplication, retries, logging, and output generation.
