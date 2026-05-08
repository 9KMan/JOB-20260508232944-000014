"""Company data normalization including deduplication."""
from typing import Dict, List, Optional, Tuple
from ..validators.email_validator import EmailValidator
from ..validators.phone_validator import PhoneValidator
from ..validators.abn_validator import ABNValidator


class CompanyNormalizer:
    def __init__(self):
        self.email_validator = EmailValidator()
        self.phone_validator = PhoneValidator()
        self.abn_validator = ABNValidator()

    def normalize_company(self, company: Dict) -> Dict:
        if company.get("abn"):
            company["abn"] = self.abn_validator.normalize(company["abn"])
        if company.get("phone"):
            company["phone"] = self.phone_validator.normalize(company["phone"])
        if company.get("email"):
            company["email"] = company["email"].lower().strip()
        if company.get("address"):
            company["address"] = self._normalize_address(company["address"])
        return company

    def _normalize_address(self, addr: str) -> str:
        return " ".join(addr.split())

    def normalize_batch(self, companies: List[Dict]) -> List[Dict]:
        seen_abn = {}
        seen_name_addr = {}
        result = []
        for comp in companies:
            norm = self.normalize_company(comp.copy())
            if norm.get("abn") and norm["abn"] in seen_abn:
                continue
            if norm.get("name") and norm.get("address"):
                key = self._name_addr_key(norm["name"], norm["address"])
                if key in seen_name_addr:
                    continue
                seen_name_addr[key] = True
            result.append(norm)
            if norm.get("abn"):
                seen_abn[norm["abn"]] = True
        return result

    def _name_addr_key(self, name: str, addr: str) -> str:
        import re
        name_clean = re.sub(r"[^\w]", "", name.lower())
        addr_clean = re.sub(r"[^\w]", "", addr.lower())[:20]
        return f"{name_clean}:{addr_clean}"