# T0-09 · Khung bộ đánh giá

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 0 — Nền tảng và spike |
| Story | US-016 — Chất lượng câu trả lời đạt ngưỡng (P0) |
| Loại việc | QA |
| Cỡ | S (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T0-01 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** `evaluation/run_eval.py` đọc `datasets/*.jsonl` (định dạng ở `implement_plan.md` mục 9.4), gọi một hàm `ask(question, history)` trừu tượng, tính các chỉ số mục 9.4 và ghi báo cáo JSON + Markdown. Kèm 5 câu mẫu và bộ gọi giả để chạy thử không cần AI thật.
- **Sản phẩm:** `evaluation/run_eval.py`, `evaluation/datasets/sample.jsonl`, `evaluation/README.md`.
- **Xong khi:** chạy với bộ gọi giả cho ra báo cáo có đủ các chỉ số; kiểm thử đơn vị cho từng công thức chỉ số.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G0 (cuối Sprint 0): chốt bộ công nghệ, DQ-003, kết quả ba spike.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
