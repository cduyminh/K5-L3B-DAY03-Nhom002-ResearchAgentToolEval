# Team

## Thông tin nhóm

- Tên nhóm: Nhom002
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-Nhom002-ResearchAgentToolEval`
- URL repo, nhánh nộp, commit chốt: https://github.com/cduyminh/K5-L3B-DAY03-Nhom002-ResearchAgentToolEval · nhánh `main` · commit chốt: `ef67e97` (B7, nội dung bài hoàn chỉnh; các commit sau chỉ cập nhật TEAM.md / tự đánh giá)

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Cao Duy Minh | 2A202603988 | cduyminh@gmail.com | cduyminh | Nhóm trưởng · CP1 baseline v0 · CP2 v1–v3 (`system_prompt.md`, `tools.yaml`, `version_log.csv`) · B1, B2, B6 |
|   2 | Hoàng Nhật Minh | 2A202603992 | Minh40009@gmail.com |  | CP5 UI Streamlit + link dùng thử (Cloudflare Tunnel) · `chat.py` ≥3 lượt live · Phần A (A1–A3) · B4 |
|   3 | Nguyễn Quang Dũng | 2A202604031 | dunghamhaha@gmail.com | NguyenQuangDunghe161764 | CP3 tool mới (`tools/<tên>/tool.py` + `TOOL.md`, đăng ký) + ≥3 unit test · B5a |
|   4 |Lê Thị Ly  |2A202603989  |lethily100202@gmail.com  | LyLe10 | CP4 10 case eval nhóm (`data/eval_group.json`, 5 single + 5 multi) + chạy `--suite group` · B3 |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## CaoDuyMinh-2A202603988

### Phần việc phụ trách

- Nhóm trưởng: fork/đặt tên repo, chia việc theo checkpoint, gom bài.
- CP1 baseline v0; CP2 vòng tối ưu v1–v3 (`system_prompt.md`, `tools.yaml`, `version_log.csv`); B1, B2, B6.

### Đóng góp cụ thể

- v0 → v3 trên OpenRouter `gpt-4o-mini`: 0.75 → 0.80 → 0.90 → 1.00 (base suite), mỗi version một giả thuyết.
- v4–v8 sau khi test site: guardrail scope/injection theo slide (v4), giới hạn `limit` (v5), guardrail mức tool (v6), chống lệnh base64 (v7), định nghĩa xác nhận + cổng duyệt `approval.py` ở tầng app (v8).
- 15 case adversarial A01–A15 + 3 case G11–G13 trong `eval_group.json`; phát hiện regression A15 (tự xưng admin → `send`).
- Showcase v0 → v8 + tab "Tất cả test case" trong UI; bonus Telegram (gửi thật sau xác nhận), local model (Ollama).

### Bằng chứng

- Commit: `47017d3` (v0), `9babd3c` (v1), `f319c78` (v2), `e6dd5e7` (v3), `79487a8` (v4), `3bb667c` (v5), `3eb2b28` (v6), `85175f4` (v7), `cea41ce` (v8), `fb2d06b` (adversarial), `8c963a2`/`9d31a8c` (showcase), `4701740` (Telegram).
- Báo cáo cá nhân: `report/team/2A202603988_CaoDuyMinh.md`.

## HoangNhatMinh-2A202603992

### Phần việc phụ trách

- CP5: UI Streamlit + link dùng thử (Cloudflare Tunnel), `chat.py` ≥ 3 lượt live, Phần A (A1–A3), B4.

### Đóng góp cụ thể

- UI Streamlit `starter_v0/app.py` (commit `9714733`), sửa provider Anthropic cho model mới, mặc định version mới nhất (`7c0714e`).
- Transcript live chat v3/v5 trên `claude-opus-5-5` (`eb5fb21`, `fe7c8ff`); baseline v0 thứ hai trên Anthropic.

### Bằng chứng

- Commit: `9714733`, `7c0714e`, `eb5fb21`, `fe7c8ff`; báo cáo cá nhân `report/team/2A202603992_HoangNhatMinh.md`.

## NguyenQuangDung-2A202604031

### Phần việc phụ trách

- CP3: tool mới + `TOOL.md` + đăng ký + ≥ 3 unit test/tool; B5a.

### Đóng góp cụ thể

- Tool `hn_search` (commit `d5d020a`) và 3 tool thêm `summarize_text`, `extract_sentences`, `claim_evidence_matrix` (`437c08d`), mỗi tool 3 test trong `tests/test_tools_todo.py`.

### Bằng chứng

- Commit: `d5d020a`, `61ad8c9`, `437c08d`; báo cáo cá nhân `report/team/2A202604031_NguyenQuangDung.md`.

## LeThiLy-2A202603989

### Phần việc phụ trách

- CP4: 10 case eval nhóm (5 single + 5 multi turn) trong `data/eval_group.json`, chạy `--suite group`; B3.

### Đóng góp cụ thể

- G01–G10, gồm case route tới tool mới `hn_search` (G05); run group v3 và bảng B3 (`8b69ce2`, `e7c51eb`, `3c540a5`, `8e09c60`).

### Bằng chứng

- Commit: `8b69ce2`, `e7c51eb`, `3c540a5`, `8e09c60`; báo cáo cá nhân `report/team/2A202603989_LeThiLy.md`.
