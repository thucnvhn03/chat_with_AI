# T3-06 · Đo thời gian, hạn thời gian chờ và trạng thái chờ

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 3 — Xóa, phạm vi quyền, kiểm toán, hội thoại |
| Story | US-013 — Thời gian phản hồi (P1) |
| Loại việc | BE+FE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T2-05, T2-07 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:**
  - **BE:** span OpenTelemetry cho từng bước (nhúng câu hỏi, truy xuất, sinh); số liệu phân bố `answer_latency_seconds`; `ANSWER_TIMEOUT_S`. Endpoint SSE `POST /conversations/{id}/messages:stream` **chỉ làm nếu AQ-006 chọn hiển thị theo luồng**.
  - **FE:** chỉ báo chờ xuất hiện ≤ 300 ms sau khi gửi; nút Hủy (hủy yêu cầu phía trình duyệt, ảnh `s02-waiting`); thông báo khi quá thời gian kèm "Thử lại".
- **Xong khi:** đo được phân vị thời gian từng bước trên bộ câu hỏi chuẩn (AC-011, LG-05); kiểm thử giao diện cho chỉ báo chờ.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G2 (trước Sprint 3): OQ-003, OQ-012. Chưa có thì dùng giá trị tạm: chỉ tài liệu của chính mình; xóa ngay khi worker chạy; lưu bản ghi 365 ngày.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
