# Nhật ký hiệu chỉnh chất lượng (T4-01, US-016)

Quy tắc: **mỗi lần chỉ đổi một yếu tố**, chạy `evaluation/run_eval.py` trên cùng bộ câu hỏi, ghi kết quả vào bảng dưới cùng phiên bản mã (`git_revision` trong báo cáo) và chi phí lần chạy. Kết quả chấm tự động chỉ được dùng cho cổng launch sau khi đối chiếu chấm tay trên mẫu 20% (`--review-sample 0.2`).

Thứ tự hiệu chỉnh: `CHUNK_TOKENS` → `CHUNK_OVERLAP` → `TOP_K` → `MAX_CHUNKS_PER_DOC` → `MIN_RELEVANCE_SCORE` → `ANSWER_EFFORT` (`low` so với `medium`) → chỉ dẫn hệ thống.

Ngưỡng nghiệm thu: MET-002 ≥ [TBD: OQ-002], tỷ lệ bịa ≤ [TBD: OQ-002], đúng trang 100%, theo từng ngôn ngữ đã chốt (OQ-007).

## Lần chạy

| # | Ngày | Bộ câu hỏi | Cấu hình (chỉ ghi yếu tố đổi) | Embedding / sinh | MET-002 | Bịa | Phủ nguồn | Hỏi tiếp | Đúng trang | p90 (ms) | Chi phí | Báo cáo | Ghi chú |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 2026-10-22 | `v1.jsonl` (59 câu) | — | bộ gọi giả (`--fake`) | 100% | 0% | 100% | 100% | 100% | — | $0 | — | Chỉ kiểm khung đánh giá chạy đủ, không phải số liệu chất lượng |
| 1 | 2026-10-23 | `v1.jsonl` (59 câu) | cấu hình mặc định | embedding giả lập (hash) + adapter sinh giả (fake), qua API thật | 70,8% | 75,0% | 0% | 58,3% | 100% (56 citation) | 319 | $0 | `evaluation/reports/v1-20261023T130536Z.md` | **Kiểm chứng luồng đánh giá đầu-cuối**, không phải số liệu chất lượng: adapter giả luôn trích một đoạn nên tỷ lệ bịa và độ phủ nhiều tài liệu kém theo thiết kế. Đường cơ sở thật cần `EMBEDDING_PROVIDER=local` + `ANSWER_PROVIDER=claude` |

Các dòng tiếp theo được thêm khi chạy với hệ thống thật (xem `docs/implement/launch_checklist.md` mục LG-02..LG-05 cho trạng thái hiện tại).

## Cấu hình đóng băng

Chưa có — chờ bộ câu hỏi chuẩn được business owner duyệt (G3) và khóa API cho môi trường đánh giá.

## Ghi nhận cần đưa vào lần hiệu chỉnh đầu tiên

- **Câu hỏi ngoài phạm vi hỏi tiếp trong cùng hội thoại** (phát hiện ở E2E 2026-10-23): truy vấn truy xuất ghép câu hỏi hiện tại với câu hỏi trước (implement_plan.md mục 5.3 bước 4), nên một câu ngoài phạm vi hỏi ngay sau câu trong phạm vi vẫn truy xuất được các chunk của câu trước và vượt lớp từ chối 1. Khi đó chỉ còn lớp 2 (mô hình trả câu từ chối cố định) và lớp 3 (không có citation hợp lệ) chặn câu trả lời bịa. Cần thêm vào bộ câu hỏi chuẩn nhóm "follow_up ngoài phạm vi" và đo tỷ lệ bịa của nhóm này; nếu vượt ngưỡng, cân nhắc: chỉ ghép câu trước khi câu hiện tại ngắn/có đại từ, hoặc truy xuất hai lần (riêng câu hiện tại và câu ghép) và lấy điểm của truy vấn riêng cho lớp 1.
