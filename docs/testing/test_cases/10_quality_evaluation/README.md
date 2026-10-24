# 10 — Ca kiểm thử chất lượng câu trả lời (QE-001..QE-008)

Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md) mục 6.1.11; implement_plan.md mục 9.4. Công cụ: `evaluation/run_eval.py`, `evaluation/upload_corpus.py`. Hướng dẫn: `evaluation/README.md`.

**Môi trường:** Test/Staging với `EMBEDDING_PROVIDER=local` (`BAAI/bge-m3`) và `ANSWER_PROVIDER=claude` (`claude-opus-5-5`). Máy ≥ 16 GB RAM (kế hoạch mục 11.3). Khóa API lấy từ kho bí mật, không commit.

**Dữ liệu:** bộ câu hỏi chuẩn đã được business owner duyệt và tập PDF thật (DEP-001, ASM-005). Trước khi có: `evaluation/datasets/v1.jsonl` (59 câu, bản nháp) trên bộ PDF tổng hợp `evaluation/spikes/corpus` — chỉ dùng để chạy thử, **không** dùng cho cổng launch.

**Điều kiện trước chung:**
1. Tạo tài khoản BD dành cho đánh giá; đặt `EVAL_LOGIN`, `EVAL_PASSWORD`.
2. `python evaluation/upload_corpus.py --api <url> --dir <thư mục PDF>`; mọi tệp có văn bản đạt `ready`.
3. Ghi lại cấu hình đang đánh giá (`CHUNK_TOKENS`, `CHUNK_OVERLAP`, `TOP_K`, `MAX_CHUNKS_PER_DOC`, `MIN_RELEVANCE_SCORE`, `ANSWER_EFFORT`, phiên bản chỉ dẫn hệ thống).

**Lệnh chạy chung:**
```bash
python evaluation/run_eval.py --dataset <bộ câu hỏi> --api <url> \
    --config-note "<cấu hình>" --cost-usd <chi phí> --review-sample 0.2 --out evaluation/reports
```

**Ghi kết quả:** báo cáo `.json` + `.md` lưu cùng phiên bản mã; một dòng trong `docs/implement/tuning_log.md`; chi phí lần chạy (RSK-005).

## Danh sách ca (8)

| Mã ca | Tên |
|---|---|
| [QE-001](QE-001.md) | Đúng và có nguồn (MET-002) |
| [QE-002](QE-002.md) | Tỷ lệ bịa |
| [QE-003](QE-003.md) | Ngoài phạm vi hỏi tiếp trong cùng hội thoại |
| [QE-004](QE-004.md) | Độ phủ nguồn khi hỏi nhiều tài liệu |
| [QE-005](QE-005.md) | Câu hỏi tiếp theo |
| [QE-006](QE-006.md) | Đúng trang và câu trả lời có nội dung có nguồn |
| [QE-007](QE-007.md) | Kết quả theo ngôn ngữ |
| [QE-008](QE-008.md) | Đối chiếu chấm tự động với chấm tay |
