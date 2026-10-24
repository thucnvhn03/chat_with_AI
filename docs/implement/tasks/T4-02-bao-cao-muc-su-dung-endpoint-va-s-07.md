# T4-02 · Báo cáo mức sử dụng: endpoint và S-07

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 4 — Chất lượng, đo lường, sẵn sàng phát hành |
| Story | US-022 — Số người dùng hoạt động hằng tuần (P1); US-023 — Số câu hỏi hằng tuần (P1) |
| Loại việc | BE+FE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T2-05, T1-06 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:**
  - **BE:** `GET /reports/usage?weeks=4` (vai trò `manager`): đếm người dùng khác nhau và số câu hỏi theo tuần từ `usage_events`; thêm tỷ lệ `helpful` khi có T4-03.
  - **FE:** S-07 theo `S-07-bao-cao-su-dung.html`, ảnh `s07-default`, `s07-empty`, `s07-error`: thẻ số liệu, biểu đồ cột có chú giải **và** bảng số liệu tương ứng (không phụ thuộc màu), trạng thái trống, lỗi.
- **Xong khi:** với dữ liệu hạt giống đã biết, số liệu đúng (AC-016, AC-021); vai trò khác → 403.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G3 (trước Sprint 4): OQ-002 (ngưỡng), bộ câu hỏi chuẩn đầy đủ. | Cổng G4 (cuối Sprint 4): tiêu chí launch LG-01..LG-11 đạt, hoặc có quyết định ngoại lệ bằng văn bản của sponsor.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
