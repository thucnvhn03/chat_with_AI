# T0-03 · Pipeline CI

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 0 — Nền tảng và spike |
| Story | Nền tảng / nghiệm thu (không gắn riêng một story) |
| Loại việc | OPS |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T0-01 |
| Trạng thái | Review (tệp CI xong; lint đỏ/xanh đã kiểm cục bộ; chưa chạy trên GitHub vì chưa đẩy mã) |

- **Làm gì:** pipeline có các bước: lint, kiểm tra kiểu, import-linter, unit, tích hợp (testcontainers), build ảnh Docker (`implement_plan.md` mục 10.4, bước 1–3). Công cụ CI theo AQ-004; nếu chưa chốt, dùng GitHub Actions.
- **Sản phẩm:** tệp cấu hình CI.
- **Xong khi:** pull request thử với một lỗi lint cố ý làm CI đỏ; sửa lỗi thì xanh.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G0 (cuối Sprint 0): chốt bộ công nghệ, DQ-003, kết quả ba spike.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
