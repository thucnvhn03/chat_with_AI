# T4-04 · Health, giám sát và cảnh báo

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 4 — Chất lượng, đo lường, sẵn sàng phát hành |
| Story | US-021 — Mức sẵn sàng của ứng dụng (P2) |
| Loại việc | OPS |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T0-04, T3-02 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** `/health/ready` kiểm cơ sở dữ liệu, kho tệp, hàng đợi và tuổi việc cũ nhất; bảng giám sát: thời gian phản hồi, tỷ lệ lỗi, tỷ lệ `not_found`, độ dài hàng đợi, thời gian nạp tài liệu, số tài liệu `deleting` quá hạn; cảnh báo theo AQ-005 và OQ-011 (chưa có thì dùng giá trị tạm trong tài liệu).
- **Xong khi:** dừng một thành phần → `/health/ready` báo lỗi và cảnh báo phát (AC-022).

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G3 (trước Sprint 4): OQ-002 (ngưỡng), bộ câu hỏi chuẩn đầy đủ. | Cổng G4 (cuối Sprint 4): tiêu chí launch LG-01..LG-11 đạt, hoặc có quyết định ngoại lệ bằng văn bản của sponsor.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
