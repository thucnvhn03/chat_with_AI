# T1-11 · Endpoint `POST /documents` (kiểm tra tệp)

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 1 — Truy cập và nạp tài liệu |
| Story | US-001 — Tải một file PDF lên (P0); US-002 — Tải nhiều PDF vào cùng một tập tài liệu (P0); US-003 — Biết file nào tải thất bại (P0) |
| Loại việc | BE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T1-04, T1-09, T1-10 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** theo `implement_plan.md` mục 5.1 phần "Trong `POST /documents`":
  1. Nhận nhiều tệp (multipart), xử lý **từng tệp độc lập**.
  2. Kiểm tra `MAX_FILE_BYTES` (`too_large`), 5 byte đầu `%PDF-` (`not_pdf`, không tin đuôi tệp hay `Content-Type`), `MAX_DOCS_PER_USER`.
  3. Tệp hợp lệ: lưu vào kho với khóa `documents/{owner_id}/{document_id}.pdf`; tạo `documents` ở trạng thái `processing`; thêm `jobs(kind='ingest')` **trong cùng giao dịch** với bản ghi tài liệu.
  4. Trả danh sách kết quả từng tệp `{id, file_name, status, failure_reason?}`.
  5. Phát sự kiện `document_upload_started`, `_succeeded`, `_failed` (nhóm lý do, không có nội dung).
- **Xong khi:** kiểm thử tích hợp: một yêu cầu gồm 1 PDF hợp lệ + 1 `.txt` đổi đuôi `.pdf` + 1 tệp vượt giới hạn → kết quả đúng cho từng tệp; tệp hợp lệ vẫn được nhận.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** không có

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
