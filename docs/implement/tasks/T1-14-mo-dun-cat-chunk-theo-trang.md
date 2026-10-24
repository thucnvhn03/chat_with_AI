# T1-14 · Mô-đun cắt chunk theo trang

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 1 — Truy cập và nạp tài liệu |
| Story | US-001 — Tải một file PDF lên (P0) |
| Loại việc | BE |
| Cỡ | S (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T1-13 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** `modules/ingestion/chunking.py`: cắt mỗi trang thành các chunk `CHUNK_TOKENS` có chồng lấp `CHUNK_OVERLAP`, **không vượt qua ranh giới trang**; mỗi chunk có `page`, `ordinal`, `text`. Đếm token bằng bộ đếm tương thích với mô hình embedding đã chọn.
- **Xong khi:** kiểm thử đơn vị: không chunk nào chứa văn bản của hai trang; trang ngắn cho đúng một chunk; trang rỗng không sinh chunk; tổng văn bản các chunk (bỏ phần chồng lấp) bằng văn bản trang.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** không có

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
