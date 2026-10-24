# T4-07 · Tài liệu vận hành

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 4 — Chất lượng, đo lường, sẵn sàng phát hành |
| Story | Nền tảng / nghiệm thu (không gắn riêng một story) |
| Loại việc | OPS |
| Cỡ | S (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T4-04 |
| Trạng thái | Review (ops_runbook.md xong; chờ một người ngoài đội thử triển khai theo runbook) |

- **Làm gì:** `docs/implement/ops_runbook.md`: triển khai và quay lui, migration, biến cấu hình (nguồn quyết định), xử lý việc `failed`, xử lý tài liệu `deleting` quá hạn, sao lưu và khôi phục (AQ-003), xoay khóa API, xử lý sự cố lộ dữ liệu.
- **Xong khi:** một người ngoài đội làm theo runbook triển khai được lên môi trường kiểm thử.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G3 (trước Sprint 4): OQ-002 (ngưỡng), bộ câu hỏi chuẩn đầy đủ. | Cổng G4 (cuối Sprint 4): tiêu chí launch LG-01..LG-11 đạt, hoặc có quyết định ngoại lệ bằng văn bản của sponsor.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
