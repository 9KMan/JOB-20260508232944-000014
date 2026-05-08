"""URL queue management for crawl frontier."""
from typing import List, Optional
from ..models.database import Database


class URLQueue:
    def __init__(self, db: Database):
        self.db = db

    def add_url(self, url: str, source: str) -> int:
        return self.db.insert_url(url, source)

    def get_pending(self, limit: int = 100) -> List[dict]:
        return self.db.get_pending_urls(limit)

    def mark_done(self, url_id: int):
        self.db.mark_url_done(url_id)

    def mark_failed(self, url_id: int, error: str):
        self.db.mark_url_failed(url_id, error)

    def get_stats(self) -> dict:
        cursor = self.db.conn.execute(
            "SELECT status, COUNT(*) FROM url_queue GROUP BY status"
        )
        stats = {"pending": 0, "done": 0, "failed": 0}
        for row in cursor.fetchall():
            if row[0] in stats:
                stats[row[0]] = row[1]
        return stats