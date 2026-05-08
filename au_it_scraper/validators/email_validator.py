"""Email validation using syntax check and MX lookup."""
import dns.resolver
import re
from typing import Optional


class EmailValidator:
    EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def validate_format(self, email: str) -> bool:
        return bool(self.EMAIL_RE.match(email))

    def validate_mx(self, email: str) -> bool:
        domain = email.split("@")[1] if "@" in email else ""
        if not domain:
            return False
        try:
            dns.resolver.resolve(domain, "MX")
            return True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            return False

    def validate(self, email: str) -> bool:
        if not email:
            return False
        return self.validate_format(email) and self.validate_mx(email)