# Báo cáo cá nhân — HoangNhatMinh_2A202603992

## 1. Thông tin thành viên

- Họ tên: Hoàng Nhật Minh
- MSSV: 2A202603992
- Email: minh40009@gmail.com
- Nhóm: Nhom002 — lớp L3B

## 2. Phần việc phụ trách

Theo phân công trong [`TEAM.md`](../../TEAM.md):

- **CP5 — UI Streamlit** cho Research Agent và link dùng thử qua Cloudflare Tunnel.
- **Live chat ≥ 3 lượt** có transcript làm bằng chứng (yêu cầu thường → thiếu thông tin rồi bổ sung → yêu cầu gửi/đăng).
- **Group report:** Phần A (A1–A3) và bảng B4 (Live Chat Evidence).

## 3. Đóng góp cụ thể

### 3.1. UI Streamlit — `starter_v0/app.py` (commit `9714733`)

- Viết UI chat chạy **cùng vòng lặp tool** với `chat.py` (tái sử dụng `run_model_tool_loop`, `trim_history`, `write_transcript`), nên transcript từ UI có **đúng định dạng** với CLI (`transcripts/<version>_<provider>_<timestamp>.transcript.json`, thêm trường `"ui": "streamlit"`).
- Sidebar cấu hình: provider, model, version label (tự lấy version mới nhất trong `artifacts/version_log.csv`), history window, max tool rounds; nút **New chat** áp dụng cấu hình.
- Hiển thị từng lượt gọi tool (tên tool, args, result) trong expander; tool lỗi được đánh dấu ⚠️ thay vì bị ẩn — để UI **không che lỗi tool** (yêu cầu C6).
- Hiển thị trạng thái đặc biệt: `waiting_for_user` (agent đang hỏi lại / chờ xác nhận), `max_tool_rounds`, `provider_error`.
- Nút tải transcript JSON ngay trên UI.
- Thêm `streamlit>=1.30.0` vào `starter_v0/requirements.txt`.

Chạy UI:

```bash
cd starter_v0
pip install -r requirements.txt
streamlit run app.py --server.port 8500
cloudflared tunnel --protocol http2 --edge-ip-version 4 --url http://localhost:8500
```

### 3.2. Sửa provider Anthropic — `starter_v0/providers/anthropic_provider.py` (commit `9714733`)

Khi chạy bằng model Claude thế hệ mới, API trả về lỗi 400 vì starter gửi `temperature` và `tool_choice` ép buộc. Mình đã sửa:

- Không gửi `temperature`; chỉ dùng `tool_choice: any` cho các model cũ còn hỗ trợ.
- Default model đọc từ biến `ANTHROPIC_MODEL`, fallback `claude-opus-5-5`; tăng `max_tokens` lên 16000.
- Bắt `stop_reason == "refusal"` để trả về text rõ ràng thay vì crash.
- Nâng `anthropic>=2.7.0` trong `requirements.txt`.

### 3.3. Baseline v0 trên Anthropic (commit `9714733`)

- Chạy base eval v0 bằng `claude-opus-5-5`: `runs/v0_B_base_anthropic_20261110T172857200899.json` — **15/20 = 0.75**, `provider_error_cases = 0`, `measured_cases = total_cases = 20` (run hợp lệ). Tool routing 0.95, argument accuracy 0.75, multi-turn 0.83.
- Ghi dòng tương ứng vào `artifacts/version_log.csv` (author: Hoàng Nhật Minh) để so sánh với baseline OpenRouter của nhóm.

### 3.4. Live chat và transcript

Chạy live trên UI với `claude-opus-5-5`, artifact version v3. Transcript quan trọng nhất là `transcripts/v3_anthropic_20261110T183833029291.transcript.json` (3 lượt, đủ 3 loại yêu cầu của C6):

| Turn | User Request | Tool Calls | Outcome |
|---|---|---|---|
| 1 | "Tóm tắt 5 tweet mới nhất giúp mình" | `clarify` | `waiting_for_user` — agent **không đoán** tài khoản, hỏi lại handle |
| 2 | "của elonmusk" | `timeline(screenname="elonmusk", limit=5)` | `answered` — tóm tắt 5 tweet có link nguồn |
| 3 | "Đăng bản tóm tắt này lên Telegram giúp mình" | `clarify` | `waiting_for_user` — agent hiển thị nội dung sẽ đăng và **xin xác nhận trước khi gửi**, chưa gọi `send` |

Các transcript bổ sung (cùng ngày 10/11/2026):

- `v3_anthropic_20261110T182452073182` — "Tin AI hôm nay có gì nổi bật?" → `lookup`.
- `v3_anthropic_20261110T182254735641` — "Whats sam altman tweet today" → `timeline`.
- `v3_anthropic_20261110T184310323012` — "Mọi người đang bàn gì về GPT-5 trên Twitter?" → `social_search` (tool mới của nhóm).
- `v3_anthropic_20261110T182402177131` — "Hello" → trả lời trực tiếp, **không gọi tool thừa**.

### 3.5. Nhật ký người dùng và dọn provider (sau commit `9714733`, cần commit trước khi nộp)

- `starter_v0/user_log.py`: ghi mỗi lượt hỏi vào `logs/user_activity.jsonl` gồm **người dùng, provider/model, câu hỏi, câu trả lời**, trạng thái, tool đã gọi, id transcript. Dùng chung cho UI (ô "Tên người dùng" + bảng "📒 Nhật ký người dùng" trong sidebar) và CLI (`chat.py --user`). Có 3 unit test trong `tests/test_user_log.py`; `logs/` được thêm vào `.gitignore` để không commit dữ liệu người dùng.
- Bỏ các lựa chọn provider `openai`, `gemini`, `ollama` khỏi UI và CLI (`app.py`, `chat.py`, `run_eval.py`, `scripts/preflight_provider.py`). Lý do: nhóm không có key cho các provider này; 2 transcript `v0_openrouter_…175820…` và `v3_openai_…182346…` cho thấy chọn nhầm provider chỉ dẫn tới `provider_error: Missing API key env var`.

## 4. Bằng chứng

- **File/commit/PR:**
  - Commit `9714733` "UI": `starter_v0/app.py`, `starter_v0/providers/anthropic_provider.py`, `starter_v0/requirements.txt`, `starter_v0/artifacts/version_log.csv`, `starter_v0/runs/v0_B_base_anthropic_20261110T172857200899.json`, 2 transcript đầu tiên.
  - Commit `cb10d22`: tạo file báo cáo cá nhân.
  - Transcript live: `starter_v0/transcripts/v3_anthropic_*.transcript.json` (6 file, liệt kê ở mục 3.4).
  - Thay đổi chưa commit (mục 3.5): `starter_v0/user_log.py`, `starter_v0/tests/test_user_log.py`, `starter_v0/.gitignore`, `starter_v0/app.py`, `starter_v0/chat.py`, `starter_v0/run_eval.py`, `starter_v0/scripts/preflight_provider.py`.
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Dùng Claude Code hỗ trợ viết UI, sửa provider và chức năng nhật ký.
  - Tự kiểm tra: chạy `pytest` sau mỗi thay đổi (**65 passed, 0 failed**); mở UI chat thật với API key thật và đọc lại từng transcript JSON để xác nhận tool được gọi đúng, args đúng, lỗi provider hiển thị đúng chứ không bị ẩn; kiểm tra run v0 có `provider_error_cases == 0` trước khi ghi vào `version_log.csv`; dùng `git check-ignore` để xác nhận `logs/` không bị commit.

## 5. Tự đánh giá

**Làm tốt:**

- UI chạy được, dùng chung logic với `chat.py` nên transcript từ UI dùng được trực tiếp làm bằng chứng cho C6, không phải viết lại.
- Transcript 3 lượt thể hiện đúng hai hành vi quan trọng nhất của lab: **hỏi lại khi thiếu thông tin** và **xin xác nhận trước khi đăng**, thay vì chỉ "trả lời nghe hay".
- Tìm và sửa lỗi tương thích của provider Anthropic với model mới, giúp nhóm có thêm một baseline hợp lệ thứ hai để so sánh.

**Chưa làm được / cần cải thiện:**

- Link Cloudflare Tunnel từng bị lỗi QUIC timeout (`failed to dial to edge with quic`) do mạng chặn UDP; cần chạy với `--protocol http2` và dán URL cuối cùng vào mục A1 của group report.
- Phần A (A1–A3) và bảng B4 trong `report/team/group_report.md` cần điền nốt từ các transcript ở mục 3.4.
- Transcript live hiện đều chạy qua UI Streamlit; nên chạy thêm một phiên `chat.py` CLI ≥ 3 lượt để có bằng chứng cho cả hai đường.
- Lượt 3 dừng ở bước xin xác nhận; chưa có lượt "xác nhận → `send(confirmed=true)` → `status: sent`" (cần cho bonus Telegram nếu nhóm làm).
- Cần commit các thay đổi ở mục 3.5 bằng đúng email `minh40009@gmail.com` (commit `cb10d22` trước đó bị dùng email mặc định của máy).
