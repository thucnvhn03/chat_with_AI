# Spike T0-07 — Embedding và truy xuất tiếng Việt

| Mục | Nội dung |
|---|---|
| Ngày chạy | 2026-10-23 |
| Script | `evaluation/spikes/retrieval.py` (kết quả thô: `evaluation/spikes/results/retrieval.json`) |
| Dữ liệu | Bộ PDF tổng hợp (`evaluation/spikes/corpus`): 19 tệp đọc được, 49 chunk; 112 câu hỏi có đáp án đã biết (tài liệu + trang), sinh từ `ground_truth.json` |
| Môi trường | CPU trong Docker Desktop (Windows), không GPU |

## Đã đo

| Mô hình | Số chiều | CHUNK_TOKENS | recall@4 | recall@8 | recall@12 | MRR | Thời gian nhúng / chunk (CPU) |
|---|---|---|---|---|---|---|---|
| `intfloat/multilingual-e5-small` | 384 | 400 | 100% | 100% | 100% | 0,987 | ~1,2–2,7 s* |
| `intfloat/multilingual-e5-small` | 384 | 500 | 100% | 100% | 100% | 0,987 | |
| `intfloat/multilingual-e5-small` | 384 | 600 | 100% | 100% | 100% | 0,987 | |
| `BAAI/bge-m3` | 1024 | 400 / 500 / 600 | **chưa đo** | | | | |

\* Thời gian đo trên máy phát triển đang tải nặng (Docker Desktop, nhiều dịch vụ khác cùng chạy); không dùng để ước lượng năng lực máy chủ.

**Điểm tương đồng câu hỏi ↔ chunk tốt nhất (e5-small, CHUNK_TOKENS = 500):**

| | Thấp nhất | P10 | Trung vị | Cao nhất |
|---|---|---|---|---|
| Câu trong phạm vi | 0,859 | 0,876 | 0,901 | |
| Câu ngoài phạm vi | | | 0,851 | **0,884** |

## Nhận xét

1. **Bộ tổng hợp quá dễ cho truy xuất.** Mỗi trang ~400 token nên vừa một chunk ở cả ba kích thước — so sánh 400/500/600 không phân biệt được; các câu hỏi chứa tên công ty/dịch vụ duy nhất nên top-1 gần như luôn đúng. Kết quả chỉ chứng minh: trích xuất pypdf + chunk theo trang + mô hình đa ngôn ngữ hoạt động đúng với tiếng Việt có dấu (MRR 0,987; 3 câu đúng trang ở hạng 2).
2. **Ngưỡng `MIN_RELEVANCE_SCORE` không thể tách câu ngoài phạm vi bằng điểm truy xuất với e5-small**: câu ngoài phạm vi cao nhất (0,884) vượt câu trong phạm vi thấp nhất (0,859) do điểm của họ E5 bị nén trong khoảng hẹp. Hệ quả cho thiết kế: lớp từ chối 1 chỉ nên lọc trường hợp rõ ràng (đặt ngưỡng thấp), còn việc chống bịa dựa vào lớp 2 (câu từ chối cố định của mô hình) và lớp 3 (không có citation hợp lệ) — đúng như ADR-011. Ngưỡng phải hiệu chỉnh lại theo mô hình được chốt.
3. **`BAAI/bge-m3` chưa chạy được**: tải mô hình (~2,3 GB) làm đầy ổ đĩa hệ thống của máy phát triển (Docker Desktop lưu dữ liệu trên ổ C: chỉ còn ~4 GB trống) và làm Docker Desktop dừng. Cần chạy trên máy CI/máy chủ kiểm thử:
   ```bash
   docker compose -f deploy/docker-compose.yml run --rm backend \
     python /repo/evaluation/spikes/retrieval.py --models BAAI/bge-m3 intfloat/multilingual-e5-small
   ```
   (hoặc chạy trực tiếp với Python 3.12 + `pip install -e "backend[embedding]"`).

## Kết luận và giá trị khởi điểm

| Biến | Giá trị khởi điểm | Trạng thái |
|---|---|---|
| `EMBEDDING_MODEL` | `BAAI/bge-m3` | **Đề xuất, chưa đo** — giữ theo kế hoạch vì hỗ trợ tiếng Việt, ngữ cảnh 8192 token và giấy phép MIT; phương án thay đã đo được: `intfloat/multilingual-e5-small` (384 chiều, nhẹ ~470 MB, cũng 100% recall@4 trên bộ tổng hợp) |
| `EMBEDDING_DIM` | 1024 (bge-m3) — đổi thành 384 nếu chọn e5-small (cần migration mới cho cột `vector`) | Chốt ở G0 |
| `CHUNK_TOKENS` / `CHUNK_OVERLAP` | 500 / 80 | Chưa phân biệt được trên bộ tổng hợp; hiệu chỉnh ở T4-01 trên tài liệu thật dài hơn |
| `TOP_K` | 8 | recall@4 đã đạt 100% trên bộ tổng hợp; giữ 8 để phủ câu hỏi nhiều tài liệu (US-009) |
| `MIN_RELEVANCE_SCORE` | 0,35 với bge-m3 [chưa đo]; nếu dùng e5-small: ≤ 0,80 | Hiệu chỉnh bằng bộ đánh giá (AQ-002) |

Adapter `app/adapters/local_embedding.py` hỗ trợ cả hai mô hình; với họ E5 cần thêm tiền tố `query:`/`passage:` (chưa cài trong adapter — chỉ thêm nếu chốt dùng E5).

**Việc còn lại trước G0:** chạy lại script với `BAAI/bge-m3` trên ≥ 20 PDF thật (DEP-001) và 20–30 câu hỏi do business owner cung cấp, ghi bổ sung bảng trên; chốt `EMBEDDING_MODEL`/`EMBEDDING_DIM`.
