# Weekly Wayback Archiver

A production-ready GitHub Actions-powered archiver that intelligently crawls specific websites and submits them to the Internet Archive's Save Page Now (SPN2) API.

## Architecture

This project is built defensively to prevent accidentally archiving thousands of irrelevant URLs. 

- **Discovery:** Discovers pages via XML sitemaps and HTML fallback.
- **Filtering:** Filters out query params, pagination, tags, search pages, etc.
- **Classification:** Differentiates normal pages from blog articles.
- **Representative Selection:** Captures exactly *one* representative blog article (to preserve the blog post design) while skipping the rest.
- **Submission:** Uses the authenticated SPN2 API to submit to Wayback with safe rate limiting.

## Local Development

```bash
# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run a dry-run for a specific site (Highly Recommended)
python crawler.py --site sikarcoachings --dry-run

# Run a dry-run for all sites
python crawler.py --dry-run
```

## Running Real Archives

To prevent accidents, the crawler runs in **dry-run** mode by default.

To enable real archives, set `ARCHIVE_ENABLED=true` and provide your Wayback Machine API keys.

```bash
export ARCHIVE_ENABLED=true
export WAYBACK_ACCESS_KEY="your_access_key"
export WAYBACK_SECRET_KEY="your_secret_key"
python crawler.py
```

## GitHub Actions

The archiver runs automatically every week (Sunday at 04:00 UTC, which is 09:30 AM IST).

**Important:** Before enabling the cron job to run real archives, you MUST:
1. Create GitHub Secrets for `WAYBACK_ACCESS_KEY` and `WAYBACK_SECRET_KEY`.
2. Create a GitHub Variable (or update the workflow file) to set `ARCHIVE_ENABLED=true`.

The workflow produces a `run-results.json` artifact containing full telemetry of the run.

## Adding a New Site

Simply edit `sites.json`. The archiver uses this config file dynamically.

```json
{
  "name": "example",
  "base_url": "https://example.com/",
  "blog": {
    "enabled": true,
    "index_urls": ["https://example.com/blog/"],
    "article_patterns": ["/blog/"]
  }
}
```
