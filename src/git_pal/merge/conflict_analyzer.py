import re
import difflib
from typing import List

def _normalize_whitespace(text: str) -> List[str]:
    normalized: List[str] = []
    for line in text.splitlines():
        # Strip leading/trailing whitespace
        line = line.strip()
        # Replace consecutive whitespace with single space
        line = re.sub(r"\s+", " ", line)
        # Remove spaces around operators and punctuation to treat "foo=1" and "foo = 1" as equivalent
        line = re.sub(r"\s*([=+\-*/<>!&|,;:(){}[\]])\s*", r"\1", line)
        normalized.append(line)
    return normalized

def is_diff_whitespace_only(a: str, b: str) -> bool:
    diff = list(difflib.ndiff(_normalize_whitespace(a), _normalize_whitespace(b)))
    return not any(d.startswith("+") or d.startswith("-") for d in diff)
