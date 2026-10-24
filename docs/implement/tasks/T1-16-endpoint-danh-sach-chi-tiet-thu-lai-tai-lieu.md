# T1-16 · Endpoint danh sách, chi tiết, thử lại tài liệu

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 1 — Truy cập và nạp tài liệu |
| Story | US-003 — Biết file nào tải thất bại (P0); US-005 — Xem danh sách tài liệu đã tải (P1) |
| Loại việc | BE |
| Cỡ | S (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T1-11, T1-15 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** `GET /documents`, `GET /documents/{id}`, `POST /documents/{id}/retry` (chỉ khi `failed`; đặt `processing` và thêm việc mới). Chỉ trả tài liệu của người dùng (tạm thời `owner_id = user`; hàm `allowed_document_ids` đầy đủ ở T3-03); không trả `deleting`/`deleted`. Tài liệu của người khác → 404.
- **Xong khi:** kiểm thử: người dùng A không thấy và không gọi được tài liệu của B (404); thử lại chỉ chấp nhận khi `failed`.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** không có

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
