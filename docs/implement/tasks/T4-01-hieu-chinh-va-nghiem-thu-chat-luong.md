# T4-01 · Hiệu chỉnh và nghiệm thu chất lượng

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 4 — Chất lượng, đo lường, sẵn sàng phát hành |
| Story | US-012 — Hỏi đáp bằng ngôn ngữ `[TBD: OQ-007]` (P0); US-016 — Chất lượng câu trả lời đạt ngưỡng (P0) |
| Loại việc | QA+BE |
| Cỡ | L (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T2-13, T3-05; G3 |
| Trạng thái | Blocked (chờ G3: OQ-002, bộ câu hỏi chuẩn duyệt, khóa API) |

- **Làm gì:**
  1. Mở rộng bộ câu hỏi chuẩn với business owner (đủ loại: `in_scope`, `out_of_scope`, `multi_doc`, `follow_up`, theo từng ngôn ngữ đã chốt).
  2. Hiệu chỉnh lần lượt: `CHUNK_TOKENS`, `CHUNK_OVERLAP`, `TOP_K`, `MAX_CHUNKS_PER_DOC`, `MIN_RELEVANCE_SCORE`, `ANSWER_EFFORT` (so `low` với `medium`), chỉ dẫn hệ thống. **Mỗi lần chỉ đổi một yếu tố**, chạy `run_eval.py`, ghi kết quả vào `docs/implement/tuning_log.md`.
  3. Chấm tay một mẫu 20% để đối chiếu với giám khảo tự động trước khi dùng kết quả tự động.
  4. Đóng băng cấu hình đạt ngưỡng; ghi cấu hình và chi phí mỗi lần chạy.
- **Xong khi:** báo cáo cuối đạt MET-002 ≥ ngưỡng, tỷ lệ bịa ≤ ngưỡng, đúng trang 100%, theo từng ngôn ngữ (AC-009, AC-010, AC-013, LG-02, LG-03, LG-04).

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G3 (trước Sprint 4): OQ-002 (ngưỡng), bộ câu hỏi chuẩn đầy đủ. | Cổng G4 (cuối Sprint 4): tiêu chí launch LG-01..LG-11 đạt, hoặc có quyết định ngoại lệ bằng văn bản của sponsor.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
