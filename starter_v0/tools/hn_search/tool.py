from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err


def hn_search(query: str = "", limit: int = 5) -> dict[str, Any]:
    try:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query is required")

        try:
            hits_per_page = int(limit or 5)
        except (TypeError, ValueError):
            hits_per_page = 5
        hits_per_page = max(1, min(20, hits_per_page))  # same cap as timeline/social_search (v5)

        response = requests.get(
            "https://hn.algolia.com/api/v1/search",
            params={
                "query": query.strip(),
                "tags": "story",
                "hitsPerPage": hits_per_page,
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json() or {}
        hits = data.get("hits", [])

        items: list[dict[str, Any]] = []
        for hit in hits:
            url = hit.get("url") or hit.get("story_url") or ""
            title = hit.get("title") or hit.get("story_title") or (url or "Hacker News story")
            summary = hit.get("story_text") or hit.get("comment_text") or ""
            items.append({
                "title": title,
                "url": url,
                "source": domain(url),
                "summary": summary,
                "score": hit.get("points"),
            })

        return {"tool": "hn_search", "query": query.strip(), "limit": hits_per_page, "items": items}
    except Exception as exc:
        return err("hn_search", exc)
