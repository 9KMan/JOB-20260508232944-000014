"""ASE Technology Directory (austech.io) scraper."""
from typing import Dict, List
from bs4 import BeautifulSoup
from .base import BaseSpider


class AustechSpider(BaseSpider):
    BASE_URL = "https://austech.io"

    def get_start_urls(self) -> List[str]:
        return [f"{self.BASE_URL}/directory"]

    def extract_company_info(self, soup: BeautifulSoup, url: str) -> Dict:
        info = {"source_url": url}
        name_elem = soup.find("h2", class_="company-name")
        if name_elem:
            info["name"] = name_elem.get_text(strip=True)
        website_elem = soup.find("a", class_="company-website")
        if website_elem:
            info["website"] = website_elem.get("href", "")
        desc_elem = soup.find("div", class_="company-description")
        if desc_elem:
            info["services"] = desc_elem.get_text(strip=True)[:500]
        contact_elem = soup.find("div", class_="contact-info")
        if contact_elem:
            email_link = contact_elem.find("a", href=lambda h: h and "mailto" in h)
            if email_link:
                info["email"] = email_link.get_text(strip=True)
            phone_link = contact_elem.find("a", href=lambda h: h and "tel:" in h)
            if phone_link:
                info["phone"] = phone_link.get_text(strip=True)
        address_elem = soup.find("div", class_="company-address")
        if address_elem:
            info["address"] = address_elem.get_text(strip=True)
        return info if info.get("name") else None