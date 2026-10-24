# T0-10 · Nền cơ sở dữ liệu và kiểm thử tích hợp

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 0 — Nền tảng và spike |
| Story | Nền tảng / nghiệm thu (không gắn riêng một story) |
| Loại việc | BE |
| Cỡ | S (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T0-04 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** cấu hình Alembic; migration đầu tiên tạo `CREATE EXTENSION vector`; fixture pytest dùng testcontainers (PostgreSQL có pgvector và MinIO) chạy migration trước mỗi phiên kiểm thử; hàm tạo dữ liệu mẫu.
- **Sản phẩm:** `backend/alembic/*`, `backend/tests/conftest.py`.
- **Xong khi:** kiểm thử tích hợp mẫu chạy được trên CI và cục bộ; `alembic upgrade head` và `downgrade base` đều thành công.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G0 (cuối Sprint 0): chốt bộ công nghệ, DQ-003, kết quả ba spike.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
