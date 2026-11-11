"""Record the 'old result' shown on the right of the showcase page.

For every case in cases.json, runs the prompt on the case's `before` version
(and on the fix version + latest for reference) and saves showcase/recorded.json.
Run from starter_v0/:  .venv/bin/python -m showcase.record
"""
from __future__ import annotations

import json
from pathlib import Path

from env_loader import load_lab_env
from showcase.runner import available_versions, run_case

HERE = Path(__file__).resolve().parent


def main() -> None:
    """Optional args: case ids to (re)record; others in recorded.json are kept."""
    import sys

    load_lab_env(HERE.parent)
    cases = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
    only = set(sys.argv[1:])
    latest = available_versions()[-1]
    out_path = HERE / "recorded.json"
    recorded: dict[str, dict] = json.loads(out_path.read_text(encoding="utf-8")) if only and out_path.exists() else {}
    for case in cases:
        if only and case["id"] not in only:
            continue
        runs = {}
        for v in dict.fromkeys([case["before"], case["version"], latest]):
            print(f"{case['id']}: running {v} ...", flush=True)
            runs[v] = run_case(v, case["prompt"], mode=case["mode"], tool_choice=case.get("tool_choice"))
            r = runs[v]
            print(f"   tools={[(c['name'], c['args']) for c in r['tool_calls']]}")
            print(f"   text={(r['assistant_text'] or '')[:160]!r}")
        bad = [v for v, r in runs.items() if r.get("status") == "error"]
        if bad:
            print(f"   NOT saved: provider/runtime error on {bad}; keeping the previous recording for {case['id']}")
            continue
        recorded[case["id"]] = runs
    out_path.write_text(json.dumps(recorded, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("saved showcase/recorded.json")


if __name__ == "__main__":
    main()
