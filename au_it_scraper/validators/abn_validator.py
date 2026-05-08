"""ABN (Australian Business Number) validation using checksum algorithm."""
import re
from typing import Optional


class ABNValidator:
    ABN_RE = re.compile(r"^\d{11}$")

    def validate(self, abn: str) -> bool:
        if not abn:
            return False
        cleaned = re.sub(r"[^\d]", "", abn)
        if len(cleaned) != 11:
            return False
        digits = [int(d) for d in cleaned]
        digits[0] -= 1
        weights = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
        total = sum(d * w for d, w in zip(digits, weights))
        return total % 89 == 0

    def normalize(self, abn: str) -> Optional[str]:
        if not abn:
            return None
        cleaned = re.sub(r"[^\d]", "", abn)
        if len(cleaned) == 11:
            return cleaned
        return None