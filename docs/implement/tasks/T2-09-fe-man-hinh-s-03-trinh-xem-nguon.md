# T2-09 · FE: màn hình S-03 Trình xem nguồn

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 2 — Hỏi đáp có nguồn |
| Story | US-015 — Biết số trang của thông tin (P0) |
| Loại việc | FE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T2-06, T2-08 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** dựng S-03 theo `S-03-trinh-xem-nguon.html`, ảnh `s03-default`, `s03-deleted`: thanh công cụ "Trang N / M" và nút trang trước/sau; hiển thị văn bản trang, tô sáng `cited_text` (tìm trong văn bản trang, nếu không thấy thì không tô sáng, không báo lỗi); cột nguồn bên phải; trạng thái tài liệu đã bị xóa khi API trả 404. Cách hiển thị (văn bản trang hay trình xem PDF) theo DQ-005; mặc định văn bản trang.
- **Xong khi:** kiểm thử cho hai trạng thái; chuyển trang không tải lại toàn bộ ứng dụng; trang nêu trong chip khớp trang hiển thị.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G1 (trước Sprint 2): OQ-006 (kịch bản A/B), OQ-005 sơ bộ, OQ-007. Chưa có thì dùng Kịch bản A với dữ liệu mẫu không nhạy cảm.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
