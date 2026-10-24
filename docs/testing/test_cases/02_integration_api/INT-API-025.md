# INT-API-025 — Lịch sử hội thoại và câu hỏi tiếp theo

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Câu hỏi tiếp theo dùng đại từ được trả lời đúng nhờ ghép câu trước; lịch sử đúng thứ tự; số lượt gửi mô hình theo `HISTORY_TURNS`; hội thoại mới không mang ngữ cảnh cũ; người khác không xem được |
| Truy vết | BR-008, AC-008, US-010, T3-05 |
| Ưu tiên / Loại | Trung bình / Dương |
| Tự động hóa | `test_qa_flow.py::test_history_and_follow_up_question`, `test_history_is_limited_to_history_turns`, `test_conversation_belongs_to_owner_only` |

**Các bước**
1. Hỏi "Hợp đồng có điều khoản phạt chậm thanh toán không?"; trong cùng hội thoại hỏi "Mức đó là bao nhiêu phần trăm mỗi ngày?".
2. `GET /conversations/{id}/messages`.
3. Hỏi trong hội thoại mới.
4. Với `HISTORY_TURNS = 1`: hỏi 3 câu liên tiếp trong một hội thoại.
5. Người dùng "binh" gọi GET/POST vào hội thoại của "an".

**Kết quả mong đợi**
- Bước 1: câu thứ hai không phải "không tìm thấy", citation trang 3; lịch sử gửi mô hình có 2 tin nhắn, bắt đầu bằng `user`.
- Bước 2: vai trò `user, assistant, user, assistant`; tin nhắn thứ 4 có citation trang 3.
- Bước 3: lịch sử gửi mô hình rỗng. Bước 4: lịch sử gửi mô hình có 2 tin nhắn. Bước 5: 404.
