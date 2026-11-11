from __future__ import annotations

from typing import Any

from tools._shared import err
from tools.timeline.tool import _twitter_get

MAX_CANDIDATES = 5


def _as_limit(limit: Any) -> int:
    """Model input may be a string, 0, negative or huge: fall back to 5, clamp to 1..5."""
    try:
        value = int(limit)
    except (TypeError, ValueError):
        return MAX_CANDIDATES
    return max(1, min(MAX_CANDIDATES, value))


def search_users(name: str = "", limit: int = MAX_CANDIDATES) -> dict[str, Any]:
    """Find X/Twitter accounts matching a person's name (People search).

    Returns candidate handles for the user to choose from; it never picks one.
    Only public profile fields are returned.
    """
    try:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name is required (the person's name as the user wrote it)")
        if len(name.strip()) > 100:
            raise ValueError("name is too long (max 100 characters)")
        take = _as_limit(limit)
        data = _twitter_get("/search.php", {"query": name.strip(), "search_type": "People"})
        candidates: list[dict[str, Any]] = []
        for raw in data.get("timeline") or []:
            if raw.get("type") not in (None, "user") or not raw.get("screen_name"):
                continue
            candidates.append({
                "screen_name": raw["screen_name"],
                "name": raw.get("name") or "",
                "followers_count": raw.get("followers_count"),
                "description": (raw.get("description") or "")[:160],
                "verified": bool(raw.get("is_blue_verified") or raw.get("verified_type")),
                "profile_url": f"https://x.com/{raw['screen_name']}",
            })
            if len(candidates) >= take:
                break
        return {"tool": "user_search", "query": name.strip(), "count": len(candidates), "candidates": candidates}
    except Exception as exc:
        return err("user_search", exc)
