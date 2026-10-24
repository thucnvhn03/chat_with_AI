# T1-12 · Hàng đợi việc và vòng lặp worker

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 1 — Truy cập và nạp tài liệu |
| Story | US-001 — Tải một file PDF lên (P0) |
| Loại việc | BE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T1-09 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** `app/worker/run.py`: vòng lặp lấy việc bằng `UPDATE … FOR UPDATE SKIP LOCKED` (đoạn SQL ở mục 5.1 của plan); đăng ký bộ xử lý theo `kind` (`ingest`, `purge`); thử lại với thời gian chờ tăng dần tới `JOB_MAX_ATTEMPTS`, quá số lần → `failed` kèm `last_error`; chạy `WORKER_CONCURRENCY` việc song song; tắt êm khi nhận tín hiệu dừng. Phát số liệu độ dài hàng đợi.
- **Xong khi:** kiểm thử tích hợp: hai worker chạy đồng thời không bao giờ lấy cùng một việc; việc lỗi tạm thời được thử lại; việc quá số lần thử chuyển `failed`.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** không có

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
