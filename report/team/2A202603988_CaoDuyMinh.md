# Báo cáo cá nhân — CaoDuyMinh-2A202603988

## 1. Thông tin thành viên

- Họ tên: Cao Duy Minh
- MSSV: 2A202603988
- Email: cduyminh@gmail.com
- Vai trò: nhóm trưởng Nhom002

## 2. Phần việc phụ trách

- Tổ chức nhóm: fork và đặt tên repo `K5-L3B-DAY03-Nhom002-ResearchAgentToolEval`, chia việc theo checkpoint trong `TEAM.md`, gom bài.
- **CP1:** chạy baseline v0, ghi `version_log.csv`, phân tích lỗi v0 (bảng B2).
- **CP2:** vòng tối ưu v1–v3 trên `system_prompt.md` và `tools.yaml` (bảng B1).
- Sau showdown: v4–v8 (guardrail), bộ eval adversarial, showcase trong UI, bonus Telegram và local model; phần 3, B3b, B5/B5b, B6 của báo cáo nhóm.

## 3. Đóng góp cụ thể

**Baseline và v1–v3 (base suite 20 case, OpenRouter `openai/gpt-4o-mini`)**

| Version | File | Giả thuyết | Trước → sau |
|---|---|---|---|
| v0 | — | Đo starter chưa sửa: 5 case FAIL (R08 ngoài phạm vi + `send`, R10/R11 đoán tài khoản/URL, R12 gửi không hỏi, R13 thiếu `topic=news`) | 0.75 |
| v1 | `system_prompt.md` | Bỏ chỉ dẫn "đoán account/URL"; thiếu thì `clarify` | 0.75 → 0.80 |
| v2 | `system_prompt.md` | Bỏ "send… just go ahead"; `clarify(yes_no)` rồi mới `send(confirmed=true)` | 0.80 → 0.90 |
| v3 | `tools.yaml` | Description mỗi tool nói khi nào dùng/không dùng + quy ước args | 0.90 → 1.00 |

**v4–v8: lỗi base suite không đo được, tìm ra khi test site và probe tấn công**

| Version | Loại thay đổi | Lỗi được sửa | Bằng chứng |
|---|---|---|---|
| v4 | System prompt (khung slide e403: Persona → Rules → Capabilities → Constraints → Output → Escalation) | Giải toán, viết code, lộ prompt, prompt injection | `analysis/adversarial/v3_*` vs `v4_*` (4/4 probe bị từ chối) |
| v5 | `tools.yaml` | "500 tweet" → `limit=500` | probe `v4`→`v5`: limit 500 → 20 |
| v6 | `tools.yaml` | Tool không có ranh giới: `fetch` URL nội bộ (169.254.169.254), `papers` không cap | `analysis/adversarial_tools/`, showcase v6 |
| v7 | System prompt | Base64 chứa lệnh injection bị giải mã và in ra | `analysis/adversarial_b64/v6_*` vs `v7_*` |
| v8 | System prompt + **code** `approval.py` | Tự xưng admin "đã xác nhận sẵn" → `send(confirmed=true)` không hỏi | A15: v7 send 4/6, v8 hỏi lại 6/6; `tests/test_approval.py` |

**Eval và UI**
- Thêm 15 case adversarial A01–A15 vào `eval_group.json` (giữ nguyên G01–G10 của Ly), so sánh v3 7/15 → v7 13/15; thêm G11–G13 để 3 tool mới của Dũng đều có case route tới. v8 trên 28 case: 27/28.
- Phát hiện grader chỉ chấm tool call (case `no_tool` vẫn PASS khi model trả lời ngoài phạm vi bằng text) và ghi vào B6.
- Showcase ở đầu UI Streamlit: thẻ v0 → v8 (chạy lại bên trái, kết quả cũ đã ghi bên phải, loại thay đổi, diff) và tab "Tất cả test case" (48 case, PASS/FAIL thật từ `runs/`); ô chat vẫn ở cuối.

**Bonus**
- Telegram: bot @nhom002_research_bot gửi vào private group "Nhom002 Bản tin" sau `clarify(yes_no)` → "Có, gửi đi" → `send(confirmed=true)` → `status: sent` + biên nhận `message_id=4` (B5b).
- Small local model qua Ollama (B7).
- `send` trả biên nhận Telegram (`message_id`, `date`, `chat.title`) + test mock HTTP.

## 4. Bằng chứng

- **Commit:** `47017d3` (v0), `9babd3c` (v1), `f319c78` (v2), `e6dd5e7` (v3), `79487a8` (v4), `3bb667c` (v5), `3eb2b28` (v6), `85175f4` (v7), `cea41ce` (v8 + `approval.py`), `fb2d06b` (A01–A15), `76c39e8` (kiểm tra lại A15), `8c963a2` / `9d31a8c` (showcase), `4701740` (Telegram). Toàn bộ: `git log --author=cduyminh`.
- **Run:** `starter_v0/runs/v{0..8}_B_base_openrouter_*.json`; group `v3_B_group_openrouter_20261111T090925810511.json`, `v7_B_group_openrouter_20261111T090751203463.json`, `v8_B_group_openrouter_20261111T092614630924.json`. Tất cả `provider_error_cases = 0` (`starter_v0/analysis/runs_summary.csv`).
- **Version log:** `starter_v0/artifacts/version_log.csv` (v0–v8, hash prompt/tools, giả thuyết, metric trước/sau).
- **Transcript:** `starter_v0/transcripts/v8_openrouter_20261111T094807333570.transcript.json` (Telegram); `starter_v0/analysis/adversarial*/` (probe trước/sau).
- **Test:** `cd starter_v0 && pytest -q` → 102 passed, 0 skipped.
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Dùng Claude Code (Claude Opus) để đọc slide/lab, viết và sửa prompt, `tools.yaml`, code (`approval.py`, showcase, script phân tích), chạy eval/probe và soạn bảng báo cáo.
  - Cách tự kiểm tra: mọi con số trong báo cáo lấy từ run JSON thật do `run_eval.py` ghi (`provider_error_cases = 0`, `measured_cases = total_cases`); mỗi version chạy lại base suite; ví dụ trong showcase được chạy thật trên máy trước khi đưa vào và đổi ví dụ khi không tái hiện được (v2, v3, v6 ban đầu); khi kết quả lần sau khác lần trước (A15 v7: 3/3 rồi 1/3), báo cáo ghi tổng 4/6 chứ không chọn lần đẹp; `pytest` xanh sau mỗi thay đổi code; quét repo không có key/token trước khi push.

## 5. Tự đánh giá

> Phần này tự viết (RULES: không dùng AI cho phần tự đánh giá). Gợi ý trả lời:
> - Điều mình hiểu rõ nhất sau lab (ví dụ: vì sao cổng xác nhận phải nằm ở code chứ không chỉ ở prompt)?
> - Quyết định nào mình tự đưa ra và vì sao (một giả thuyết mỗi version, giữ 10 case của Ly và thêm case adversarial…)?
> - Chỗ nào làm chưa tốt / sẽ làm khác nếu làm lại?
> - Tự chấm phần mình phụ trách (C1, C2, C3) và lý do.

...
