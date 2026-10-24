# Spike T0-08 — Sinh câu trả lời có trích dẫn (Claude)

| Mục | Nội dung |
|---|---|
| Script | `evaluation/spikes/generate.py` (kết quả sẽ ghi vào `evaluation/spikes/results/generation.json`) |
| Dữ liệu | Bộ PDF tổng hợp, không nhạy cảm (`evaluation/spikes/corpus`) |
| Mô hình | `claude-opus-5-5`, SDK chính thức `anthropic` |
| Trạng thái | **Đã có mã và kiểm thử với phản hồi giả lập; CHƯA chạy với API thật — môi trường phát triển chưa có `ANTHROPIC_API_KEY`.** |

## Đã xác nhận (không cần khóa API)

Kiểm thử `backend/tests/unit/test_claude_adapter.py` (chạy trong CI) xác nhận adapter `app/adapters/claude_llm.py`:

| Điểm kiểm tra | Kết quả |
|---|---|
| Mỗi chunk là một khối `document` văn bản, `citations.enabled = true`, tiêu đề "tên tệp — trang N" | Đạt |
| Citation `document_index` → chỉ số chunk đầu vào → tài liệu và trang (qua `map_citations` ở `modules/qa/service.py`) | Đạt (phản hồi giả lập có nhiều khối `text`, khối `thinking` bị bỏ qua) |
| `stop_reason = "refusal"` được đọc **trước** nội dung → `refused`; `max_tokens` → lỗi | Đạt |
| Không đặt `thinking`, không prefill, không `output_config.format`; `effort` nằm trong `output_config` | Đạt |
| Chỉ dẫn hệ thống cố định đứng đầu, có `cache_control` | Đạt |
| Chuyển mô hình dự phòng phía máy chủ khi bị từ chối: beta `server-side-fallback-2026-07-01`, `fallbacks="default"` | Đạt (kiểm hình dạng yêu cầu) |
| Lỗi bắt theo thứ tự `RateLimitError` → `APIStatusError` → `APITimeoutError` → `APIConnectionError` | Có trong mã |
| Câu từ chối cố định → `not_found` (so khớp chính xác sau chuẩn hóa); có nội dung mà không có citation hợp lệ → `not_found` | Đạt (`test_qa_service.py`, `test_qa_flow.py`) |

## Còn phải chạy khi có khóa API (trước cổng G1)

```bash
ANTHROPIC_API_KEY=... python evaluation/spikes/generate.py --corpus evaluation/spikes/corpus --efforts low medium
```
Script đo và ghi:
- (a) tỷ lệ citation trỏ đúng tài liệu và trang mong đợi;
- (b) tỷ lệ câu ngoài phạm vi nhận đúng câu từ chối cố định;
- (c) so sánh `effort` `low` và `medium`: tỷ lệ đúng nguồn, độ trễ trung vị, token đầu ra;
- (d) `usage.cache_read_input_tokens` > 0 ở các lượt sau. Lưu ý: chỉ dẫn hệ thống hiện ngắn hơn ngưỡng tối thiểu để được lưu đệm, nên giá trị này có thể luôn bằng 0 — **không phải lỗi**; nếu cần tiết kiệm, cân nhắc lưu đệm phần đầu `messages` thay vì `system`.
- Chi phí ước tính mỗi câu hỏi (đơn giá truyền bằng tham số, mặc định $4 / $20 / $0,20 cho mỗi triệu token đầu vào / đầu ra / đọc từ bộ nhớ đệm) — đầu vào RSK-005.

Kiểm thử `test_real_api_cites_correct_chunk` (đánh dấu `needs_api_key`) tự chạy khi có khóa.

## Đề xuất tạm thời

- `ANSWER_EFFORT` khởi điểm **`medium`** (mặc định của `claude-opus-5-5`, đúng kế hoạch); so sánh với `low` bằng script trên và bộ đánh giá ở T4-01.
- Ước lượng chi phí trước khi đo: mỗi câu hỏi gửi ~8 chunk × ~500 token + câu hỏi + lịch sử ≈ 5–6 nghìn token đầu vào và vài trăm token đầu ra → khoảng **$0,03 mỗi câu hỏi** ở đơn giá trên (chưa tính token suy nghĩ thích ứng). Con số thật phải lấy từ lần chạy spike.
