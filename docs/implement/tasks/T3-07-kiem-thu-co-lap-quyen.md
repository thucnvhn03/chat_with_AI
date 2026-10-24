# T3-07 · Kiểm thử cô lập quyền

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 3 — Xóa, phạm vi quyền, kiểm toán, hội thoại |
| Story | US-018 — Chỉ thấy tài liệu trong phạm vi chia sẻ (P0) |
| Loại việc | QA |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T3-03 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** `backend/tests/security/test_isolation.py`: hai người dùng A và B, mỗi người một tài liệu có chuỗi đặc trưng. Khẳng định: A hỏi nội dung của B → `not_found`; A gọi `GET /documents/{idB}`, `/pages/…`, `/file`, `DELETE`, `POST …/retry` → 404; danh sách của A không có tài liệu của B; bản ghi kiểm toán của A không liệt kê tài liệu của B. Kiểm thử tự sinh từ danh sách route để khỏi bỏ sót route mới.
- **Xong khi:** tất cả đạt (AC-020, LG-07); thêm cố ý một route không kiểm quyền thì kiểm thử đỏ.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G2 (trước Sprint 3): OQ-003, OQ-012. Chưa có thì dùng giá trị tạm: chỉ tài liệu của chính mình; xóa ngay khi worker chạy; lưu bản ghi 365 ngày.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
