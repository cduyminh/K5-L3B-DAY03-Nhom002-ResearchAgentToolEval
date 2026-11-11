"""Unit tests for the custom tools added to this project."""
from __future__ import annotations

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS


# ---------------- Custom tools ----------------

hn_search_tool = TOOL_FUNCTIONS["hn_search"]


def test_hn_search_happy_path(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "hits": [
            {
                "title": "AI startup raises funds",
                "url": "https://news.ycombinator.com/item?id=123",
                "story_text": "example summary",
                "points": 42,
                "author": "alice",
            }
        ]
    }))

    result = hn_search_tool(query="ai", limit=1)

    assert calls[0]["url"].startswith("https://hn.algolia.com/api/v1/search")
    assert calls[0]["params"]["query"] == "ai"
    assert calls[0]["params"]["tags"] == "story"
    assert calls[0]["params"]["hitsPerPage"] == 1
    assert result["items"][0]["title"] == "AI startup raises funds"
    assert result["items"][0]["source"] == "news.ycombinator.com"


def test_hn_search_bad_input_from_model() -> None:
    result = hn_search_tool(query="   ")

    assert result["error"] == "ValueError"
    assert "query" in result["message"].lower()


def test_hn_search_failure_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=500))

    result = hn_search_tool(query="ai")

    assert result["error"] == "HTTPError"
    assert result["tool"] == "hn_search"


summarize_text_tool = TOOL_FUNCTIONS["summarize_text"]


def test_summarize_text_happy_path() -> None:
    text = "AI is changing the world. It affects work and education. Teams are adapting quickly."

    result = summarize_text_tool(text=text, max_sentences=2)

    assert result["tool"] == "summarize_text"
    assert result["sentence_count"] == 2
    assert result["summary"].count(".") >= 1
    assert "AI is changing the world." in result["summary"]


def test_summarize_text_empty_input_returns_empty_summary() -> None:
    result = summarize_text_tool(text="   ", max_sentences=3)

    assert result["tool"] == "summarize_text"
    assert result["summary"] == ""
    assert result["sentence_count"] == 0


def test_summarize_text_wrong_type_returns_error_dict() -> None:
    result = summarize_text_tool(text=None, max_sentences=3)

    assert result["error"] == "TypeError"
    assert result["tool"] == "summarize_text"
    assert "string" in result["message"].lower()


extract_sentences_tool = TOOL_FUNCTIONS["extract_sentences"]


def test_extract_sentences_happy_path() -> None:
    text = "First sentence is important. Second sentence adds context. Third sentence wraps up."

    result = extract_sentences_tool(text=text, limit=2)

    assert result["tool"] == "extract_sentences"
    assert result["count"] == 2
    assert result["sentences"][0] == "First sentence is important."
    assert result["sentences"][1] == "Second sentence adds context."


def test_extract_sentences_empty_text_returns_empty_list() -> None:
    result = extract_sentences_tool(text="", limit=5)

    assert result["tool"] == "extract_sentences"
    assert result["sentences"] == []
    assert result["count"] == 0


def test_extract_sentences_bad_limit_uses_safe_default() -> None:
    text = "One. Two. Three. Four."

    result = extract_sentences_tool(text=text, limit=0)

    assert result["tool"] == "extract_sentences"
    assert result["count"] == 3
    assert len(result["sentences"]) == 3


claim_evidence_matrix_tool = TOOL_FUNCTIONS["claim_evidence_matrix"]


def test_claim_evidence_matrix_groups_provided_evidence_by_claim() -> None:
    claim = "The study found improved retention."
    result = claim_evidence_matrix_tool(
        claims=[claim, "The intervention reduced cost."],
        evidence=[
            {"claim": claim, "citation": "Lee et al. (2024)", "excerpt": "Retention increased by 12%."},
            {"claim": claim, "citation": "Dataset A, table 2", "excerpt": "Follow-up results confirm the increase."},
        ],
    )

    assert result["matrix"][0]["claim"] == claim
    assert len(result["matrix"][0]["evidence"]) == 2
    assert result["matrix"][0]["evidence_status"] == "provided"
    assert result["matrix"][1]["evidence_status"] == "not_provided"
    assert result["verification"] == "not_performed"


def test_claim_evidence_matrix_invalid_input_returns_error_dict() -> None:
    result = claim_evidence_matrix_tool(
        claims="not a list",
        evidence=[],
    )

    assert result["tool"] == "claim_evidence_matrix"
    assert result["error"] == "ValueError"
    assert "claims" in result["message"]


def test_claim_evidence_matrix_malformed_evidence_returns_error_dict() -> None:
    result = claim_evidence_matrix_tool(
        claims=["A claim"],
        evidence=[{"claim": "A claim", "excerpt": "No citation was supplied."}],
    )

    assert result["tool"] == "claim_evidence_matrix"
    assert result["error"] == "ValueError"
    assert "citation" in result["message"]


def test_send_confirmed_posts_once_and_returns_telegram_receipt(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:fake")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100")
    calls = fake_http(FakeResponse({"ok": True, "result": {"message_id": 7, "date": 1794365040,
                                                            "chat": {"id": -100, "title": "Nhom002 Bản tin", "type": "group"}}}))
    result = TOOL_FUNCTIONS["send"](text="Bản tin", confirmed=True)
    assert len(calls) == 1 and calls[0]["url"].endswith("/sendMessage")
    assert calls[0]["json"]["chat_id"] == "-100" and calls[0]["json"]["text"] == "Bản tin"
    assert result["status"] == "sent"
    assert result["telegram_receipt"] == {"message_id": 7, "date_unix": 1794365040,
                                          "chat_title": "Nhom002 Bản tin", "chat_type": "group"}


# ---------------- user_search (v10) ----------------

user_search_tool = TOOL_FUNCTIONS["user_search"]

PEOPLE_PAYLOAD = {"status": "ok", "timeline": [
    {"type": "user", "screen_name": "MinhKhoaTrn1", "name": "Minh Khoa Trần", "followers_count": 312,
     "description": "x" * 300, "is_blue_verified": False, "verified_type": None},
    {"type": "user", "screen_name": "Mingkhwan559", "name": "Trần Minh Khoa", "followers_count": 126,
     "description": "", "is_blue_verified": True},
    {"type": "tweet", "tweet_id": "1", "text": "not a user"},
]}


def test_user_search_sends_people_search_and_maps_candidates(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    calls = fake_http(FakeResponse(PEOPLE_PAYLOAD))

    result = user_search_tool(name="  Trần Minh Khoa ", limit=5)

    assert len(calls) == 1 and calls[0]["url"].endswith("/search.php")
    assert calls[0]["params"] == {"query": "Trần Minh Khoa", "search_type": "People"}
    assert calls[0]["headers"]["x-rapidapi-key"] == "test-key"
    assert result["count"] == 2  # the tweet entry is skipped
    first = result["candidates"][0]
    assert first["screen_name"] == "MinhKhoaTrn1" and first["profile_url"] == "https://x.com/MinhKhoaTrn1"
    assert len(first["description"]) == 160  # long bios are truncated
    assert result["candidates"][1]["verified"] is True


def test_user_search_bad_name_from_model_returns_error_without_calling_api(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    calls = fake_http(FakeResponse(PEOPLE_PAYLOAD))

    for bad in ("   ", None, 123, "a" * 101):
        result = user_search_tool(name=bad)
        assert result["tool"] == "user_search" and result["error"] == "ValueError"
    assert calls == []


def test_user_search_limit_from_model_is_clamped(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    fake_http(FakeResponse(PEOPLE_PAYLOAD))

    assert user_search_tool(name="Khoa", limit=1)["count"] == 1
    assert user_search_tool(name="Khoa", limit=500)["count"] == 2  # capped at 5, only 2 users in payload
    assert user_search_tool(name="Khoa", limit="abc")["count"] == 2  # bad type -> default 5, no exception


def test_user_search_missing_key_returns_error_dict(fake_http) -> None:
    calls = fake_http(FakeResponse(PEOPLE_PAYLOAD))

    result = user_search_tool(name="Trần Minh Khoa")

    assert result == {"tool": "user_search", "error": "RuntimeError", "message": "Missing RAPIDAPI_KEY env var"}
    assert calls == []


def test_user_search_http_429_returns_error_dict(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    fake_http(FakeResponse(status_code=429))

    result = user_search_tool(name="Trần Minh Khoa")

    assert result["tool"] == "user_search" and result["error"] == "HTTPError"


# ---------------- Regression tests: bugs found in the team's tools (v10 audit) ----------------

def test_summarize_text_non_numeric_max_sentences_does_not_raise() -> None:
    # Bug: int("abc") raised ValueError out of the tool instead of returning a result/error dict.
    result = summarize_text_tool(text="One. Two. Three. Four.", max_sentences="abc")
    assert result["tool"] == "summarize_text" and result["sentence_count"] == 3  # falls back to default 3


def test_extract_sentences_non_numeric_limit_does_not_raise() -> None:
    result = extract_sentences_tool(text="One. Two. Three. Four.", limit="abc")
    assert result["tool"] == "extract_sentences" and result["count"] == 3


def test_extract_sentences_wrong_type_returns_error_dict() -> None:
    result = extract_sentences_tool(text=None, limit=2)
    assert result == {"tool": "extract_sentences", "error": "TypeError", "message": "text must be a string"}


def test_hn_search_huge_limit_is_capped_at_20(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))
    result = hn_search_tool(query="ai agents", limit=500)
    assert calls[0]["params"]["hitsPerPage"] == 20 and result["limit"] == 20
