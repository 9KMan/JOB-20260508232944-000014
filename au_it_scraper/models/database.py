"""Database models and SQLite operations."""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict


class Database:
    SCHEMA = """
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        website TEXT,
        email TEXT,
        phone TEXT,
        address TEXT,
        state TEXT,
        postcode TEXT,
        abn TEXT,
        services TEXT,
        source_url TEXT,
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS url_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE NOT NULL,
        source TEXT,
        status TEXT DEFAULT 'pending',
        attempts INTEGER DEFAULT 0,
        last_error TEXT
    );

    CREATE INDEX IF NOT EXISTS idx_companies_abn ON companies(abn);
    CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
    CREATE INDEX IF NOT EXISTS idx_url_queue_status ON url_queue(status);
    """

    def __init__(self, path: str = "au_it_scraper.db"):
        self.conn = sqlite3.connect(path)
        self.conn.executescript(self.SCHEMA)

    def insert_company(self, company: Dict) -> int:
        cols = ["name", "website", "email", "phone", "address", "state",
                "postcode", "abn", "services", "source_url"]
        vals = {k: company.get(k) for k in cols}
        placeholders = ", ".join(["?"] * len(cols))
        sql = f"INSERT INTO companies ({', '.join(cols)}) VALUES ({placeholders})"
        cursor = self.conn.execute(sql, [vals[c] for c in cols])
        self.conn.commit()
        return cursor.lastrowid

    def update_company(self, id: int, company: Dict):
        sets = [f"{k} = ?" for k in company.keys()]
        sql = f"UPDATE companies SET {', '.join(sets)} WHERE id = ?"
        self.conn.execute(sql, list(company.values()) + [id])
        self.conn.commit()

    def update_companies(self, companies: List[Dict]):
        for comp in companies:
            if "id" in comp:
                self.update_company(comp["id"], {k: v for k, v in comp.items() if k != "id"})
        self.conn.commit()

    def get_all_companies(self) -> List[Dict]:
        cursor = self.conn.execute("SELECT * FROM companies")
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def get_company_by_abn(self, abn: str) -> Optional[Dict]:
        cursor = self.conn.execute("SELECT * FROM companies WHERE abn = ?", (abn,))
        row = cursor.fetchone()
        if row:
            cols = [d[0] for d in cursor.description]
            return dict(zip(cols, row))
        return None

    def insert_url(self, url: str, source: str) -> Optional[int]:
        try:
            cursor = self.conn.execute(
                "INSERT OR IGNORE INTO url_queue (url, source) VALUES (?, ?)",
                (url, source)
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return 0

    def get_pending_urls(self, limit: int = 100) -> List[Dict]:
        cursor = self.conn.execute(
            "SELECT * FROM url_queue WHERE status = 'pending' ORDER BY id LIMIT ?",
            (limit,)
        )
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def mark_url_done(self, url_id: int):
        self.conn.execute("UPDATE url_queue SET status = 'done' WHERE id = ?", (url_id,))
        self.conn.commit()

    def mark_url_failed(self, url_id: int, error: str):
        self.conn.execute(
            "UPDATE url_queue SET status = 'failed', attempts = attempts + 1, last_error = ? WHERE id = ?",
            (error, url_id)
        )
        self.conn.commit()

    def close(self):
        self.conn.close()