---
name: summarize_text
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [text, max_sentences]
outputs: [summary, sentence_count]
side_effect: false
requires_confirmation: false
---

Tóm tắt ngắn một đoạn văn bản bằng cách giữ lại các câu mở đầu hoặc câu quan trọng nhất.

- Dùng khi cần một bản tóm tắt ngắn để đọc nhanh.
- Không dùng để mô tả toàn bộ nội dung chi tiết hoặc tìm kiếm web.
- Trả về bản tóm tắt và số câu đã chọn.
