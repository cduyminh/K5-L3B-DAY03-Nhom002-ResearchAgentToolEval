# Báo cáo cá nhân — Nguyễn Quang Dũng (2A202604031)

## 1. Thông tin thành viên

- Họ tên: Nguyễn Quang Dũng
- MSSV: 2A202604031
- Email: dunghamhaha@gmail.com

## 2. Phần việc phụ trách

Tôi phụ trách phần triển khai và kiểm chứng tool mới cho nhóm:

- Xây dựng tool `hn_search` để tìm các bài viết story trên Hacker News theo từ khóa.
- Viết file mô tả tool theo chuẩn của repo.
- Đăng ký tool vào `TOOL_FUNCTIONS` và khai báo trong `starter_v0/artifacts/tools.yaml`.
- Viết 3 test unit cho tool mới: happy path, bad input, failure path.
- Chạy kiểm tra contract và full pytest để xác minh không có failed.

## 3. Đóng góp cụ thể

1. Triển khai tool mới
   - File: `starter_v0/tools/hn_search/tool.py`
   - Tool nhận `query` bắt buộc và `limit` mặc định `5`.
   - Gọi API `https://hn.algolia.com/api/v1/search` với `tags=story`.
   - Parse kết quả và trả về `items` gồm `title`, `url`, `source`, `summary`, `score`.
   - Nếu query rỗng hoặc lỗi HTTP thì trả về `error` dict theo chuẩn của project, không raise exception.

2. Viết tài liệu cho tool
   - File: `starter_v0/tools/hn_search/TOOL.md`
   - Mô tả mục đích, đầu vào, đầu ra, và khi nào nên dùng / không nên dùng.

3. Đăng ký tool vào hệ thống
   - File: `starter_v0/tools/__init__.py`
   - File: `starter_v0/artifacts/tools.yaml`
   - Đảm bảo tên tool, registry và khai báo YAML đồng bộ với eval contract.

4. Viết unit test cho tool mới
   - File: `starter_v0/tests/test_tools_todo.py`
   - Test happy path: mock API và kiểm tra `url`, `tags`, `hitsPerPage`, dữ liệu trả về.
   - Test bad input: query rỗng -> trả `ValueError` trong error dict.
   - Test failure path: HTTP 500 -> trả `HTTPError` trong error dict.

## 4. Bằng chứng

### File chính đã cập nhật
- `starter_v0/tools/hn_search/tool.py`
- `starter_v0/tools/hn_search/TOOL.md`
- `starter_v0/tools/__init__.py`
- `starter_v0/artifacts/tools.yaml`
- `starter_v0/tests/test_tools_todo.py`

### Lệnh tự kiểm tra

```powershell
cd D:\Lab3-002\K5-L3B-DAY03-Nhom002-ResearchAgentToolEval\starter_v0
.\.venv\Scripts\python.exe -m pytest tests/test_tool_contract.py -q
```

Kết quả thực tế: `60 passed in 0.23s`

```powershell
cd D:\Lab3-002\K5-L3B-DAY03-Nhom002-ResearchAgentToolEval\starter_v0
.\.venv\Scripts\python.exe -m pytest -q
```

Kết quả thực tế: `70 passed, 14 skipped in 0.29s`

> Trong toàn bộ suite không có failed. Các `skipped` còn lại là test challenge mẫu chưa làm trong file todo, không phải lỗi của tool mới.

## 5. Tự đánh giá

- Mức độ hoàn thành: 8.5/10
- Điểm mạnh: triển khai tool mới theo chuẩn repo, đồng bộ đúng registry và YAML, có unit test cho happy path và lỗi, kiểm tra bằng pytest đạt 0 failed.
- Cần cải thiện: nếu muốn đạt `0 skipped`, nhóm cần hoàn thiện các test stub còn lại trong `starter_v0/tests/test_tools_todo.py`.
- Kết luận: phần công việc của tôi trong CP3 đã hoàn thành đúng mục tiêu: thêm tool mới, test tool mới, và chứng minh tool hoạt động đúng theo contract.
