"""Streamlit chat UI for the Research Agent.

Runs the same multi-round tool loop as chat.py and writes transcripts in the
same format to transcripts/<version>_<provider>_<timestamp>.transcript.json.

Run from starter_v0/:
    streamlit run app.py
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version
from showcase.ui import render as render_showcase

PROVIDERS = ["openrouter", "openai", "anthropic", "gemini", "ollama"]
PROVIDER_LABELS = {
    "openrouter": "OpenRouter (cloud, nhiều model)",
    "openai": "OpenAI",
    "anthropic": "Anthropic (Claude)",
    "gemini": "Google Gemini",
    "ollama": "Ollama (model local, miễn phí)",
}
# Suggested models; any other model id can be typed in via "Khác (tự nhập)".
MODEL_OPTIONS = {
    "openrouter": ["openai/gpt-4o-mini", "anthropic/claude-sonnet-5-5", "google/gemini-3.8-flash", "qwen/qwen-2.5-7b-instruct"],
    "openai": ["gpt-4o-mini", "gpt-4o"],
    "anthropic": ["claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"],
    "gemini": ["gemini-3.8-flash"],
    "ollama": [],  # filled from the local Ollama server
}
KEY_ENV = {"openrouter": "OPENROUTER_API_KEY", "openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY", "gemini": "GEMINI_API_KEY"}
OTHER_MODEL = "Khác (tự nhập)…"


def ollama_models() -> tuple[list[str], str | None]:
    """Models installed on the local Ollama server, or an error message."""
    import os

    import requests

    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1").rsplit("/v1", 1)[0]
    try:
        tags = requests.get(f"{base}/api/tags", timeout=2).json().get("models", [])
        return [m["name"] for m in tags], None
    except Exception as exc:  # server not running
        return [], f"Không kết nối được Ollama ({base}): chạy `ollama serve` rồi tải model, ví dụ `ollama pull qwen2.5:7b`. Lỗi: {type(exc).__name__}"
TRANSCRIPTS_DIR = ROOT / "transcripts"

st.set_page_config(page_title="Research Agent · Nhom002", page_icon="🔎", layout="wide")


def latest_logged_version() -> str:
    """Last `version` in artifacts/version_log.csv (e.g. v3), fallback v0."""
    import csv

    try:
        with (ARTIFACTS_DIR / "version_log.csv").open(encoding="utf-8") as fh:
            rows = [r for r in csv.DictReader(fh) if r.get("version")]
        return rows[-1]["version"] if rows else "v0"
    except OSError:
        return "v0"


# ---------------------------------------------------------------- session setup
def new_session(provider_name: str, model: str, version: str, history_window: int, max_tool_rounds: int, api_key: str = "") -> None:
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"

    provider = make_provider(provider_name, api_key=api_key or None)  # key stays in memory for this session only
    selected_model = model or getattr(provider, "default_model", None)
    artifact_version = build_artifact_version(version, system_prompt_path, tools_path)

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), timestamp])

    st.session_state.cfg = {
        "provider": provider_name,
        "model": model or None,
        "version": version,
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
    }
    st.session_state.provider = provider
    st.session_state.system_prompt = system_prompt_path.read_text(encoding="utf-8")
    st.session_state.openai_tools = to_openai_tools(load_tool_declarations(tools_path))
    st.session_state.history = []  # model context (user/assistant pairs), same as chat.py
    st.session_state.turn_index = 0
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": selected_model,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "ui": "streamlit",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }


# ---------------------------------------------------------------- rendering
def render_rounds(rounds: list[dict[str, Any]]) -> None:
    for rnd in rounds:
        calls = rnd.get("tool_calls") or []
        if not calls:
            continue
        for event in rnd.get("tool_results") or []:
            args_txt = json.dumps(event.get("args", {}), ensure_ascii=False, sort_keys=True)
            result = event.get("result", {})
            is_error = isinstance(result, dict) and "error" in result
            icon = "⚠️" if is_error else "🔧"
            with st.expander(f"{icon} Round {rnd['round']}: `{event.get('tool')}({args_txt})`", expanded=False):
                st.markdown("**Args**")
                st.json(event.get("args", {}))
                st.markdown("**Result**")
                st.json(result)
        if rnd.get("assistant_text"):
            st.caption(f"Assistant note (round {rnd['round']}): {rnd['assistant_text']}")


def render_turn(turn: dict[str, Any]) -> None:
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant"):
        render_rounds(turn.get("rounds", []))
        status = turn.get("status")
        if status == "provider_error":
            st.error(turn.get("error"))
            return
        if status == "waiting_for_user":
            st.info("❓ Agent đang chờ bạn trả lời (clarify)")
        elif status == "max_tool_rounds":
            st.warning("Đã chạm giới hạn max_tool_rounds")
        st.markdown(turn.get("assistant_text") or "_(không có text)_")


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("⚙️ Cấu hình")
    provider_name = st.selectbox("Provider", PROVIDERS, index=0, format_func=lambda p: PROVIDER_LABELS.get(p, p))
    options = list(MODEL_OPTIONS.get(provider_name, []))
    if provider_name == "ollama":
        options, ollama_err = ollama_models()
        if ollama_err:
            st.warning(ollama_err)
        elif not options:
            st.warning("Ollama đang chạy nhưng chưa có model nào: `ollama pull qwen2.5:7b`.")
    picked = st.selectbox("Model", options + [OTHER_MODEL], index=0, key=f"model_{provider_name}")
    model = st.text_input("Model id", value="", placeholder="vd openai/gpt-4o hoặc llama3.1:8b") if picked == OTHER_MODEL else picked
    api_key = ""
    if provider_name != "ollama":
        api_key = st.text_input(
            f"API key (để trống = dùng {KEY_ENV[provider_name]} trong .env)",
            value="", type="password", key=f"key_{provider_name}",
            help="Key chỉ giữ trong bộ nhớ của phiên này, không ghi vào transcript, file hay biến môi trường.",
        )
    else:
        st.caption("Model local chạy trên máy này, không cần API key.")
    version = st.text_input("Version label", value=latest_logged_version())
    history_window = st.number_input("History window (cặp user/assistant)", 0, 50, 5)
    max_tool_rounds = st.number_input("Max tool rounds", 1, 20, 4)
    start = st.button("🆕 New chat (xóa hội thoại)", use_container_width=True)
    st.caption("Đổi provider / model / key / version là áp dụng ngay (bắt đầu chat mới).")

# Apply sidebar changes right away: any change of provider/model/key/version/limits starts a new session.
import hashlib

_config_sig = (
    provider_name, (model or "").strip(), version.strip() or "v0", int(history_window), int(max_tool_rounds),
    hashlib.sha256(api_key.strip().encode()).hexdigest()[:12],  # only a hash of the key is kept for comparison
)
_changed = "transcript" in st.session_state and st.session_state.get("config_sig") != _config_sig
if start or _changed or "transcript" not in st.session_state:
    try:
        new_session(provider_name, (model or "").strip(), version.strip() or "v0", int(history_window), int(max_tool_rounds), api_key.strip())
        st.session_state.config_sig = _config_sig
        if _changed and not start:
            st.toast(f"Đã áp dụng: {PROVIDER_LABELS.get(provider_name, provider_name)} · {(model or 'model mặc định')} — bắt đầu chat mới")
    except Exception as exc:
        st.error(f"Không khởi tạo được provider: {type(exc).__name__}: {exc}")
        st.stop()

cfg = st.session_state.cfg
transcript = st.session_state.transcript

with st.sidebar:
    st.divider()
    st.markdown(f"**Đang dùng:** `{cfg['provider']}` / `{transcript['model']}`")
    st.markdown(f"**artifact_version:** `{transcript['artifact_version']}`")
    st.markdown(f"**Transcript:** `{st.session_state.transcript_path.relative_to(ROOT)}`")
    if transcript["turns"]:
        st.download_button(
            "⬇️ Tải transcript JSON",
            data=json.dumps(transcript, ensure_ascii=False, indent=2, default=str),
            file_name=st.session_state.transcript_path.name,
            mime="application/json",
            use_container_width=True,
        )

# Test cases front and center; the chat history and st.chat_input stay below (input pinned at the bottom).
render_showcase()

for past_turn in transcript["turns"]:
    render_turn(past_turn)

# ---------------------------------------------------------------- new turn
user_text = st.chat_input("Nhập câu hỏi...")
if user_text and user_text.strip():
    user_text = user_text.strip()
    st.session_state.turn_index += 1
    messages = [
        {"role": "system", "content": st.session_state.system_prompt},
        *trim_history(st.session_state.history, cfg["history_window"]),
        {"role": "user", "content": user_text},
    ]
    turn_record: dict[str, Any] = {
        "turn_index": st.session_state.turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    with st.chat_message("user"):
        st.markdown(user_text)

    with st.spinner("Agent đang xử lý..."):
        try:
            result = run_model_tool_loop(
                provider=st.session_state.provider,
                messages=messages,
                tools=st.session_state.openai_tools,
                model=cfg["model"],
                max_tool_rounds=cfg["max_tool_rounds"],
            )
            turn_record.update(result)
            st.session_state.history.append({"role": "user", "content": user_text})
            st.session_state.history.append({"role": "assistant", "content": result["assistant_text"]})
        except Exception as exc:
            turn_record.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"})

    turn_record["ended_at"] = now_iso()
    transcript["turns"].append(turn_record)
    write_transcript(st.session_state.transcript_path, transcript)
    st.rerun()
