# T3-04 · Bản ghi kiểm toán: endpoint và màn hình S-06

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 3 — Xóa, phạm vi quyền, kiểm toán, hội thoại |
| Story | US-020 — Bản ghi ai hỏi về tài liệu nào, khi nào (P1) |
| Loại việc | BE+FE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T2-05, T1-07 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:**
  - **BE:** `GET /admin/audit?from&to&user&document&cursor` (chỉ `security_admin`; phân trang con trỏ); tác vụ dọn bản ghi quá `AUDIT_RETENTION_DAYS`.
  - **FE:** S-06 theo `S-06-ban-ghi-kiem-toan.html`, ảnh `s06-default`, `s06-empty`, `s06-error`: bộ lọc, bảng (thời điểm, người dùng, tài liệu liên quan), trạng thái trống và lỗi (kèm "Thử lại"); không hiển thị nội dung câu hỏi.
- **Xong khi:** mỗi câu hỏi sinh đúng một bản ghi hiển thị được; bộ lọc hoạt động; vai trò khác gọi → 403 (AC-023).

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G2 (trước Sprint 3): OQ-003, OQ-012. Chưa có thì dùng giá trị tạm: chỉ tài liệu của chính mình; xóa ngay khi worker chạy; lưu bản ghi 365 ngày.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
