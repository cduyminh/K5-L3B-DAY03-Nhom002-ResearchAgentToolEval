from __future__ import annotations

from typing import Any


def claim_evidence_matrix(
    claims: list[str] | None = None,
    evidence: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    if not isinstance(claims, list) or any(not isinstance(claim, str) or not claim.strip() for claim in claims):
        return {
            "tool": "claim_evidence_matrix",
            "error": "ValueError",
            "message": "claims must be a list of non-empty strings",
        }
    if not isinstance(evidence, list):
        return {
            "tool": "claim_evidence_matrix",
            "error": "ValueError",
            "message": "evidence must be a list",
        }

    rows = {claim.strip(): [] for claim in claims}
    for item in evidence:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("claim"), str)
            or not isinstance(item.get("citation"), str)
            or not isinstance(item.get("excerpt", ""), str)
        ):
            return {
                "tool": "claim_evidence_matrix",
                "error": "ValueError",
                "message": "each evidence item needs string claim, citation, and optional excerpt fields",
            }

        claim = item["claim"].strip()
        if claim in rows:
            rows[claim].append({
                "citation": item["citation"].strip(),
                "excerpt": item.get("excerpt", "").strip(),
            })

    matrix = [
        {
            "claim": claim,
            "evidence": claim_evidence,
            "evidence_status": "provided" if claim_evidence else "not_provided",
        }
        for claim, claim_evidence in rows.items()
    ]
    return {
        "tool": "claim_evidence_matrix",
        "matrix": matrix,
        "verification": "not_performed",
        "note": "This tool only organizes user-provided claims and evidence; it does not verify factual accuracy.",
    }