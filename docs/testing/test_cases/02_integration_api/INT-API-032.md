# INT-API-032 — Đánh giá câu trả lời

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Lưu đánh giá, ghi đè được, hiện trong lịch sử; giá trị sai bị từ chối; người khác không đánh giá được |
| Truy vết | BR-017, AC-017, US-024, T4-03 |
| Ưu tiên / Loại | Thấp / Dương, âm |
| Tự động hóa | `test_qa_flow.py::test_feedback_is_saved_and_can_be_changed` |

**Các bước**
1. `PUT /messages/{id}/feedback` `{"value": "helpful"}` rồi `{"value": "not_helpful"}`.
2. `GET` lịch sử hội thoại.
3. Gửi `{"value": "tot"}`.
4. "binh" gửi `{"value": "helpful"}`.

**Kết quả mong đợi**
- 204, 204; bảng `feedback` có đúng 1 dòng giá trị `not_helpful`.
- Lịch sử: `feedback = "not_helpful"`. Bước 3: 400. Bước 4: 404.
