# Spike T0-06 — Trích xuất PDF

| Mục | Nội dung |
|---|---|
| Ngày chạy | 2026-10-22 |
| Script | `evaluation/spikes/extract.py` (kết quả thô: `evaluation/spikes/results/extract.json`) |
| Dữ liệu | Bộ PDF **tổng hợp, không nhạy cảm**, 22 tệp / 53 trang, sinh bằng `evaluation/spikes/make_corpus.py` (tất định, có đáp án) |
| Thư viện | `pypdf` (BSD) và `pdfplumber` (MIT); không thử PyMuPDF vì giấy phép AGPL (ADR-010) |

> **Giới hạn quan trọng.** Tập PDF mẫu thật của đội BD (DEP-001) chưa có. Bộ tổng hợp được dựng để mô phỏng các loại tài liệu BD hay gặp (hợp đồng nhiều trang, báo giá có bảng, đề xuất bố cục hai cột, tài liệu tiếng Anh, PDF có mật khẩu, PDF chụp/scan). Kết luận về **chọn thư viện** đứng vững; **tỷ lệ PDF "không có văn bản" trong thực tế chưa đo được** — phải chạy lại script với `--real-dir` khi có DEP-001 trước cổng G0.

## Kết quả

| Chỉ số | pypdf | pdfplumber |
|---|---|---|
| Tỷ lệ trang có văn bản (≥ 20 ký tự) | 92,5% (49/53) | 92,5% (49/53) |
| Độ giống văn bản gốc (trung bình / thấp nhất) | **0,934** / 0,450 | 0,889 / 0,351 |
| Giữ dấu tiếng Việt (tỷ lệ ký tự có dấu còn nguyên) | **100%** | **100%** |
| Bảng giá: dòng bảng còn nằm trên một dòng | 0/18 | **18/18** |
| Bố cục hai cột: câu chứa sự kiện còn liền mạch | **8/8** | 3/8 |
| Thời gian trích xuất mỗi trang (trung vị, CPU) | **31,6 ms** | 269 ms |
| PDF có mật khẩu | Phát hiện được (`FileNotDecryptedError`) | Báo lỗi chung (`PdfminerException`) |

4 trang không có văn bản đều thuộc 2 tệp "scan" (chỉ có hình) — đúng như thiết kế bộ dữ liệu.

**Quan sát chi tiết**
- **Bảng:** pypdf xuất mỗi ô trên một dòng nhưng **giữ đúng thứ tự theo hàng** (`Gói Tiêu chuẩn` → `52` → `12 tháng`). Khi cắt chunk, các ô của một hàng vẫn nằm cạnh nhau nên truy xuất và trích dẫn vẫn đúng; chỉ mất cấu trúc "một dòng". pdfplumber giữ nguyên dòng.
- **Hai cột:** pdfplumber đọc theo dòng ngang nên **trộn hai cột** (câu ở cột trái bị chèn nửa câu của cột phải) — với tài liệu dạng brochure/đề xuất, chunk sẽ chứa câu vô nghĩa và cited_text không khớp trang. pypdf đọc theo luồng nội dung nên giữ được từng cột.
- **Tiếng Việt:** cả hai giữ đủ dấu với phông nhúng có bảng ToUnicode; mô-đun `extract.py` chuẩn hóa NFC nên dạng tổ hợp và dựng sẵn về cùng một dạng (kiểm thử `test_vietnamese_text_is_nfc_and_keeps_diacritics`).
- **Hiệu năng:** pypdf nhanh hơn ~8,5 lần; với giới hạn 20 MB/tệp và vài trăm trang, nạp tài liệu bị chặn bởi embedding chứ không phải trích xuất.

## Kết luận

1. **Chọn `pypdf`** làm thư viện trích xuất mặc định (đã cài trong `app/modules/ingestion/extract.py`). Lý do: giữ bố cục nhiều cột, nhanh, phân biệt rõ PDF mã hóa với PDF hỏng, giấy phép BSD. **Xác nhận ADR-010.**
2. **Không dùng pdfplumber ở MVP.** Ghi nhận làm phương án bổ sung cho **trang có bảng** nếu bộ đánh giá cho thấy câu hỏi về bảng giá trả lời kém (ví dụ: chỉ dùng `pdfplumber.extract_tables()` cho trang có bảng, ghép vào văn bản pypdf).
3. **Giới hạn MVP đề xuất** (ghi vào cấu hình, chốt theo OQ-004 / OQ-007):
   - PDF dạng ảnh scan → `no_text` ("chưa hỗ trợ"), không OCR ở MVP (ADR-010, OQ-007).
   - PDF có mật khẩu mở → `encrypted`; PDF chỉ có mật khẩu chủ sở hữu (mở được) vẫn được nạp.
   - Tổng ký tự toàn tài liệu < `MIN_TEXT_CHARS` (20) → `no_text`.
4. **Việc còn lại trước G0:** chạy `python evaluation/spikes/extract.py --real-dir <thư mục DEP-001>` trên ≥ 20 PDF thật, ghi bổ sung vào bảng trên: tỷ lệ tệp "không có văn bản" (để xác nhận ADR-010 trên dữ liệu thật), các loại PDF kém (phông không có ToUnicode, văn bản dạng đường cong).
