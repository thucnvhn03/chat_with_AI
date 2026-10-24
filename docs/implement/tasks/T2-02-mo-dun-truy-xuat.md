# T2-02 · Mô-đun truy xuất

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 2 — Hỏi đáp có nguồn |
| Story | US-008 — Đặt câu hỏi bằng ngôn ngữ tự nhiên (P0); US-009 — Câu trả lời tổng hợp từ nhiều tài liệu (P0) |
| Loại việc | BE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T1-15, T2-01 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** `modules/retrieval/search.py`: `search(query_embedding, allowed_document_ids, top_k) -> list[RetrievedChunk]` thực hiện đúng truy vấn ở mục 5.2 của plan; **bộ lọc quyền nằm trong truy vấn**, chỉ lấy tài liệu `ready`. Giới hạn `MAX_CHUNKS_PER_DOC` nếu cấu hình bật. Bật `hnsw.iterative_scan` hoặc tăng `ef_search` khi lọc bằng danh sách tài liệu.
- **Xong khi:** kiểm thử tích hợp: (a) chunk của tài liệu không thuộc danh sách cho phép **không bao giờ** xuất hiện; (b) tài liệu `deleting` không xuất hiện; (c) với danh sách tài liệu nhỏ trong kho lớn, vẫn trả đủ `top_k` kết quả.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G1 (trước Sprint 2): OQ-006 (kịch bản A/B), OQ-005 sơ bộ, OQ-007. Chưa có thì dùng Kịch bản A với dữ liệu mẫu không nhạy cảm.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
