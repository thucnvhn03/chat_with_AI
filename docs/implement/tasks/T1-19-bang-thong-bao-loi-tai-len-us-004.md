# T1-19 · Bảng thông báo lỗi tải lên (US-004)

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 1 — Truy cập và nạp tài liệu |
| Story | US-004 — Biết lý do tệp thất bại (P1) |
| Loại việc | FE |
| Cỡ | S (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T1-18 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** một tệp `frontend/src/features/documents/failureMessages.ts` ánh xạ `failure_reason` → câu tiếng Việt kèm cách khắc phục cho `corrupted`, `encrypted`, `not_pdf`, `too_large`, `no_text`, `network`, `internal`. Câu mẫu: "Tài liệu bị khóa hoặc mã hóa. Hãy mở khóa rồi tải lại." Mã không biết → câu chung, không hiện mã kỹ thuật.
- **Xong khi:** kiểm thử đơn vị: mỗi mã trả đúng một câu không rỗng; mã lạ trả câu chung (AC-018).

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** không có

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
