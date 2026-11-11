from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


def send_telegram(text: str = "", confirmed: bool = False) -> dict[str, Any]:
    if not confirmed:
        return {
            "tool": "send_telegram",
            "status": "needs_confirmation",
            "message": "Only send after the user explicitly confirms.",
        }
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not token or not chat_id:
            raise RuntimeError("Missing TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID env var")
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        out: dict[str, Any] = {"tool": "send_telegram", "status": "sent"}
        # Telegram's own receipt, so a reviewer can verify the post without seeing the private group.
        try:
            msg = (response.json() or {}).get("result") or {}
            chat = msg.get("chat") or {}
            out["telegram_receipt"] = {
                "message_id": msg.get("message_id"),
                "date_unix": msg.get("date"),
                "chat_title": chat.get("title"),
                "chat_type": chat.get("type"),
            }
        except Exception:  # receipt is optional; the post already succeeded
            pass
        return out
    except Exception as exc:
        return err("send_telegram", exc)

