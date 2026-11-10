---
name: claim_evidence_matrix
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [claims, evidence]
outputs: [matrix, verification, note]
side_effect: false
requires_confirmation: false
---

Sắp xếp các nhận định và trích dẫn/bằng chứng do người dùng cung cấp thành bảng.

- Mỗi mục evidence cần có `claim` và `citation`; `excerpt` là phần trích dẫn hoặc ghi chú bằng chứng tùy chọn.
- Chỉ ghép evidence với nhận định có nội dung khớp chính xác sau khi bỏ khoảng trắng đầu/cuối.
- Không tìm nguồn, không đánh giá độ tin cậy, và không xác minh nhận định là đúng hay sai. Kết quả luôn ghi `verification: not_performed`.