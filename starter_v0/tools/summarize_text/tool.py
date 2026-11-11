from __future__ import annotations

import re
from typing import Any


def _as_int(value, default: int) -> int:
    """Model input may be a non-numeric string; fall back instead of raising."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def summarize_text(text: str = "", max_sentences: int = 3) -> dict[str, Any]:
    if not isinstance(text, str):
        return {"tool": "summarize_text", "error": "TypeError", "message": "text must be a string"}

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    if not sentences:
        return {"tool": "summarize_text", "summary": "", "sentence_count": 0}

    limit = max(1, _as_int(max_sentences or 3, 3))
    selected = sentences[:limit]
    return {
        "tool": "summarize_text",
        "summary": " ".join(selected),
        "sentence_count": len(selected),
    }
