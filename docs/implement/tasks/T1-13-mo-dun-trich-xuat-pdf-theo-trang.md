# T1-13 · Mô-đun trích xuất PDF theo trang

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 1 — Truy cập và nạp tài liệu |
| Story | US-001 — Tải một file PDF lên (P0); US-003 — Biết file nào tải thất bại (P0); US-004 — Biết lý do tệp thất bại (P1) |
| Loại việc | BE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T0-06 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** `modules/ingestion/extract.py`: `extract_pages(stream) -> list[PageText]` dùng thư viện đã chọn ở spike. Phát hiện tài liệu mã hóa (`encrypted`), hỏng (`corrupted`), không có văn bản (`no_text`, tổng ký tự < `MIN_TEXT_CHARS`). Chuẩn hóa Unicode NFC và khoảng trắng. Số trang bắt đầu từ 1.
- **Xong khi:** kiểm thử đơn vị trên bộ PDF tổng hợp ở `backend/tests/fixtures/` (PDF thường, tiếng Việt, mã hóa, hỏng, chỉ ảnh): mỗi tệp cho đúng kết quả hoặc đúng loại lỗi; số trang khớp.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** không có

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
