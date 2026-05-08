"""Phone number normalization for Australian format."""
import re
import phonenumbers
from typing import Optional


class PhoneValidator:
    def normalize(self, phone: str) -> Optional[str]:
        if not phone:
            return None
        try:
            parsed = phonenumbers.parse(phone, "AU")
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            pass
        cleaned = re.sub(r"[^\d+]", "", phone)
        if cleaned.startswith("61"):
            return f"+{cleaned[:2]} {cleaned[2:5]} {cleaned[5:]}"
        elif cleaned.startswith("0"):
            return f"+61 {cleaned[1:4]} {cleaned[4:]}"
        return phone

    def is_valid(self, phone: str) -> bool:
        if not phone:
            return False
        try:
            parsed = phonenumbers.parse(phone, "AU")
            return phonenumbers.is_valid_number(parsed)
        except phonenumbers.NumberParseException:
            return False