# Mẫu Báo cáo tổng kết kiểm thử

Theo IEEE 829-2008 (Master Test Report), giữ các mục quen thuộc của bản 1998 (variances, comprehensive assessment). Thay `<...>` bằng nội dung thật; bỏ hướng dẫn trong `_..._`. Không để trống mục — nếu không có gì, viết "Không có" và lý do.

```markdown
# BÁO CÁO TỔNG KẾT KIỂM THỬ — "CHAT VỚI TÀI LIỆU" (MVP)

| Mục | Nội dung |
|---|---|
| Mã tài liệu | CWD-TSR-<NNN> |
| Mốc | <Sprint N / Cổng G4 / đợt kiểm thử ...> |
| Kế hoạch tham chiếu | docs/testing/Master_Test_Plan.md (CWD-MTP-001) |
| Phiên bản mã | <commit ngắn> trên nhánh <nhánh> <(có thay đổi chưa commit) nếu có> |
| Môi trường | <Local Docker Compose / CI / Staging>, adapter AI <giả lập / Claude>, embedding <hash / bge-m3> |
| Thời gian kiểm thử | <từ ngày> – <đến ngày> |
| Người lập | <tên / vai trò> |
| Ngày lập | <YYYY-MM-DD> |

## 1. Tóm tắt

_3–6 câu cho sponsor: kết luận chung (Đủ điều kiện / Đủ điều kiện có điều kiện / Chưa đủ điều kiện), số ca đạt trên tổng, lỗi nghiêm trọng/cao còn mở, các LG chưa đạt và việc cần làm để đạt._

**Kết luận:** <...>

| Chỉ số | Giá trị |
|---|---|
| Ca kiểm thử đạt | <n> / 149 (<%>) |
| Không đạt | <n> |
| Bỏ qua / Chưa có kết quả | <n> / <n> |
| Thủ công chưa ghi nhận | <n> |
| Lỗi nghiêm trọng / cao còn mở | <n> / <n> |
| Tiêu chí launch đạt | <n> / 11 |

## 2. Phạm vi và hạng mục đã kiểm thử

_Tầng nào đã chạy, trên phiên bản nào; phạm vi khác Master Test Plan ở đâu._

## 3. Sai khác so với kế hoạch (Variances)

_Những gì khác Master Test Plan: ca không chạy và lý do, thay đổi môi trường (ví dụ dùng embedding giả lập vì thiếu tài nguyên), thay đổi ngưỡng, kết quả cũ hơn mã hiện tại._

| Sai khác | Lý do | Ảnh hưởng tới kết luận |
|---|---|---|

## 4. Kết quả theo tầng

| Tầng | Nguồn kết quả (thời điểm) | Tổng | Đạt | Lỗi | Bỏ qua |
|---|---|---|---|---|---|
| Backend (pytest) | | | | | |
| Frontend (Vitest) | | | | | |
| E2E (Playwright) | | | | | |
| Bộ đánh giá (công thức) | | | | | |

## 5. Kết quả theo nhóm ca kiểm thử

_Bảng "Trạng thái ca theo nhóm" từ summary.md._

## 6. Lỗi phát hiện

| Mã | Ca / kiểm thử | Mô tả | Mức độ (MTP 6.2) | Căn cứ mức độ | Trạng thái | Người xử lý |
|---|---|---|---|---|---|---|

## 7. Chất lượng câu trả lời (bộ đánh giá)

_Từ evaluation/reports. Nêu rõ cấu hình (embedding, adapter, bộ câu hỏi). Nếu dùng adapter/embedding giả lập: ghi "kiểm chứng luồng, không phải số liệu chất lượng"._

| Chỉ số | Giá trị | Ngưỡng | Kết luận |
|---|---|---|---|
| Đúng và có nguồn (MET-002) | | [TBD: OQ-002] | |
| Tỷ lệ bịa | | | |
| Độ phủ nguồn | | | |
| Câu hỏi tiếp theo đúng | | | |
| Đúng trang | | 100% | |
| Độ trễ p50/p90/p95 | | | |

## 8. Đánh giá theo tiêu chí launch (LG-01..LG-11)

| LG | Tiêu chí | Kết luận | Bằng chứng | Còn thiếu / việc cần làm | Người chịu trách nhiệm |
|---|---|---|---|---|---|
| LG-01 | 100% AC của story P0 đạt | | | | |
| … | | | | | |
| LG-11 | OQ-001..OQ-007 đã chốt | | | | |

## 9. Đánh giá tổng thể (Comprehensive assessment)

_Độ phủ: số BR/AC có ca đạt (Phụ lục 1 của MTP). Kiểm thử chưa gắn với ca nào (lỗ hổng truy vết). Mức độ tin cậy của kết quả: môi trường, adapter giả lập, phần thủ công._

## 10. Rủi ro còn lại

| Rủi ro | Mức | Giảm thiểu / theo dõi |
|---|---|---|

## 11. Khuyến nghị

_Việc cụ thể, có người và hạn, xếp theo thứ tự ảnh hưởng tới quyết định phát hành._

## 12. Hoạt động kiểm thử đã thực hiện

| Hoạt động | Thời điểm | Người thực hiện | Ghi chú |
|---|---|---|---|

## 13. Phê duyệt

| Vai trò | Họ tên | Quyết định | Ngày |
|---|---|---|---|
| Trưởng nhóm QA | | | |
| Chủ sản phẩm | | | |
| Sponsor | | | |
| Bảo mật | | | |

## Phụ lục A — Trạng thái từng ca

_Bảng "Từng ca" từ summary.md._

## Phụ lục B — Lịch sử phiên bản

| Phiên bản | Ngày | Mốc | Thay đổi chính |
|---|---|---|---|
```
