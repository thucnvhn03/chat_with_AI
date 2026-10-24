# T2-13 · Bộ câu hỏi chuẩn phiên bản 1 và đường cơ sở

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 2 — Hỏi đáp có nguồn |
| Story | US-008 — Đặt câu hỏi bằng ngôn ngữ tự nhiên (P0); US-009 — Câu trả lời tổng hợp từ nhiều tài liệu (P0); US-011 — Báo rõ khi tài liệu không có thông tin (P0); US-012 — Hỏi đáp bằng ngôn ngữ `[TBD: OQ-007]` (P0); US-016 — Chất lượng câu trả lời đạt ngưỡng (P0) |
| Loại việc | QA |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T0-09, T2-05; tập PDF và câu hỏi từ business owner (DEP-001, ASM-005) |
| Trạng thái | Blocked một phần (v1.jsonl bản nháp 59 câu + chạy luồng qua API; chờ business owner duyệt và đường cơ sở với AI thật) |

- **Làm gì:** cùng business owner tạo `evaluation/datasets/v1.jsonl` với các loại `in_scope`, `out_of_scope`, `multi_doc` (≥ 10 câu mỗi loại [Đề xuất]); nối `run_eval.py` với API thật; chạy và lưu báo cáo đường cơ sở cùng phiên bản mã và cấu hình.
- **Xong khi:** có báo cáo đường cơ sở với MET-002, tỷ lệ bịa, độ phủ nguồn, độ trễ; business owner xác nhận đáp án mẫu.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G1 (trước Sprint 2): OQ-006 (kịch bản A/B), OQ-005 sơ bộ, OQ-007. Chưa có thì dùng Kịch bản A với dữ liệu mẫu không nhạy cảm.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
