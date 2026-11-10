"""Showcase v0 → v7: one real example per version.

List view: one card per version. Click a card to open it: the LEFT column runs
the prompt live now, the RIGHT column shows the old result recorded locally by
`python -m showcase.record` (showcase/recorded.json). "Quay lại danh sách"
returns to the list. `send` is always stubbed here, so nothing is ever posted.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from showcase.runner import available_versions, run_case  # noqa: E402

st.set_page_config(page_title="Showcase v0 → v7", page_icon="🧪", layout="wide")

st.markdown(
    """
    <style>
      .block-container {max-width: 1180px; margin: 0 auto; padding-top: 2rem;}
      .sc-center {text-align: center;}
      .sc-badge {display:inline-block; padding:2px 10px; border-radius:999px;
                 background:#eef2ff; color:#3730a3; font-weight:600; font-size:0.85rem;}
      .sc-old {display:inline-block; padding:2px 10px; border-radius:999px;
               background:#fef3c7; color:#92400e; font-weight:600; font-size:0.85rem;}
      .sc-kind {display:inline-block; padding:2px 10px; border-radius:999px; margin-left:6px;
                font-weight:600; font-size:0.85rem;}
      .sc-kind-prompt {background:#dbeafe; color:#1e40af;}
      .sc-kind-tools {background:#ede9fe; color:#5b21b6;}
      .sc-kind-code {background:#fee2e2; color:#991b1b;}
      .sc-kind-baseline {background:#e5e7eb; color:#374151;}
      .sc-new {display:inline-block; padding:2px 10px; border-radius:999px;
               background:#dcfce7; color:#166534; font-weight:600; font-size:0.85rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

CASES: list[dict[str, Any]] = json.loads((ROOT / "showcase" / "cases.json").read_text(encoding="utf-8"))
REC_PATH = ROOT / "showcase" / "recorded.json"
RECORDED: dict[str, dict[str, Any]] = json.loads(REC_PATH.read_text(encoding="utf-8")) if REC_PATH.exists() else {}
VERSIONS = available_versions()
LATEST = VERSIONS[-1]

st.session_state.setdefault("sc_selected", None)
st.session_state.setdefault("sc_live", {})


def go_list() -> None:
    st.session_state.sc_selected = None


def open_case(case_id: str) -> None:
    st.session_state.sc_selected = case_id
    st.session_state.sc_autorun = True


KIND_ICON = {"prompt": "📝", "tools": "🧰", "code": "💻", "baseline": "⏺"}


def kind_badge(case: dict[str, Any]) -> str:
    k = case.get("change_kind", "baseline")
    return f"<span class='sc-kind sc-kind-{k}'>{KIND_ICON.get(k, '')} {case.get('change_kind_label', k)}</span>"


def version_diff(case: dict[str, Any]) -> str | None:
    import difflib

    rel = case.get("changed_file")
    if not rel or case["before"] == case["version"]:
        return None
    name = Path(rel).name
    old = (ROOT / "artifacts" / "versions" / case["before"] / name).read_text(encoding="utf-8").splitlines()
    new = (ROOT / "artifacts" / "versions" / case["version"] / name).read_text(encoding="utf-8").splitlines()
    return "\n".join(difflib.unified_diff(old, new, f"{case['before']}/{name}", f"{case['version']}/{name}", lineterm="", n=1))


def render_result(res: dict[str, Any] | None) -> None:
    if not res:
        st.info("Chưa có kết quả.")
        return
    st.caption(
        f"`{res.get('artifact_version')}` · {res.get('provider')}/{res.get('model')} · "
        f"{res.get('status')} · {res.get('seconds')}s · {res.get('ran_at')}"
    )
    calls = res.get("tool_calls") or []
    st.markdown("**Tool calls**")
    if calls:
        for c in calls:
            st.code(f"{c.get('name')}({json.dumps(c.get('args') or {}, ensure_ascii=False)})", language="python")
    else:
        st.code("(không gọi tool)", language="text")
    if res.get("mode") == "plan":
        st.caption("Chế độ plan: chỉ ghi quyết định đầu tiên của model, không chạy tool (tránh gọi API số lượng lớn).")
    st.markdown("**Agent trả lời**")
    with st.container(height=320, border=True):
        st.markdown(res.get("assistant_text") or "_(không có text — agent dừng ở tool call)_")


# ------------------------------------------------------------------ list view
if st.session_state.sc_selected is None:
    st.markdown("<h1 class='sc-center'>🧪 Hành trình v0 → v7</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='sc-center'>Mỗi version sửa thêm một vấn đề. Bấm một thẻ để chạy lại ví dụ ngay bây giờ "
        "(trái) và so với kết quả cũ đã ghi khi chạy local (phải).</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='sc-center'>Loại thay đổi: <span class='sc-kind sc-kind-prompt'>📝 System prompt</span>"
        "<span class='sc-kind sc-kind-tools'>🧰 Tool — tools.yaml</span>"
        "<span class='sc-kind sc-kind-code'>💻 Code</span> · v1–v7 chỉ sửa prompt hoặc tools.yaml, "
        "chưa version nào sửa code agent.</p>",
        unsafe_allow_html=True,
    )
    if not RECORDED:
        st.warning("Chưa có showcase/recorded.json — chạy `python -m showcase.record` trong starter_v0/.")
    for i, case in enumerate(CASES):
        if i % 2 == 0:
            cols = st.columns(2, gap="large")
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"<span class='sc-badge'>{case['version']}</span>{kind_badge(case)}", unsafe_allow_html=True)
                st.subheader(case["title"])
                st.markdown(f"**Vấn đề:** {case['problem']}")
                st.markdown(f"**Thay đổi:** {case['change']}")
                st.button("▶ Chạy ví dụ", key=f"open_{case['id']}", on_click=open_case,
                          args=(case["id"],), use_container_width=True)
    st.stop()

# ------------------------------------------------------------------ detail view
case = next(c for c in CASES if c["id"] == st.session_state.sc_selected)
st.button("⟲ Quay lại danh sách", on_click=go_list, key="back_top")
st.markdown(f"<h2 class='sc-center'>{case['title']}</h2>", unsafe_allow_html=True)
st.markdown(f"<p class='sc-center'>Loại thay đổi: {kind_badge(case)}"
            + (f" · file <code>{case['changed_file']}</code>" if case.get('changed_file') else "")
            + "</p>", unsafe_allow_html=True)
st.markdown(f"**Vấn đề:** {case['problem']}  \n**Thay đổi:** {case['change']}")
_diff = version_diff(case)
if _diff:
    with st.expander(f"Xem diff {case['before']} → {case['version']} ({case['changed_file']})"):
        st.code(_diff, language="diff")
st.markdown("**Prompt của user**")
st.code(case["prompt"], language="text")

c1, c2, c3 = st.columns([2, 2, 1])
with c1:
    live_version = st.selectbox("Version chạy bên trái", VERSIONS, index=VERSIONS.index(LATEST), key=f"lv_{case['id']}")
recorded_runs = RECORDED.get(case["id"], {})
with c2:
    old_options = list(recorded_runs) or [case["before"]]
    old_version = st.selectbox("Kết quả cũ bên phải", old_options,
                               index=old_options.index(case["before"]) if case["before"] in old_options else 0,
                               key=f"ov_{case['id']}")
with c3:
    st.write("")
    run_now = st.button("▶ Chạy lại", type="primary", use_container_width=True, key=f"run_{case['id']}")

live_key = f"{case['id']}::{live_version}"
if run_now or (st.session_state.pop("sc_autorun", False) and live_key not in st.session_state.sc_live):
    with st.spinner(f"Đang chạy {live_version} ..."):
        st.session_state.sc_live[live_key] = run_case(live_version, case["prompt"], mode=case["mode"])

left, right = st.columns(2, gap="large")
with left:
    st.markdown(f"<span class='sc-new'>ĐANG CHẠY BÂY GIỜ · {live_version}</span>", unsafe_allow_html=True)
    render_result(st.session_state.sc_live.get(live_key))
with right:
    st.markdown(f"<span class='sc-old'>KẾT QUẢ CŨ (đã ghi) · {old_version}</span>", unsafe_allow_html=True)
    render_result(recorded_runs.get(old_version))

st.divider()
st.button("⟲ Quay lại danh sách", on_click=go_list, key="back_bottom")
