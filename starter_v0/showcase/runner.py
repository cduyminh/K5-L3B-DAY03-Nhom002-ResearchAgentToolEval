"""Run one showcase prompt against a snapshot of artifacts/versions/<version>/.

Safety: `send` is always stubbed (never posts). mode="plan" asks the model for
its first decision only (tool calls + text) and does not execute any tool, for
cases whose old behaviour would hammer an API (500 tweets, 100 papers).
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import chat
from chat import run_model_tool_loop
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version

ROOT = Path(__file__).resolve().parents[1]
VERSIONS_DIR = ROOT / "artifacts" / "versions"


def available_versions() -> list[str]:
    return sorted(p.name for p in VERSIONS_DIR.iterdir() if (p / "system_prompt.md").exists())


def _safe_execute(call):
    if call.name == "send":
        return {"tool": "send", "args": call.args,
                "result": {"status": "demo_stub", "message": "Showcase: send bị chặn, không gửi thật."}}
    return _ORIGINAL_EXECUTE(call)


_ORIGINAL_EXECUTE = chat.execute_tool_call


def run_case(version: str, prompt: str, *, mode: str = "full", provider_name: str = "openrouter",
             model: str | None = None, max_tool_rounds: int = 3) -> dict[str, Any]:
    vdir = VERSIONS_DIR / version
    sp, tp = vdir / "system_prompt.md", vdir / "tools.yaml"
    provider = make_provider(provider_name)
    tools = to_openai_tools(load_tool_declarations(tp))
    messages = [{"role": "system", "content": sp.read_text(encoding="utf-8")},
                {"role": "user", "content": prompt}]
    started = time.time()
    out: dict[str, Any] = {
        "version": version,
        "artifact_version": build_artifact_version(version, sp, tp).artifact_version,
        "provider": provider_name,
        "model": model or getattr(provider, "default_model", None),
        "mode": mode,
    }
    try:
        if mode == "plan":
            resp = provider.complete(messages, tools, model=model, temperature=0.0)
            out.update(status="plan_only", assistant_text=resp.text or "",
                       tool_calls=[{"name": c.name, "args": c.args} for c in resp.tool_calls])
        else:
            chat.execute_tool_call = _safe_execute
            try:
                res = run_model_tool_loop(provider=provider, messages=messages, tools=tools,
                                          model=model, max_tool_rounds=max_tool_rounds)
            finally:
                chat.execute_tool_call = _ORIGINAL_EXECUTE
            out.update(status=res["status"], assistant_text=res["assistant_text"],
                       tool_calls=[{"name": e.get("tool"), "args": e.get("args")} for e in res["tool_events"]])
    except Exception as exc:  # show the error instead of crashing the page
        out.update(status="error", assistant_text=f"{type(exc).__name__}: {exc}", tool_calls=[])
    out["seconds"] = round(time.time() - started, 1)
    out["ran_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    return out
