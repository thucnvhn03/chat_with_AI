# T1-15 · Embedding và hoàn tất việc nạp

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 1 — Truy cập và nạp tài liệu |
| Story | US-001 — Tải một file PDF lên (P0); US-003 — Biết file nào tải thất bại (P0) |
| Loại việc | BE |
| Cỡ | L (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T1-12, T1-13, T1-14, T0-07 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:**
  1. `ports/ai.py`: `EmbeddingProvider`; `adapters/local_embedding.py`: nạp mô hình một lần khi khởi động, `embed(texts)` theo lô `EMBED_BATCH`, chuẩn hóa vector độ dài 1.
  2. Bộ xử lý `ingest`: đọc tệp từ kho → trích xuất → chunk → embedding → ghi **toàn bộ** chunk và cập nhật `status='ready'`, `page_count` trong một giao dịch (mục 5.1 bước 7). Nếu tài liệu đã chuyển `deleting` trong lúc xử lý, bỏ kết quả.
  3. Ánh xạ lỗi từ T1-13 sang `status='failed'` + `failure_reason`.
  4. Lỗi tạm thời → thử lại theo T1-12.
- **Xong khi:** kiểm thử tích hợp: PDF hợp lệ → `ready`, mọi chunk có `page` và vector đúng số chiều; PDF mã hóa → `failed/encrypted`; không có trường hợp tài liệu `ready` mà thiếu chunk (giao dịch nguyên tử).

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** không có

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
