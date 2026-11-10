---
name: word_count
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [text]
outputs: [word_count, unique_words, tokens]
side_effect: false
requires_confirmation: false
---

Đếm số từ và số từ duy nhất trong văn bản.

- Dùng khi cần thống kê ngắn gọn hoặc kiểm tra độ dài văn bản.
- Không dùng để tìm tin tức, truy xuất web hoặc sửa dữ liệu.
- Trả về số từ, số từ duy nhất và danh sách token đã tokenize.
