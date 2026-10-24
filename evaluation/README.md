# Bộ đánh giá chất lượng (M-12, US-016)

Đo chất lượng hỏi đáp trên bộ câu hỏi chuẩn theo `docs/implement/implement_plan.md` mục 9.4.

## Cấu trúc

| Đường dẫn | Nội dung |
|---|---|
| `run_eval.py` | Đọc `datasets/*.jsonl`, gọi `ask(question, history)`, tính chỉ số, ghi báo cáo JSON + Markdown |
| `datasets/sample.jsonl` | 5 câu mẫu để chạy thử khung |
| `datasets/v1.jsonl` | Bộ câu hỏi chuẩn v1 — **bản nháp** trên bộ PDF tổng hợp, 59 câu (in_scope 24, out_of_scope 12, multi_doc 11, follow_up 12). Chờ business owner duyệt (DEP-001, ASM-005) |
| `datasets/build_v1.py` | Sinh lại `v1.jsonl` từ `spikes/corpus/ground_truth.json` |
| `upload_corpus.py` | Tải một thư mục PDF lên hệ thống qua API và chờ xử lý xong |
| `spikes/` | Spike T0-06 (`extract.py`), T0-07 (`retrieval.py`), T0-08 (`generate.py`), bộ PDF tổng hợp (`make_corpus.py`) |
| `tests/` | Kiểm thử đơn vị cho từng công thức chỉ số |
| `reports/` | Báo cáo các lần chạy (lưu cùng phiên bản mã) |

**Không commit tài liệu thật** nếu nhạy cảm (OQ-005). Bộ PDF tổng hợp sinh lại được: `python evaluation/spikes/make_corpus.py` (cần phông DejaVu, có trong ảnh dev).

## Định dạng câu hỏi

```json
{"id": "q001", "lang": "vi", "type": "in_scope", "question": "...", "expected_answer": "...", "expected_keywords": ["30 ngày"], "expected_sources": [{"document": "HopDong_A.pdf", "page": 5}]}
{"id": "q101", "lang": "vi", "type": "out_of_scope", "question": "..."}
{"id": "q201", "lang": "vi", "type": "multi_doc", "question": "...", "expected_sources": [{"document": "A.pdf", "page": 5}, {"document": "B.pdf", "page": 2}]}
{"id": "q301", "lang": "vi", "type": "follow_up", "history": ["..."], "question": "...", "expected_answer": "..."}
```
Dòng bắt đầu bằng `//` là ghi chú.

## Chạy

```bash
# Chạy thử với bộ gọi giả (không cần AI thật)
python evaluation/run_eval.py --dataset evaluation/datasets/sample.jsonl --fake

# Với hệ thống thật (tài khoản BD đã có tài liệu của bộ câu hỏi)
export EVAL_LOGIN=eval.bd EVAL_PASSWORD=...
python evaluation/upload_corpus.py --api http://localhost:8000 --dir evaluation/spikes/corpus
python evaluation/run_eval.py --dataset evaluation/datasets/v1.jsonl --api http://localhost:8000 \
    --config-note "CHUNK_TOKENS=500 TOP_K=8 MIN_RELEVANCE_SCORE=0.35 ANSWER_EFFORT=medium" \
    --review-sample 0.2 --out evaluation/reports
```

## Chỉ số

| Chỉ số | Cách tính | Tiêu chí |
|---|---|---|
| Đúng và có nguồn (MET-002) | Câu `in_scope` trả lời đúng **và** có ≥ 1 nguồn khớp tài liệu + trang mong đợi ÷ số câu `in_scope` | ≥ [TBD: OQ-002] (LG-02) |
| Tỷ lệ bịa | Câu `out_of_scope` nhận câu trả lời có nội dung ÷ số câu `out_of_scope` | ≤ [TBD: OQ-002] (LG-03) |
| Độ phủ nguồn | Câu `multi_doc` có nguồn từ tất cả tài liệu mong đợi ÷ số câu `multi_doc` | Báo cáo (AC-007) |
| Câu hỏi tiếp theo đúng | Câu `follow_up` trả lời đúng ÷ số câu `follow_up` | Báo cáo (AC-008) |
| Đúng trang | Citation có `cited_text` nằm trong văn bản trang được nêu ÷ số citation kiểm tra được | 100% (LG-04) |
| Câu trả lời có nội dung có nguồn | ÷ số câu trả lời có nội dung | 100% (BR-012) |
| Độ trễ | p50 / p90 / p95 / max | ≤ [TBD: OQ-002] (LG-05) |

Báo cáo tách theo ngôn ngữ (`lang`) khi có nhiều ngôn ngữ (US-012).

**Chấm "đúng"** tự động: mọi `expected_keywords` có trong câu trả lời; nếu không có từ khóa thì ≥ 60% từ nội dung của `expected_answer`. Trước khi dùng cho cổng launch phải đối chiếu với **chấm tay** trên mẫu ngẫu nhiên 20% (`--review-sample 0.2` xuất tệp CSV có cột `human_correct` để điền).

**Chi phí:** mỗi lần chạy với adapter thật tốn phí dịch vụ AI; ghi bằng `--cost-usd` để theo dõi RSK-005.

## Kiểm thử

```bash
cd evaluation && pytest -q
```
