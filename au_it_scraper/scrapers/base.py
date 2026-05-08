"""Base spider class for web scraping."""
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, List
import httpx
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BaseSpider(ABC):
    def __init__(self, db, queue, rate_limit: float = 1.0):
        self.db = db
        self.queue = queue
        self.rate_limit = rate_limit
        self.last_request_time = 0.0

    def throttle(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()

    async def fetch(self, url: str) -> Optional[str]:
        self.throttle()
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url, headers=self._get_headers())
                response.raise_for_status()
                return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def fetch_sync(self, url: str) -> Optional[str]:
        self.throttle()
        try:
            response = httpx.get(url, headers=self._get_headers(), timeout=30.0, follow_redirects=True)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def _get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-AU,en;q=0.9",
        }

    def parse_html(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "lxml")

    def fetch_js_rendered(self, url: str) -> Optional[str]:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=options)
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            return driver.page_source
        except Exception as e:
            print(f"JS render error for {url}: {e}")
            return None
        finally:
            driver.quit()

    @abstractmethod
    def extract_company_info(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        pass

    @abstractmethod
    def get_start_urls(self) -> List[str]:
        pass

    def run(self, limit: int = 0):
        start_urls = self.get_start_urls()
        for url in start_urls:
            self.queue.add_url(url, self.__class__.__name__)
        count = 0
        for pending in self.queue.get_pending(limit or 100):
            url = pending["url"]
            html = self.fetch_sync(url)
            if html:
                soup = self.parse_html(html)
                info = self.extract_company_info(soup, url)
                if info:
                    self.db.insert_company(info)
                    count += 1
            self.queue.mark_done(pending["id"])
            if limit and count >= limit:
                break