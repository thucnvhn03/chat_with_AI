# T2-08 · FE: thẻ câu trả lời, nguồn, "không tìm thấy"

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 2 — Hỏi đáp có nguồn |
| Story | US-011 — Báo rõ khi tài liệu không có thông tin (P0); US-014 — Biết câu trả lời lấy từ tài liệu nào (P0) |
| Loại việc | FE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T2-07 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** `AnswerCard` (C-11) với `SourceChip` (C-12) "tên tài liệu, tr.N" (chọn chip điều hướng S-03); `NotFoundNotice` (C-15) như `s02-default` kèm gợi ý. Phát `source_opened` khi mở nguồn. Nội dung câu trả lời được hiển thị **dưới dạng văn bản đã thoát ký tự** (không render HTML từ mô hình).
- **Xong khi:** kiểm thử: câu trả lời có nguồn hiển thị chip đúng; `not_found` hiển thị khối cảnh báo, không hiển thị chip; chuỗi chứa `<script>` hiển thị nguyên văn, không thực thi.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G1 (trước Sprint 2): OQ-006 (kịch bản A/B), OQ-005 sơ bộ, OQ-007. Chưa có thì dùng Kịch bản A với dữ liệu mẫu không nhạy cảm.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
