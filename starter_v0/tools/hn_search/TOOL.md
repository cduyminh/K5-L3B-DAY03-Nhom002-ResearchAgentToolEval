---
name: hn_search
track: bonus
kind: live_api
provider: Hacker News Algolia
requires_env: []
inputs: [query, limit]
outputs: [items]
side_effect: false
requires_confirmation: false
---

Tìm các bài viết kiểu story trên Hacker News theo từ khóa.

- Dùng khi cần tra cứu tin tức / chủ đề đang hot trên HN.
- Bắt buộc có `query` và có thể tùy chọn `limit` (mặc định 5).
- Không dùng cho tìm kiếm email, tài liệu nội bộ, hay nội dung không phải story.

Khi gọi API, gửi query và `tags=story`, đồng thời giới hạn số lượng kết quả bằng `limit`.
