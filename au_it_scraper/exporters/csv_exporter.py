"""CSV exporter for company data."""
import csv
from typing import Optional
from ..models.database import Database


class CSVExporter:
    COLUMNS = ["name", "website", "email", "phone", "address", "state", "postcode", "abn", "services", "source_url"]

    def __init__(self, db: Database):
        self.db = db

    def export(self, path: str, limit: Optional[int] = None) -> int:
        companies = self.db.get_all_companies()
        if limit:
            companies = companies[:limit]
        count = 0
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.COLUMNS, extrasaction="ignore")
            writer.writeheader()
            for comp in companies:
                writer.writerow({k: comp.get(k, "") for k in self.COLUMNS})
                count += 1
        return count