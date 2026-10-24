# T0-07 · Spike embedding và truy xuất tiếng Việt

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 0 — Nền tảng và spike |
| Story | US-012 — Hỏi đáp bằng ngôn ngữ `[TBD: OQ-007]` (P0) |
| Loại việc | SPK |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T0-06 |
| Trạng thái | Blocked một phần (đo được multilingual-e5-small; bge-m3 chưa đo do thiếu đĩa trên máy phát triển) |

- **Làm gì:** nạp 1–2 mô hình embedding đa ngôn ngữ (ví dụ `BAAI/bge-m3`); cắt chunk 400/500/600 token trên cùng tập PDF; với 20–30 câu hỏi mẫu có đáp án đã biết, đo tỷ lệ chunk đúng nằm trong top-K (K = 4, 8, 12). Ghi số chiều vector và thời gian embedding mỗi chunk.
- **Sản phẩm:** `evaluation/spikes/retrieval.py` và `docs/implement/spike_embedding.md`.
- **Xong khi:** báo cáo chốt `EMBEDDING_MODEL`, `EMBEDDING_DIM`, giá trị khởi điểm cho `CHUNK_TOKENS` và `TOP_K`.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G0 (cuối Sprint 0): chốt bộ công nghệ, DQ-003, kết quả ba spike.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
