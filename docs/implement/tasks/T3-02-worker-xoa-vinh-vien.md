# T3-02 · Worker xóa vĩnh viễn

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 3 — Xóa, phạm vi quyền, kiểm toán, hội thoại |
| Story | US-007 — Xóa vĩnh viễn nội dung tài liệu (P0) |
| Loại việc | BE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T3-01, T1-12 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** bộ xử lý `purge`: xóa `chunks` của tài liệu → xóa tệp trên kho → đặt `status='deleted'`, `purged_at=now()`. Mỗi bước làm lại được nhiều lần không lỗi. Cảnh báo nếu có tài liệu `deleting` quá `PURGE_SLA_HOURS`. Ghi vào `docs/implement/ops_runbook.md` cách xử lý bản sao lưu (AQ-003).
- **Xong khi:** kiểm thử tích hợp: sau khi worker chạy không còn chunk, không còn tệp trên MinIO, `purged_at` có giá trị (AC-024); giả lập lỗi kho tệp giữa chừng → thử lại và hoàn tất; chạy `purge` hai lần không lỗi.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G2 (trước Sprint 3): OQ-003, OQ-012. Chưa có thì dùng giá trị tạm: chỉ tài liệu của chính mình; xóa ngay khi worker chạy; lưu bản ghi 365 ngày.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
