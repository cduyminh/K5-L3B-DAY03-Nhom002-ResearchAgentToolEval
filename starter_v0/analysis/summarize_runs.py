"""Parse runs/*.json into two CSVs (run from starter_v0/):

    python analysis/summarize_runs.py

- analysis/runs_summary.csv: one row per run (version, suite, model, accuracy, validity).
- analysis/case_matrix.csv: one row per (run, case) with pass/fail, failure type and actual tool calls.
Only reads run JSON written by run_eval.py; nothing is re-scored here.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = sorted((ROOT / "runs").glob("*.json"))

summary_rows, case_rows = [], []
for f in RUNS:
    run = json.loads(f.read_text(encoding="utf-8"))
    s = run.get("summary", {})
    valid = s.get("provider_error_cases") == 0 and s.get("measured_cases") == s.get("total_cases")
    summary_rows.append({
        "run_file": f"runs/{f.name}",
        "version": run.get("version"),
        "suite": run.get("suite"),
        "dataset_id": run.get("dataset_id"),
        "provider": run.get("provider"),
        "model": run.get("model"),
        "artifact_version": run.get("artifact_version"),
        "total_cases": s.get("total_cases"),
        "measured_cases": s.get("measured_cases"),
        "provider_error_cases": s.get("provider_error_cases"),
        "passed_cases": s.get("passed_cases"),
        "case_accuracy": s.get("case_accuracy"),
        "tool_routing_accuracy": s.get("tool_routing_accuracy"),
        "argument_accuracy": s.get("argument_accuracy"),
        "multiturn_accuracy": s.get("multiturn_accuracy"),
        "valid_evidence": valid,
    })
    for r in run.get("results", []):
        res = r.get("result", {})
        case_rows.append({
            "run_file": f"runs/{f.name}",
            "version": run.get("version"),
            "model": run.get("model"),
            "case_id": r.get("id"),
            "passed": res.get("passed"),
            "failure_type": res.get("failure_type") or "",
            "observed_mismatch": res.get("observed_mismatch") or "",
            "actual_tool_calls": json.dumps(
                [{"name": c.get("name"), "args": c.get("args")} for c in res.get("actual_tool_calls") or []],
                ensure_ascii=False),
        })

for name, rows in (("runs_summary.csv", summary_rows), ("case_matrix.csv", case_rows)):
    out = ROOT / "analysis" / name
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote analysis/{name}: {len(rows)} rows")
