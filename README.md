# AU IT Company Scraper

Web scraping pipeline to collect publicly available contact data for Australian IT companies — company name, website, email, phone, physical address, ABN, and services. Designed for outreach list building.

**Stack:** Python 3.10+ · Scrapy-inspired async HTTP · BeautifulSoup · SQLite (checkpoint) · ABN/email/phone validators

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run full scrape (all sources, unlimited)
python main.py --source all --export results.csv

# Scrape one source with a limit
python main.py --source yellowpages --limit 100

# Deduplicate and export
python main.py --source all --dedupe --export results.csv
```

---

## Architecture

```
yellowpages.com.au ──▶ YellowPagesSpider ──┐
austech.io ──────────▶ AustechSpider ────────┼──▶ SQLite
abr.business.gov.au ─▶ ABRSpider ────────────┘   (checkpoint every 100 records)
                                                          │
                                                    ┌─────▼─────┐
                                                    │ URL Queue │
                                                    │ (pending  │
                                                    │  domains) │
                                                    └───────────┘
                                                          │
                                                      ▼
                                          ┌───────────────┐
                                          │  Validators   │
                                          │  ABN checksum │
                                          │  Email MX     │
                                          │  Phone format │
                                          └───────────────┘
                                                          │
                                          ┌───────────────┐
                                          │  Normalizer   │
                                          │  Deduplicate  │
                                          │  Jaro-Winkler │
                                          └───────────────┘
                                                          │
                                              ┌───────────▼───────────┐
                                              │  CSV Exporter (UTF-8) │
                                              │  results.csv          │
                                              └───────────────────────┘
```

---

## Data Sources

| Source | URL Pattern | Fields Extracted |
|--------|-------------|-----------------|
| Yellow Pages AU | yp.com.au | name, address, phone, website, email, services, ABN |
| ASE Tech Directory | austech.io | name, website, services, state |
| Australian Business Register | abr.business.gov.au | name, ABN, address, state, postcode |

---

## Data Model

**`companies` table:**
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | auto-increment |
| name | TEXT NOT NULL | |
| website | TEXT | |
| email | TEXT | validated via MX before storage |
| phone | TEXT | normalized to +61 format |
| address | TEXT | |
| state | TEXT | NSW, VIC, QLD, etc. |
| postcode | TEXT | |
| abn | TEXT | validated with ABN checksum |
| services | TEXT | comma-separated |
| source_url | TEXT | origin URL |
| scraped_at | TIMESTAMP | |

**`url_queue` table:**
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| url | TEXT UNIQUE | |
| source | TEXT | which spider found it |
| status | TEXT | pending / done / failed |
| attempts | INTEGER | retry counter |
| last_error | TEXT | |

---

## CLI Reference

```bash
python main.py [options]

--source   yellowpages | austech | abr | all  (default: all)
--limit    N  Max URLs to process, 0=unlimited  (default: 0)
--dedupe   Run Jaro-Winkler deduplication before export
--export   PATH  CSV output path
```

**Examples:**
```bash
# Scrape Yellow Pages only, max 200 listings
python main.py --source yellowpages --limit 200

# Scrape all sources, deduplicate, save to CSV
python main.py --source all --dedupe --export my_company_list.csv

# Export existing database to CSV
python main.py --export results.csv
```

---

## Installation

**Requirements:**
- Python 3.10+
- pip

**Dependencies:**
```
beautifulsoup4   HTML parsing
lxml             XML/HTML parser (fast)
requests         HTTP client
phonenumbers     AU phone normalization (pip install phonenumbers)
rapidfuzz        Jaro-Winkler string similarity
```

Install all at once:
```bash
pip install -r requirements.txt

# phonenumbers requires libphonenumber C++ extension on some platforms
# Ubuntu/Debian: sudo apt-get install libphonenumber-dev
# macOS: brew install libphonenumber
```

---

## Configuration

No config file required — all settings are CLI flags.

For production runs with high concurrency, set domain rate limits in `au_it_scraper/scrapers/base.py`:
```python
REQUEST_DELAY = 1.0        # seconds between requests per domain
MAX_RETRIES = 3            # retry failed URLs up to 3 times
CHECKPOINT_EVERY = 100     # write to SQLite every N records
```

---

## Quality Guarantees

- **ABN checksum:** Every ABN is validated against the Australian Business Number algorithm before storage. Invalid ABNs are flagged and rejected.
- **Email MX validation:** Emails are checked for valid MX records (DNS lookup) before storage. Role-based addresses (info@, admin@) are flagged with a `generic_email` flag.
- **Phone normalization:** All phone numbers normalized to `+61 4XX XXX XXX` format via `phonenumbers` library.
- **Deduplication:** Exact match on ABN. Fuzzy match on name+address via Jaro-Winkler similarity > 0.9.
- **Checkpointing:** SQLite write after every 100 records — crash-resumable.
- **No blank required fields:** Required columns are name + at least one contact method (phone, email, or website). All other fields optional if data genuinely unavailable.

---

## Output Format

CSV (UTF-8, Excel-safe):
```csv
name,website,email,phone,address,state,postcode,abn,services,source_url,scraped_at
"Acme Tech Pty Ltd","https://acmetech.com.au","contact@acmetech.com.au","+61 3 9123 4567","Level 5, 123 Collins St","VIC","3000","12 345 678 901","IT Services, Software Development","https://yp.com.au/listing/123","2026-05-09T01:45:00"
```

---

## Project Structure

```
JOB-20260508232944-000014/
├── README.md
├── main.py                          # CLI entry point
├── requirements.txt
├── au_it_scraper/
│   ├── __init__.py
│   ├── models/
│   │   └── database.py              # SQLite schema + CRUD
│   ├── scrapers/
│   │   ├── base.py                  # BaseSpider: rate limit, retry, checkpoint
│   │   ├── yellowpages.py           # YellowPages spider
│   │   ├── austech.py              # Austech directory spider
│   │   └── abr.py                  # ABR register spider
│   ├── validators/
│   │   ├── abn_validator.py        # ABN checksum (mod 89)
│   │   ├── email_validator.py       # MX + syntax validation
│   │   └── phone_validator.py       # AU phone normalization
│   ├── normalizers/
│   │   └── company_normalizer.py    # Deduplication + Jaro-Winkler
│   ├── queue/
│   │   └── url_queue.py            # URL frontier management
│   └── exporters/
│       └── csv_exporter.py         # UTF-8 CSV export
└── SPEC.md                          # Full specification
```

---

## Limitations

- **LinkedIn:** Not scraped — LinkedIn blocks automated access and enforces strict TOS. Use Yellow Pages and ABR for contact data instead.
- **Email deliverability:** MX validation confirms the domain accepts mail, but cannot guarantee the specific address is actively monitored. Always validate against a real recipient before sending outreach.
- **Address accuracy:** ABN addresses reflect the registered business location, not necessarily operational/office locations.