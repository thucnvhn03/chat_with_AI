# T3-01 · Xóa tài liệu: endpoint và hộp thoại

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 3 — Xóa, phạm vi quyền, kiểm toán, hội thoại |
| Story | US-006 — Loại tài liệu khỏi tập truy vấn (P1); US-007 — Xóa vĩnh viễn nội dung tài liệu (P0) |
| Loại việc | BE+FE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T1-16, T2-02 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:**
  - **BE:** `DELETE /documents/{id}` (chủ sở hữu hoặc `security_admin`): trong một giao dịch đặt `status='deleting'`, `deleted_at=now()` và thêm `jobs(kind='purge')`; trả 202; phát `document_deleted`.
  - **FE:** `DeleteConfirmDialog` (C-05) khớp ảnh `s04-default` và `s04-failed`: tiêu điểm mặc định ở "Hủy", nêu tên tài liệu và "không thể hoàn tác", nêu thời hạn xóa `[TBD: OQ-012]`, lỗi hiển thị ngay trong hộp thoại.
- **Xong khi:** sau `DELETE` trả về, câu hỏi chỉ có đáp án trong tài liệu đó nhận `not_found` **ngay**, kể cả khi worker chưa chạy (AC-005); hộp thoại đóng bằng phím Esc và trả focus về nút gọi.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G2 (trước Sprint 3): OQ-003, OQ-012. Chưa có thì dùng giá trị tạm: chỉ tài liệu của chính mình; xóa ngay khi worker chạy; lưu bản ghi 365 ngày.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
