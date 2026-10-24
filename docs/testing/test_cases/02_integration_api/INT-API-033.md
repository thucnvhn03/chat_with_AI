# INT-API-033 — Bản ghi kiểm toán: lọc và phân trang

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Danh sách mới nhất trước, trang 50 bản ghi, con trỏ không trùng/không sót; lọc theo người dùng, tài liệu, ngày; không có nội dung câu hỏi |
| Truy vết | BR-023, AC-023, US-020, T3-04 |
| Ưu tiên / Loại | Trung bình / Dương |
| Tự động hóa | `test_admin_reports_health.py::test_audit_lists_one_record_per_question_without_content`, `test_audit_filters_and_cursor` |

**Các bước**
1. Tạo 60 bản ghi (xen kẽ "an"/"binh"; 10 bản ghi đầu có tài liệu X; 5 bản ghi lùi 10 ngày).
2. `GET /admin/audit`; theo `next_cursor` lấy trang 2.
3. Lọc `user=an`; `document={X}`; `from=to=hôm nay`; `to=7 ngày trước`; `document=khong-co-ten-nay`.
4. Với câu hỏi thật của "an": kiểm nội dung trang.

**Kết quả mong đợi**
- Trang 1: 50 + con trỏ; trang 2: 10, con trỏ null; 60 id khác nhau, giảm dần.
- 30; 10; 55; 5; 0.
- Mục có `user.login = "an"`, `documents = [{id, file_name}]`; không chứa câu hỏi hay "30 ngày".
