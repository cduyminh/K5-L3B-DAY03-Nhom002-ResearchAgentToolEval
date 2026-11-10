from __future__ import annotations

import re
from collections import Counter
from typing import Any


def word_count(text: str = "") -> dict[str, Any]:
    if not isinstance(text, str):
        return {"tool": "word_count", "error": "TypeError", "message": "text must be a string"}

    cleaned = re.findall(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)?", text.lower())
    count = len(cleaned)
    unique = len(set(cleaned))
    return {
        "tool": "word_count",
        "text": text,
        "word_count": count,
        "unique_words": unique,
        "tokens": cleaned,
    }
