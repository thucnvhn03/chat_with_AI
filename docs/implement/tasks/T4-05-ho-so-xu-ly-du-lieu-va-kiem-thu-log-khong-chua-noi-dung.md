# T4-05 · Hồ sơ xử lý dữ liệu và kiểm thử "log không chứa nội dung"

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 4 — Chất lượng, đo lường, sẵn sàng phát hành |
| Story | US-019 — Tài liệu được xử lý và lưu theo chính sách dữ liệu (P0) |
| Loại việc | QA+OPS |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T3-02, T3-04; G1 (OQ-005, OQ-006) |
| Trạng thái | Review (kiểm thử canary đạt, data_handling.md đã soạn; chờ bộ phận bảo mật xác nhận bằng văn bản) |

- **Làm gì:**
  1. Kiểm thử tự động theo `implement_plan.md` mục 9.3: chạy luồng tải lên, hỏi đáp, xóa với chuỗi đánh dấu duy nhất (`CANARY-…`) trong tài liệu và câu hỏi; thu toàn bộ log, sự kiện phân tích, bản ghi kiểm toán, `usage_events`; khẳng định chuỗi không xuất hiện.
  2. Viết `docs/implement/data_handling.md`: dữ liệu nào đi đâu (đặc biệt phần gửi tới dịch vụ AI ở Kịch bản A), nơi lưu, mã hóa, thời gian lưu, quy trình xóa, sao lưu.
  3. Trình bộ phận bảo mật rà soát.
- **Xong khi:** kiểm thử canary đạt; có xác nhận bằng văn bản của bộ phận bảo mật (AC-015, LG-06).

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G3 (trước Sprint 4): OQ-002 (ngưỡng), bộ câu hỏi chuẩn đầy đủ. | Cổng G4 (cuối Sprint 4): tiêu chí launch LG-01..LG-11 đạt, hoặc có quyết định ngoại lệ bằng văn bản của sponsor.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
