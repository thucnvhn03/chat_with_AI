# T3-05 · Hội thoại: lịch sử và câu hỏi tiếp theo

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 3 — Xóa, phạm vi quyền, kiểm toán, hội thoại |
| Story | US-010 — Hỏi tiếp trong cùng hội thoại (P1) |
| Loại việc | BE+FE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T2-05, T2-08 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:**
  - **BE:** đưa `HISTORY_TURNS` lượt gần nhất vào `messages` của lời gọi mô hình; truy vấn truy xuất ghép câu hỏi hiện tại với câu hỏi người dùng ở lượt trước; `GET /conversations/{id}/messages`.
  - **FE:** hiển thị chuỗi hỏi đáp; nút "Hội thoại mới". Lưu hội thoại giữa các phiên theo PQ-004; mặc định chỉ trong phiên.
- **Xong khi:** bộ đánh giá có nhóm `follow_up` (≥ 10 câu) và kết quả được báo cáo (AC-008); hội thoại mới không mang ngữ cảnh cũ.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G2 (trước Sprint 3): OQ-003, OQ-012. Chưa có thì dùng giá trị tạm: chỉ tài liệu của chính mình; xóa ngay khi worker chạy; lưu bản ghi 365 ngày.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
