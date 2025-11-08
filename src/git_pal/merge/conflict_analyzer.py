import re
import difflib
from typing import List

def _normalize_whitespace(text: str) -> List[str]:
    normalized: List[str] = []
    for line in text.splitlines():
        normalized.append(re.sub(r"\s+", " ", line.strip()))
    return normalized

def is_diff_whitespace_only(a: str, b: str) -> bool:
    diff = list(difflib.ndiff(_normalize_whitespace(a), _normalize_whitespace(b)))
    return not any(d.startswith("+") or d.startswith("-") for d in diff)
