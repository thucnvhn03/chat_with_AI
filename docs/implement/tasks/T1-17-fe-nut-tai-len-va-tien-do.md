# T1-17 · FE: nút tải lên và tiến độ

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 1 — Truy cập và nạp tài liệu |
| Story | US-001 — Tải một file PDF lên (P0); US-002 — Tải nhiều PDF vào cùng một tập tài liệu (P0); US-003 — Biết file nào tải thất bại (P0) |
| Loại việc | FE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T0-05, T1-11 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** `UploadControl` (C-03) theo vùng "Tải PDF lên" ở `html_design/S-02-man-hinh-chinh.html`: chọn nhiều tệp, kéo thả, hiển thị tiến độ và kết quả **từng tệp**; kiểm tra phía trình duyệt (đuôi, kích thước) chỉ để phản hồi sớm, quyết định cuối ở backend; không khóa vùng hội thoại khi đang tải; xử lý mất kết nối: tệp chưa xong hiển thị "Chưa tải xong" kèm "Tải lại" (ảnh `s02-offline-upload`).
- **Xong khi:** kiểm thử Testing Library; E2E (Playwright chặn mạng giữa chừng): tệp chưa tải xong **không** xuất hiện là "Sẵn sàng".

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** không có

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
