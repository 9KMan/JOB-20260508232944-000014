"""Australian Business Register (abr.business.gov.au) scraper."""
from typing import Dict, List
import re
from bs4 import BeautifulSoup
from .base import BaseSpider


POSTCODES_BY_STATE = {
    "NSW": ["2000-2999"],
    "VIC": ["3000-3999"],
    "QLD": ["4000-4999"],
    "SA": ["5000-5999"],
    "WA": ["6000-6999"],
    "TAS": ["7000-7999"],
    "ACT": ["2600-2699", "2900-2999"],
    "NT": ["0800-0999"]
}


class ABRSpider(BaseSpider):
    BASE_URL = "https://abr.business.gov.au"

    def get_start_urls(self) -> List[str]:
        urls = []
        for state, ranges in POSTCODES_BY_STATE.items():
            for rng in ranges:
                start, end = rng.split("-")
                first = start[:2]
                urls.append(f"{self.BASE_URL}/Search?Location={first}&x=0&y=0")
        return list(set(urls))

    def extract_company_info(self, soup: BeautifulSoup, url: str) -> Dict:
        info = {"source_url": url}
        name_elem = soup.find("div", class_="business-name")
        if name_elem:
            info["name"] = name_elem.get_text(strip=True)
        abn_elem = soup.find("span", class_="abn-value")
        if abn_elem:
            abn = abn_elem.get_text(strip=True).replace(" ", "")
            info["abn"] = abn
        address_elem = soup.find("div", class_="address")
        if address_elem:
            info["address"] = address_elem.get_text(strip=True)
        state_match = re.search(r'\b([A-Z]{2,3})\s+(\d{4})\b', info.get("address", ""))
        if state_match:
            info["state"] = state_match.group(1)
            info["postcode"] = state_match.group(2)
        return info if info.get("name") else None