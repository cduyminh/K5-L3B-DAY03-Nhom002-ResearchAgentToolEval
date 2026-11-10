from __future__ import annotations

import os
from typing import Any

from providers.base import ModelResponse, ToolCall

DEFAULT_MODEL = "claude-opus-5-5"

# Current Claude models (Opus 5.5, Sonnet 5.5, Fable 5.1, ...) reject sampling params
# (temperature/top_p/top_k) and forced tool use (tool_choice "any"/"tool") with a 400.
# Only these older models still accept forced tool use.
_FORCED_TOOL_CHOICE_MODELS = ("claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-6")


def _to_anthropic_tools(tools: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    converted: list[dict[str, Any]] = []
    for item in tools or []:
        function = item.get("function", item)
        converted.append({
            "name": function["name"],
            "description": function.get("description", ""),
            "input_schema": function.get("parameters", {"type": "object", "properties": {}}),
        })
    return converted


def _split_system(messages: list[dict[str, str]]) -> tuple[str | None, list[dict[str, str]]]:
    system_parts: list[str] = []
    chat_messages: list[dict[str, str]] = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "system":
            system_parts.append(content)
        elif role in {"user", "assistant"}:
            chat_messages.append({"role": role, "content": content})
    return ("\n\n".join(system_parts) if system_parts else None), chat_messages


class AnthropicProvider:
    """Anthropic Messages provider with normalized tool_calls output."""

    def __init__(
        self,
        *,
        api_key_env: str = "ANTHROPIC_API_KEY",
        default_model: str | None = None,
    ) -> None:
        self.api_key_env = api_key_env
        self.default_model = default_model or os.getenv("ANTHROPIC_MODEL") or DEFAULT_MODEL

    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,  # kept for the Provider interface; not sent (current models reject it)
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise RuntimeError("Install live provider dependency first: pip install anthropic") from exc

        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key env var: {self.api_key_env}")

        selected_model = model or self.default_model
        system, chat_messages = _split_system(messages)
        kwargs: dict[str, Any] = {
            "model": selected_model,
            "messages": chat_messages,
            "max_tokens": 16000,  # room for adaptive thinking + tool call
        }
        if system:
            kwargs["system"] = system
        anthropic_tools = _to_anthropic_tools(tools)
        if anthropic_tools:
            kwargs["tools"] = anthropic_tools
            if tool_choice == "required" and selected_model.startswith(_FORCED_TOOL_CHOICE_MODELS):
                kwargs["tool_choice"] = {"type": "any"}
            # Newer models: leave tool_choice as auto; the system prompt must steer tool use.

        client = Anthropic(api_key=api_key)
        if selected_model.startswith(_FORCED_TOOL_CHOICE_MODELS):
            resp = client.messages.create(**kwargs)
        else:
            # Server-side fallback: if a safety classifier refuses, the API retries on a
            # suitable model instead of returning stop_reason="refusal".
            resp = client.beta.messages.create(
                **kwargs,
                output_config={"effort": "medium"},
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            )

        text_parts: list[str] = []
        calls: list[ToolCall] = []
        if getattr(resp, "stop_reason", None) == "refusal":
            return ModelResponse(text="[refusal] The model declined this request.", tool_calls=[], raw=resp)
        for block in resp.content:
            block_type = getattr(block, "type", None)
            if block_type == "text":
                text_parts.append(getattr(block, "text", ""))
            elif block_type == "tool_use":
                calls.append(ToolCall(name=getattr(block, "name"), args=dict(getattr(block, "input", {}) or {})))
        return ModelResponse(text="\n".join(part for part in text_parts if part) or None, tool_calls=calls, raw=resp)
