---
name: extract_sentences
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [text, limit]
outputs: [sentences, count]
side_effect: false
requires_confirmation: false
---

Trích xuất các câu đầu tiên hoặc các câu quan trọng nhất từ một đoạn văn bản.

- Dùng khi cần lấy ngắn gọn nội dung quan trọng từ văn bản dài.
- Không dùng cho tìm kiếm web hoặc thao tác ngoài văn bản.
- Trả về danh sách câu và số lượng câu đã chọn.
