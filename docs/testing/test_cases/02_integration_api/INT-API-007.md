# INT-API-007 — Tải nhiều tệp, mỗi tệp xét độc lập

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Một yêu cầu gồm tệp hợp lệ, tệp không phải PDF và tệp quá lớn: mỗi tệp có kết quả riêng, tệp hợp lệ vẫn được nhận |
| Truy vết | BR-002, BR-003, AC-002, AC-003, US-002, US-003, T1-11 |
| Ưu tiên / Loại | Cao / Dương, âm, biên |
| Điều kiện trước | `MAX_FILE_BYTES = 200000` |
| Dữ liệu | `hop-le.pdf` (HĐ-3T); `ghi-chu.pdf` (nội dung văn bản thường); `qua-lon.pdf` (HĐ-3T + 250.000 byte đệm) |
| Tự động hóa | `test_ingestion_flow.py::test_mixed_upload_each_file_judged_independently` |

**Các bước**
1. `POST /documents` multipart với 3 tệp.
2. Chạy worker tới khi hết việc.
3. `GET /documents`.

**Kết quả mong đợi**
- Bước 1: 200, kết quả theo thứ tự: (`hop-le.pdf`, `processing`, null), (`ghi-chu.pdf`, `failed`, `not_pdf`), (`qua-lon.pdf`, `failed`, `too_large`).
- Bước 3: chỉ có `hop-le.pdf` ở trạng thái `ready`.
