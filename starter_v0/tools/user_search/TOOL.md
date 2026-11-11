---
name: user_search
track: bonus
kind: live_api
provider: RapidAPI twitter-api45 (/search.php, search_type=People)
requires_env: [RAPIDAPI_KEY]
inputs: [name, limit]
outputs: [query, count, candidates]
side_effect: false
---

# user_search

Tìm tài khoản X/Twitter theo **tên người** khi user nhắc một người mà không đưa handle
và người đó không phải người nổi tiếng có sẵn trong mô tả `timeline`.

Vì sao cần: không có tool này, model tự ghép handle từ tên (eval G15, v9:
"Trần Minh Khoa" → `timeline(screenname="tranminhkhoa")`). Handle bịa đó lại là một
tài khoản thật không liên quan (`/screenname.php` trả `status: active`), nên agent sẽ
trả tweet của người lạ mà không báo lỗi.

Cách dùng đúng:
- Gọi `user_search(name=...)` để lấy danh sách ứng viên (tối đa 5: `screen_name`,
  `name`, `followers_count`, `description`, `verified`, `profile_url`).
- Sau đó **luôn** để user chọn bằng `clarify(response_type="choice", options=[...])`
  (hoặc hỏi handle nếu không có ứng viên); không tự chọn một tài khoản.
- Chỉ gọi `timeline` với handle user đã chọn hoặc tự gõ.

Giới hạn và guardrail:
- Chỉ đọc, chỉ trả trường hồ sơ công khai; không lưu.
- Chỉ chạy khi user tự nêu tên người cần tìm; không dùng để dò thông tin người khác.
- `limit` bị kẹp trong 1..5; input xấu (rỗng, sai kiểu, quá dài) trả error dict, không raise.
