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
