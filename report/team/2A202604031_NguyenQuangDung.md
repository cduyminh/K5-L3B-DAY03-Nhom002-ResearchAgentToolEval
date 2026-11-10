# Báo cáo cá nhân — Nguyễn Quang Dũng (2A202604031)

## 1. Thông tin thành viên

- Họ tên: Nguyễn Quang Dũng
- MSSV: 2A202604031
- Email: dunghamhaha@gmail.com

## 2. Phần việc phụ trách

- CP3: xây dựng tool mới, viết `TOOL.md`, đăng ký implementation trong `tools/__init__.py`, khai báo schema trong `artifacts/tools.yaml`, và viết ít nhất 3 unit test cho mỗi tool.
- B5a: tổng hợp bằng chứng về tool mới và unit test trong báo cáo nhóm.

## 3. Đóng góp cụ thể

- Bổ sung `hn_search` để tìm Hacker News stories theo query; kiểm tra input, ánh xạ kết quả và trả error dict khi request thất bại.
- Bổ sung `summarize_text` và `extract_sentences` để xử lý văn bản cục bộ.
- Thay `extract_keywords` bằng `claim_evidence_matrix`: ghép nhận định với trích dẫn/bằng chứng người dùng cung cấp. Tool ghi rõ chỉ tổ chức thông tin, không tự xác minh tính đúng sai.
- Tạo `TOOL.md` cho từng tool và đồng bộ đăng ký trong `tools/__init__.py` với khai báo trong `artifacts/tools.yaml`.
- Viết 3 unit test cho mỗi tool: kiểm tra kết quả bình thường và các trường hợp input không hợp lệ hoặc không có dữ liệu/bằng chứng. Các HTTP call của `hn_search` được kiểm thử offline bằng `fake_http`.
- Xóa các test stub TODO cũ bị skip trong `test_tools_todo.py` để suite chỉ còn các test đang thực thi.

## 4. Bằng chứng

- Các tool và metadata: [hn_search](../../starter_v0/tools/hn_search/tool.py), [summarize_text](../../starter_v0/tools/summarize_text/tool.py), [extract_sentences](../../starter_v0/tools/extract_sentences/tool.py), [claim_evidence_matrix](../../starter_v0/tools/claim_evidence_matrix/tool.py); mỗi thư mục có `TOOL.md` tương ứng.
- Registry và schema: [tools/__init__.py](../../starter_v0/tools/__init__.py), [tools.yaml](../../starter_v0/artifacts/tools.yaml).
- Unit test: [test_tools_todo.py](../../starter_v0/tests/test_tools_todo.py) có 12 test cho 4 tool mới, chạy offline.
- Xác minh: từ thư mục `starter_v0`, chạy `.\.venv\Scripts\python.exe -m pytest -q`; kết quả `94 passed in 0.35s`, không skipped hoặc failed.
- Cách tự kiểm tra: dùng contract test để kiểm tra sự khớp nhau giữa manifest, function signature, registry và `TOOL.md`; dùng unit test với fake HTTP cho nhánh thành công và HTTP lỗi của `hn_search`.
- Commit/PR: chưa ghi nhận mã commit hoặc PR riêng trong báo cáo này.

## 5. Tự đánh giá

- Hoàn thành phần CP3 theo cấu trúc tool của starter và kiểm tra được bằng full test suite.
- Các tool mới có phạm vi đa dạng hơn: tìm kiếm Hacker News, xử lý văn bản và tổ chức bằng chứng nghiên cứu.
- Giới hạn: `summarize_text` hiện lấy các câu đầu thay vì đánh giá mức độ quan trọng; `claim_evidence_matrix` chỉ ghép theo nội dung nhận định khớp chính xác và không xác minh nguồn hay sự thật. Các giới hạn này đã được mô tả trong `TOOL.md`/kết quả tool để tránh hiểu nhầm.
