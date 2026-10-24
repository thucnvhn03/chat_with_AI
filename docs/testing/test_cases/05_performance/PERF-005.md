# PERF-005 — Phản hồi giao diện

Nhóm: [05 — Ca kiểm thử hiệu năng (PERF-001..PERF-006)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Chỉ báo "Đang xử lý câu hỏi…" hiện ≤ 300 ms sau khi gửi; danh sách 200 tài liệu không giật |
| Truy vết | US-013, US-005, T3-06, T1-18 |
| Ưu tiên | Trung bình |
| Môi trường | Cấu hình E2E (adapter giả lập chậm hoặc chặn phản hồi) |
| Tự động hóa | Vitest `chat.test.tsx` (chỉ báo chờ xuất hiện trong 300 ms), `documents.test.tsx` (200 tài liệu) |

**Các bước**
1. Gửi câu hỏi trong khi phản hồi API bị giữ lại; đo thời điểm chỉ báo xuất hiện.
2. Hiển thị 200 tài liệu; cuộn danh sách trong Chromium, ghi Performance trace.

**Kết quả mong đợi**
- Chỉ báo xuất hiện ≤ 300 ms; nút "Hủy" dùng được.
- Danh sách dựng xong; không có khung hình dài > 50 ms khi cuộn (`content-visibility: auto` đã bật).
