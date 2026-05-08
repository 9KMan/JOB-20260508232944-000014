#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from models.database import Database
from scrapers.yellowpages import YellowPagesSpider
from scrapers.austech import AustechSpider
from scrapers.abr import ABRSpider
from normalizers.company_normalizer import CompanyNormalizer
from exporters.csv_exporter import CSVExporter
from queue.url_queue import URLQueue


def main():
    parser = argparse.ArgumentParser(description="AU IT Company Scraper")
    parser.add_argument("--source", choices=["yellowpages", "austech", "abr", "all"],
                        default="all", help="Data source to scrape")
    parser.add_argument("--limit", type=int, default=0, help="Max URLs to process (0=unlimited)")
    parser.add_argument("--export", type=str, help="Export CSV path")
    parser.add_argument("--dedupe", action="store_true", help="Run deduplication before export")

    args = parser.parse_args()

    db = Database()
    queue = URLQueue(db)
    normalizer = CompanyNormalizer()

    if args.source in ("yellowpages", "all"):
        spider = YellowPagesSpider(db, queue)
        spider.run(limit=args.limit)

    if args.source in ("austech", "all"):
        spider = AustechSpider(db, queue)
        spider.run(limit=args.limit)

    if args.source in ("abr", "all"):
        spider = ABRSpider(db, queue)
        spider.run(limit=args.limit)

    if args.dedupe:
        records = db.get_all_companies()
        normalized = normalizer.normalize_batch(records)
        db.update_companies(normalized)

    if args.export:
        exporter = CSVExporter(db)
        exporter.export(args.export)
        print(f"Exported to {args.export}")


if __name__ == "__main__":
    main()