"""Showcase + all eval cases, rendered at the top of app.py (chat input stays at the bottom).

Tab 1 "Hành trình v0 → v8": one real example per version. Click a card: LEFT runs it
live now, RIGHT shows the old result recorded locally (showcase/recorded.json).
Tab 2 "Tất cả test case": every case in data/eval_base.json and data/eval_group.json,
with the PASS/FAIL each version actually got in runs/*.json; pick a case to see the
recorded tool calls and run it live, graded by the same evaluate_phase_b as run_eval.
`send` never posts: the approval gate (approval.py) and the showcase stub block it.
"""
from __future__ import annotations

import difflib
import json
from pathlib import Path
from typing import Any

import streamlit as st

from showcase.runner import VERSIONS_DIR, available_versions, run_case

ROOT = Path(__file__).resolve().parents[1]
CASES: list[dict[str, Any]] = json.loads((ROOT / "showcase" / "cases.json").read_text(encoding="utf-8"))
REC_PATH = ROOT / "showcase" / "recorded.json"
DATASETS = {"Base (eval_base.json)": ROOT / "data" / "eval_base.json",
            "Group (eval_group.json)": ROOT / "data" / "eval_group.json"}
KIND_ICON = {"prompt": "📝", "tools": "🧰", "code": "💻", "baseline": "⏺"}

CSS = """
<style>
  .block-container {max-width: 1220px; margin: 0 auto; padding-top: 1.5rem;}
  .sc-center {text-align: center;}
  .sc-pill {display:inline-block; padding:2px 10px; border-radius:999px; font-weight:600;
            font-size:0.85rem; margin-right:6px;}
  .sc-badge {background:#eef2ff; color:#3730a3;}
  .sc-kind-prompt {background:#dbeafe; color:#1e40af;}
  .sc-kind-tools {background:#ede9fe; color:#5b21b6;}
  .sc-kind-code {background:#fee2e2; color:#991b1b;}
  .sc-kind-baseline {background:#e5e7eb; color:#374151;}
  .sc-old {background:#fef3c7; color:#92400e;}
  .sc-new {background:#dcfce7; color:#166534;}
</style>
"""


def _recorded() -> dict[str, Any]:
    return json.loads(REC_PATH.read_text(encoding="utf-8")) if REC_PATH.exists() else {}


def _pill(text: str, cls: str) -> str:
    return f"<span class='sc-pill {cls}'>{text}</span>"


def _kind(case: dict[str, Any]) -> str:
    k = case.get("change_kind", "baseline")
    return _pill(f"{KIND_ICON.get(k, '')} {case.get('change_kind_label', k)}", f"sc-kind-{k}")


def _diff(case: dict[str, Any]) -> str | None:
    rel = case.get("changed_file")
    if not rel or case["before"] == case["version"]:
        return None
    name = Path(rel).name
    old = (VERSIONS_DIR / case["before"] / name).read_text(encoding="utf-8").splitlines()
    new = (VERSIONS_DIR / case["version"] / name).read_text(encoding="utf-8").splitlines()
    return "\n".join(difflib.unified_diff(old, new, f"{case['before']}/{name}", f"{case['version']}/{name}", lineterm="", n=1))


def _calls_block(calls: list[dict[str, Any]]) -> None:
    if calls:
        for c in calls:
            st.code(f"{c.get('name')}({json.dumps(c.get('args') or {}, ensure_ascii=False)})", language="python")
    else:
        st.code("(không gọi tool)", language="text")


def _result(res: dict[str, Any] | None) -> None:
    if not res:
        st.info("Chưa có kết quả. Bấm ▶ Chạy lại.")
        return
    st.caption(f"`{res.get('artifact_version')}` · {res.get('model')} · {res.get('status')} · "
               f"{res.get('seconds')}s · {res.get('ran_at')}")
    st.markdown("**Tool calls**")
    _calls_block(res.get("tool_calls") or [])
    for tr in res.get("tool_results") or []:
        r = tr.get("result")
        if isinstance(r, dict) and r.get("error") == "SEND_BLOCKED_NEEDS_CONFIRMATION":
            st.warning("💻 Cổng duyệt (approval.py) đã chặn `send`: chưa có xác nhận thật của user.")
    if res.get("mode") == "plan":
        st.caption("Chế độ plan: chỉ ghi quyết định đầu tiên của model, không chạy tool.")
    if res.get("mode") == "eval":
        st.caption("Chế độ eval: giống run_eval (tool_choice như eval, tool chạy qua agent.py có cổng duyệt).")
    st.markdown("**Agent trả lời**")
    with st.container(height=240, border=True):
        st.markdown(res.get("assistant_text") or "_(không có text — agent dừng ở tool call)_")


# ------------------------------------------------------------------ tab 1: journey
def _journey() -> None:
    st.session_state.setdefault("sc_selected", None)
    st.session_state.setdefault("sc_live", {})
    recorded = _recorded()
    versions = available_versions()

    if st.session_state.sc_selected is None:
        st.markdown("<p class='sc-center'>Mỗi version sửa thêm một vấn đề. Bấm một thẻ: <b>trái</b> chạy lại "
                    "ngay bây giờ, <b>phải</b> là kết quả cũ đã ghi khi chạy local. Loại thay đổi: "
                    + _pill("📝 System prompt", "sc-kind-prompt") + _pill("🧰 Tool — tools.yaml", "sc-kind-tools")
                    + _pill("💻 Code", "sc-kind-code") + "</p>", unsafe_allow_html=True)
        for i, case in enumerate(CASES):
            if i % 3 == 0:
                cols = st.columns(3, gap="medium")
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(_pill(case["version"], "sc-badge") + _kind(case), unsafe_allow_html=True)
                    st.markdown(f"**{case['title']}**")
                    st.caption(case["problem"])
                    if st.button("▶ Xem & chạy", key=f"open_{case['id']}", use_container_width=True):
                        st.session_state.sc_selected = case["id"]
                        st.session_state.sc_autorun = True
                        st.rerun()
        return

    case = next(c for c in CASES if c["id"] == st.session_state.sc_selected)
    if st.button("⟲ Quay lại danh sách", key="back_top"):
        st.session_state.sc_selected = None
        st.rerun()
    st.markdown(f"<h3 class='sc-center'>{case['title']}</h3>", unsafe_allow_html=True)
    st.markdown("<p class='sc-center'>Loại thay đổi: " + _kind(case)
                + (f" · <code>{case['changed_file']}</code>" if case.get("changed_file") else "") + "</p>",
                unsafe_allow_html=True)
    st.markdown(f"**Vấn đề:** {case['problem']}  \n**Thay đổi:** {case['change']}")
    d = _diff(case)
    if d:
        with st.expander(f"Xem diff {case['before']} → {case['version']} ({case['changed_file']})"):
            st.code(d, language="diff")
    st.markdown("**Prompt của user**" + (" (nhiều lượt)" if isinstance(case["prompt"], list) else ""))
    turns = case["prompt"] if isinstance(case["prompt"], list) else [case["prompt"]]
    st.code("\n".join(f"[{i + 1}] {t}" for i, t in enumerate(turns)), language="text")

    runs = recorded.get(case["id"], {})
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        live_v = st.selectbox("Bên trái chạy version", versions, index=len(versions) - 1, key=f"lv_{case['id']}")
    with c2:
        opts = list(runs) or [case["before"]]
        old_v = st.selectbox("Bên phải: kết quả đã ghi", opts,
                             index=opts.index(case["before"]) if case["before"] in opts else 0, key=f"ov_{case['id']}")
    with c3:
        st.write("")
        run_now = st.button("▶ Chạy lại", type="primary", use_container_width=True, key=f"run_{case['id']}")
    key = f"{case['id']}::{live_v}"
    if run_now or (st.session_state.pop("sc_autorun", False) and key not in st.session_state.sc_live):
        with st.spinner(f"Đang chạy {live_v} ..."):
            st.session_state.sc_live[key] = run_case(live_v, case["prompt"], mode=case["mode"],
                                                     tool_choice=case.get("tool_choice"))
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown(_pill(f"ĐANG CHẠY BÂY GIỜ · {live_v}", "sc-new"), unsafe_allow_html=True)
        _result(st.session_state.sc_live.get(key))
    with right:
        st.markdown(_pill(f"KẾT QUẢ CŨ (đã ghi) · {old_v}", "sc-old"), unsafe_allow_html=True)
        _result(runs.get(old_v))


# ------------------------------------------------------------------ tab 2: all eval cases
@st.cache_data(show_spinner=False)
def _run_index(mtime_key: float) -> dict[str, dict[str, dict[str, Any]]]:
    """dataset_id -> version -> {case_id: result} from the latest valid run of each version."""
    index: dict[str, dict[str, dict[str, Any]]] = {}
    for f in sorted((ROOT / "runs").glob("*_B_*.json")):
        try:
            run = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        s = run.get("summary", {})
        if s.get("provider_error_cases", 1) != 0:
            continue
        ver = run.get("version", "?")
        if run.get("provider") != "openrouter":
            ver = f"{ver} ({run.get('provider')})"
        bucket = index.setdefault(run.get("dataset_id", f.stem), {}).setdefault(ver, {})
        for r in run.get("results", []):
            bucket[r["id"]] = {**r["result"], "_run": f.name}
    return index


def _all_cases() -> None:
    from run_eval import evaluate_phase_b

    name = st.radio("Bộ case", list(DATASETS), horizontal=True, label_visibility="collapsed")
    data = json.loads(DATASETS[name].read_text(encoding="utf-8"))
    cases = data["cases"]
    runs_dir = ROOT / "runs"
    idx = _run_index(max((p.stat().st_mtime for p in runs_dir.glob("*.json")), default=0.0)).get(data.get("dataset_id"), {})
    versions = sorted(idx, key=lambda v: (len(v), v))
    st.caption(f"{len(cases)} case · kết quả lấy từ run thật trong `runs/` (lần chạy mới nhất mỗi version, 0 provider error). "
               "Grader chỉ chấm tool call; ô trống = version đó chưa chạy case này.")
    rows = []
    for c in cases:
        row = {"Case": c["id"], "Lượt": "nhiều" if "turns" in c else "1", "Kiểm tra": c["metadata"]["what_it_tests"][:90]}
        for v in versions:
            r = idx[v].get(c["id"])
            row[v] = "" if r is None else ("✅" if r.get("passed") else "❌")
        rows.append(row)
    st.dataframe(rows, use_container_width=True, hide_index=True, height=min(38 * (len(rows) + 1), 520))

    pick = st.selectbox("Chọn case để xem chi tiết và chạy thử", [c["id"] for c in cases], key=f"pick_{name}")
    case = next(c for c in cases if c["id"] == pick)
    turns = [t["content"] for t in case["turns"]] if "turns" in case else [case["query"]]
    a, b = st.columns([3, 2], gap="large")
    with a:
        st.markdown(f"**{case['id']}** · `{case['failure_type']}`  \n{case['metadata']['what_it_tests']}")
        st.code("\n".join(f"[{i + 1}] {t}" for i, t in enumerate(turns)), language="text")
    with b:
        st.markdown("**Expect**")
        st.json(case["expect"], expanded=True)
    rec_cols = [v for v in versions if pick in idx[v]]
    if rec_cols:
        st.markdown("**Kết quả đã ghi trong run**")
        show = [v for v in ("v0", "v3", "v7", "v8") if v in rec_cols] or rec_cols[-4:]
        cols = st.columns(len(show))
        for i, v in enumerate(show):
            r = idx[v][pick]
            with cols[i]:
                st.markdown(_pill(f"{v} · {'PASS' if r.get('passed') else 'FAIL'}", "sc-new" if r.get("passed") else "sc-old"),
                            unsafe_allow_html=True)
                _calls_block(r.get("actual_tool_calls") or [])
                st.caption(r.get("_run", ""))
    vs = available_versions()
    c1, c2 = st.columns([3, 1])
    with c1:
        live_v = st.selectbox("Chạy thử ngay với version", vs, index=len(vs) - 1, key=f"cv_{name}")
    with c2:
        st.write("")
        go = st.button("▶ Chạy case", type="primary", use_container_width=True, key=f"go_{name}")
    lk = f"case::{pick}::{live_v}"
    if go:
        with st.spinner(f"Đang chạy {pick} trên {live_v} ..."):
            res = run_case(live_v, turns, mode="eval", tool_choice=None if case["expect"].get("no_tool") else "required")
            if res.get("status") != "error":
                res["grade"] = evaluate_phase_b(case, res["tool_calls"], res.get("assistant_text"))
            st.session_state.setdefault("sc_live", {})[lk] = res
    res = st.session_state.get("sc_live", {}).get(lk)
    if res:
        g = res.get("grade")
        if g:
            (st.success if g["passed"] else st.error)(
                f"{'PASS' if g['passed'] else 'FAIL'} · {live_v}" + ("" if g["passed"] else f" · {', '.join(g['failures'])}"))
        _result(res)


def render() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown("<h1 class='sc-center'>🔎 Research Agent · Nhom002</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🧪 Hành trình v0 → v8", "📋 Tất cả test case"])
    with t1:
        _journey()
    with t2:
        _all_cases()
    st.divider()
    st.markdown("<h3 class='sc-center'>💬 Chat với agent</h3>", unsafe_allow_html=True)
    st.caption("Ô chat ở cuối trang dùng version và provider ở thanh bên.")
