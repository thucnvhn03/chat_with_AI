# T1-09 · Migration `documents`, `jobs`, `chunks`

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 1 — Truy cập và nạp tài liệu |
| Story | US-001 — Tải một file PDF lên (P0) |
| Loại việc | BE |
| Cỡ | S (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T0-10 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** tạo ba bảng đúng như mục 3 của plan, gồm các ràng buộc `CHECK` (trạng thái, lý do lỗi) và chỉ mục HNSW. `chunks.page` là `NOT NULL`. Số chiều vector đọc từ kết quả spike T0-07.
- **Xong khi:** migration lên/xuống; chèn `chunks` thiếu `page` bị từ chối; chèn `status` ngoài danh sách bị từ chối.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** không có

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
