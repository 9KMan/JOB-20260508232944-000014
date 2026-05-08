"""Yellow Pages Australia scraper."""
from typing import Dict, List
from bs4 import BeautifulSoup
from .base import BaseSpider


CATEGORIES = [
    "computing", "it-services", "software", "web-design",
    "computer-repairs", "internet-services", "telecommunications"
]


class YellowPagesSpider(BaseSpider):
    BASE_URL = "https://www.yp.com.au"

    def get_start_urls(self) -> List[str]:
        urls = []
        for cat in CATEGORIES:
            urls.append(f"{self.BASE_URL}/search/{cat}?pos=AU&page=1")
        return urls

    def extract_company_info(self, soup: BeautifulSoup, url: str) -> Dict:
        info = {"source_url": url, "services": []}
        name_elem = soup.find("div", class_="listing-name")
        if name_elem:
            info["name"] = name_elem.get_text(strip=True)
        addr_elem = soup.find("div", class_="listing-address")
        if addr_elem:
            info["address"] = addr_elem.get_text(strip=True)
        phone_elem = soup.find("a", class_="phone-link")
        if phone_elem:
            info["phone"] = phone_elem.get_text(strip=True)
        web_elem = soup.find("a", class_="website-link")
        if web_elem:
            info["website"] = web_elem.get("href", "").replace("redirect=", "")
        email_elem = soup.find("a", class_="email-link")
        if email_elem:
            info["email"] = email_elem.get_text(strip=True)
        services_elem = soup.find("div", class_="services-list")
        if services_elem:
            info["services"] = services_elem.get_text(strip=True)
        abn_elem = soup.find("span", class_="abn")
        if abn_elem:
            info["abn"] = abn_elem.get_text(strip=True)
        self._extract_state_postcode(info)
        return info if info.get("name") else None

    def _extract_state_postcode(self, info: Dict):
        addr = info.get("address", "")
        import re
        match = re.search(r'\b([A-Z]{2,3})\s*(\d{4})\b', addr)
        if match:
            info["state"] = match.group(1)
            info["postcode"] = match.group(2)