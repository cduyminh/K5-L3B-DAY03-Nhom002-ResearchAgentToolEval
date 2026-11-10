from __future__ import annotations

import re
from typing import Any


def extract_sentences(text: str = "", limit: int = 3) -> dict[str, Any]:
    if not isinstance(text, str):
        return {"tool": "extract_sentences", "error": "TypeError", "message": "text must be a string"}

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    if not sentences:
        return {"tool": "extract_sentences", "sentences": [], "count": 0}

    take = max(1, int(limit or 3))
    return {
        "tool": "extract_sentences",
        "sentences": sentences[:take],
        "count": min(len(sentences), take),
    }
