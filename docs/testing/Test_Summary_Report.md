# BÁO CÁO TỔNG KẾT KIỂM THỬ — "CHAT VỚI TÀI LIỆU" (MVP)

| Mục | Nội dung |
|---|---|
| Mã tài liệu | CWD-TSR-001 |
| Mốc | Đợt kiểm thử trước cổng G4 (phát hành) — lần 1 |
| Kế hoạch tham chiếu | [Master_Test_Plan.md](Master_Test_Plan.md) (CWD-MTP-001); ca kiểm thử: [test_cases/](test_cases/README.md) |
| Phiên bản mã | `019fdc6` trên nhánh `main` (chỉ có thay đổi chưa commit ở tài liệu và skill, không đổi mã ứng dụng) |
| Môi trường | Máy phát triển Windows 10, 7,9 GB RAM; Node 24; **không chạy Docker** (máy chỉ còn 1,6 GB RAM trống, từng bị reset khi chạy Docker nặng) |
| Thời gian kiểm thử | 2026-10-28 (Vitest); kết quả tham khảo từ 2026-10-23 |
| Người lập | QA (Claude Code, theo yêu cầu của chủ dự án) |
| Ngày lập | 2026-10-28 |

## 1. Tóm tắt

**Kết luận: Chưa đủ điều kiện phát hành.**

Lần này chỉ chạy được tầng giao diện (Vitest): **79/79 kiểm thử đạt**, không có lỗi. Kết quả đó phủ trực tiếp **9/149 ca**. **108 ca** có kiểm thử tự động nhưng chưa có kết quả, vì backend và E2E cần Docker mà máy không đủ RAM. **32 ca** thủ công chưa được thực hiện. Không ca nào không đạt.

Ngoài phần thiếu kết quả, có 6 tiêu chí launch chưa thể đạt bằng kiểm thử: ngưỡng chất lượng chưa chốt (OQ-002), chưa có PDF thật và bộ câu hỏi đã duyệt, chưa có khóa API Claude, chưa có xác nhận bảo mật, các OQ chưa chốt.

Để kết luận được, cần: (1) chạy backend và E2E trên máy ≥ 16 GB RAM hoặc trên CI; (2) business owner cung cấp dữ liệu thật; (3) sponsor chốt OQ-001..OQ-007.

| Chỉ số | Giá trị |
|---|---|
| Ca kiểm thử đạt | 9 / 149 (6%) |
| Không đạt | 0 |
| Bỏ qua / Chưa có kết quả | 0 / 108 |
| Thủ công chưa ghi nhận | 32 |
| Lỗi nghiêm trọng / cao còn mở | 0 / 0 đã biết (chưa chạy lại backend, E2E nên chưa xác nhận) |
| Tiêu chí launch đạt | 0 / 11 (3 không đạt, 8 chưa kết luận) |

## 2. Phạm vi và hạng mục đã kiểm thử

| Tầng | Chạy lần này? | Ghi chú |
|---|---|---|
| Frontend — Vitest + Testing Library + axe-core (jsdom) | **Có** | `npx vitest run`, JUnit tại `test-results/frontend-vitest.xml` |
| Backend — đơn vị, tích hợp, bảo mật (pytest, PostgreSQL + S3 thật) | Không | Cần Docker |
| E2E — Playwright + axe | Không | Cần dựng toàn bộ stack Docker |
| Bộ đánh giá — kiểm thử công thức (pytest) | Không | Máy không có Python cục bộ |
| Bộ đánh giá — chất lượng câu trả lời | Không | Thiếu khóa API, PDF thật, bộ câu hỏi đã duyệt |
| Luật cảnh báo (promtool) | Không | Cần Docker |
| Kiểm thử thủ công (UAT, PERF, trình đọc màn hình, vận hành) | Không | Chưa lên lịch; cần người dùng thật và môi trường Staging |

## 3. Sai khác so với kế hoạch

| Sai khác | Lý do | Ảnh hưởng tới kết luận |
|---|---|---|
| Không chạy backend, E2E, promtool | Máy 7,9 GB RAM, còn 1,6 GB trống; Docker cần ~4 GB; máy từng reset (BSOD) khi chạy Docker nặng. Chủ dự án quyết định không chạy Docker | 108 ca "Chưa có kết quả"; LG-07, LG-08, LG-09 không thể xác nhận lại |
| Không chạy bộ đánh giá với mô hình thật | Thiếu `ANTHROPIC_API_KEY`, PDF thật (DEP-001), bộ câu hỏi đã duyệt (ASM-005) — đúng điều kiện tạm dừng ở MTP mục 8 | LG-02..LG-05 chưa kết luận |
| Số liệu backend/E2E lần trước không dùng để tính ca | Lần chạy 2026-10-23 (183 đạt backend, 19 đạt E2E — theo `docs/implement/launch_checklist.md`) không còn tệp kết quả; báo cáo HTML Playwright chỉ còn lần chạy `screenshots.spec.ts` (1/1 đạt). Lần chạy đó cũng trước commit `019fdc6` | Chỉ nêu làm tham khảo ở mục 9, không tính vào số ca đạt |
| Chưa có môi trường Test/Staging | Chưa có hạ tầng (MTP mục 11.1) | PERF, OPS-004, OPS-005, UAT chưa thể chạy |

## 4. Kết quả theo tầng

| Tầng | Nguồn kết quả (thời điểm) | Tổng | Đạt | Lỗi | Bỏ qua |
|---|---|---|---|---|---|
| Frontend (Vitest) | `test-results/frontend-vitest.xml` (2026-10-28 19:34, commit `019fdc6`) | 79 | 79 | 0 | 0 |
| Backend (pytest) | — | — | — | — | — |
| E2E (Playwright) | — | — | — | — | — |
| Bộ đánh giá (công thức) | — | — | — | — | — |

8 tệp Vitest: `components.test.tsx` (8), `failureMessages.test.ts` (16), `LoginPage.test.tsx`, `documents.test.tsx`, `chat.test.tsx`, `sources.test.tsx`, `admin.test.tsx`, `reports.test.tsx`. Thời gian chạy 70 giây. Cảnh báo duy nhất: React Router v7 future flags (không ảnh hưởng chức năng).

## 5. Kết quả theo nhóm ca kiểm thử

| Nhóm | Tổng | Đạt | Không đạt | Chưa có kết quả | Thủ công — chưa ghi nhận |
|---|---|---|---|---|---|
| 01 Đơn vị | 22 | 2 | 0 | 20 | 0 |
| 02 Tích hợp API | 40 | 0 | 0 | 40 | 0 |
| 03 Hệ thống (E2E) | 13 | 0 | 0 | 13 | 0 |
| 04 Chấp nhận | 11 | 0 | 0 | 0 | 11 |
| 05 Hiệu năng | 6 | 1 | 0 | 1 | 4 |
| 06 Bảo mật | 13 | 1 | 0 | 10 | 2 |
| 07 Khả năng tiếp cận | 8 | 2 | 0 | 4 | 2 |
| 08 Giao diện | 8 | 3 | 0 | 2 | 3 |
| 09 API (hợp đồng) | 15 | 0 | 0 | 15 | 0 |
| 10 Chất lượng câu trả lời | 8 | 0 | 0 | 0 | 8 |
| 11 Vận hành | 5 | 0 | 0 | 3 | 2 |
| **Tổng** | **149** | **9** | **0** | **108** | **32** |

**9 ca đạt:** UT-020 (thông báo lỗi tải lên), UT-021 (tô sáng đoạn trích), PERF-005 (phản hồi giao diện), SEC-007 (chống XSS từ câu trả lời), ACC-006 (thông báo lỗi cho trình đọc màn hình), ACC-008 (không chỉ dùng màu), UI-003 (trạng thái thành phần), UI-006 (trạng thái chờ), UI-007 (thông báo).

**Đạt một phần (phần Vitest đạt, phần E2E chưa chạy):** E2E-003 (thiếu `auth.spec.ts` "hết phiên"), ACC-001 (thiếu `a11y.spec.ts` "chỉ dùng bàn phím"), ACC-005 (thiếu `delete-audit.spec.ts`), UI-008 (thiếu `qa.spec.ts`). Theo quy tắc, các ca này vẫn tính "Chưa có kết quả".

## 6. Lỗi phát hiện

Không phát hiện lỗi trong lần chạy này.

| Mã | Ca / kiểm thử | Mô tả | Mức độ | Trạng thái |
|---|---|---|---|---|
| — | — | Không có | — | — |

Ghi nhận từ đợt phát triển (theo `launch_checklist.md`): hai lỗi nghiêm trọng phát hiện ở E2E đã được sửa và có kiểm thử hồi quy. Lỗi 1: API trả 200 nhưng chưa lưu tin nhắn, do commit chạy sau phản hồi. Lỗi 2: tiến trình API thiếu model. Lần này chưa chạy lại hai kiểm thử hồi quy đó (thuộc backend).

## 7. Chất lượng câu trả lời (bộ đánh giá)

Báo cáo gần nhất: `evaluation/reports/v1-20261023T130536Z.json`, ngày 2026-10-23, bộ `v1.jsonl` (59 câu, bản nháp).

**Cấu hình lần chạy đó là embedding giả lập (`hash`) và adapter trả lời giả lập (`fake`).** Vì vậy đây là kiểm chứng luồng đầu-cuối, **không phải số liệu chất lượng**, và không dùng để đánh giá LG-02..LG-05.

| Chỉ số | Giá trị (luồng giả lập) | Ngưỡng | Kết luận |
|---|---|---|---|
| Đúng và có nguồn (MET-002) | 70,8% | [TBD: OQ-002] | Chưa kết luận — chưa đo với mô hình thật |
| Tỷ lệ bịa | 75,0% | [TBD: OQ-002] | Chưa kết luận — adapter giả lập không có khả năng từ chối thật |
| Độ phủ nguồn (nhiều tài liệu) | 0,0% | báo cáo | Chưa kết luận |
| Câu hỏi tiếp theo đúng | 58,3% | báo cáo | Chưa kết luận |
| Đúng trang | 100% (56/56 citation) | 100% | Cơ chế kiểm đúng trang hoạt động; cần đo lại với Claude |
| Câu trả lời có nội dung có nguồn | 100% | 100% | Như trên |
| Độ trễ p50 / p90 / p95 | 197 / 319 / 356 ms | [TBD] | Không có ý nghĩa — không gọi mô hình thật |

## 8. Đánh giá theo tiêu chí launch (LG-01..LG-11)

| LG | Tiêu chí | Kết luận | Bằng chứng | Còn thiếu / việc cần làm | Người chịu trách nhiệm |
|---|---|---|---|---|---|
| LG-01 | 100% AC của story P0 đạt | Chưa kết luận | Vitest đạt cho phần giao diện của AC-011, AC-017, AC-018 | Chạy backend + E2E; AC-010, AC-013, AC-015 phụ thuộc LG-02, LG-06 | Trưởng nhóm QA |
| LG-02 | MET-002 ≥ [TBD] | Chưa kết luận | Chỉ có số liệu luồng giả lập | Chốt OQ-002; chạy bộ đánh giá với `bge-m3` + Claude và bộ câu hỏi đã duyệt | Chủ sản phẩm, kỹ sư AI |
| LG-03 | Tỷ lệ bịa ≤ [TBD] | Chưa kết luận | Như LG-02 | Như LG-02; thêm nhóm câu QE-003 | Kỹ sư AI |
| LG-04 | 100% câu trả lời có nội dung nêu đúng tài liệu và trang | Chưa kết luận | Cơ chế đạt ở luồng giả lập (56/56); kiểm thử tích hợp chưa chạy lại | Chạy INT-API-019 và QE-006 với mô hình thật | Kỹ sư AI |
| LG-05 | Thời gian phản hồi ≤ [TBD] | Chưa kết luận | PERF-005 (giao diện) đạt; PERF-001 chưa chạy | Chốt ngưỡng; chạy PERF-001 trên Staging với Claude | Chủ sản phẩm, DevOps |
| LG-06 | Bảo mật xác nhận bằng văn bản | **Không đạt** | `data_handling.md` đã soạn; chưa có chữ ký | Bộ phận bảo mật rà soát và ký (UAT-011) | Bộ phận bảo mật |
| LG-07 | Kiểm tra quyền và phạm vi tài liệu | Chưa kết luận (lần này) | SEC-001..003 chưa chạy lại; lần 2026-10-23 ghi "Đạt" trong `launch_checklist.md` nhưng không còn tệp kết quả | Chạy `tests/security` | Trưởng nhóm QA |
| LG-08 | Xóa đúng ở truy vấn và nơi lưu | Chưa kết luận (lần này) | INT-API-028..030 chưa chạy lại | Chạy `test_delete_and_purge.py`; AQ-003 (sao lưu) còn mở | DevOps |
| LG-09 | Không còn lỗi nghiêm trọng/cao; độ phủ đạt [TBD] | Chưa kết luận | Không có lỗi mở đã biết; chưa đo coverage; ngưỡng chưa chốt | Chạy toàn bộ backend + E2E kèm `pytest --cov`; chốt ngưỡng | Trưởng nhóm QA |
| LG-10 | Có bộ câu hỏi chuẩn và PDF mẫu thật | **Không đạt** | Chỉ có bộ tổng hợp và `v1.jsonl` bản nháp | Business owner cung cấp (DEP-001, ASM-005) | Business owner |
| LG-11 | OQ-001..OQ-007 đã chốt | **Không đạt** | Giá trị đang dùng là tạm thời | Sponsor chốt | Sponsor |

## 9. Đánh giá tổng thể

- **Độ phủ của lần chạy:** 9/149 ca (6%) có kết quả đạt. Toàn bộ 108 ca "Chưa có kết quả" là do tầng chưa chạy, không do lệch tên kiểm thử. Cả 79 kiểm thử Vitest đều gắn được với ít nhất một ca, nên phía frontend không có lỗ hổng truy vết.
- **Lỗ hổng truy vết phía backend (từ phân tích tĩnh mã kiểm thử, chưa chạy):** khoảng 12 kiểm thử backend chưa được ca nào tham chiếu, ví dụ `test_source_opened_event`, `test_health_live_and_ready`, `test_session_started_once_per_day`, `test_real_api_cites_correct_chunk`. Nên bổ sung chúng vào cột "Tự động hóa" của ca tương ứng (API-009, INT-API-036, INT-API-034, QE-006).
- **Kết quả tham khảo (không tính vào số ca):** theo `launch_checklist.md` ngày 2026-10-23, backend 183 đạt / 1 bỏ qua (cần khóa API), E2E 19 đạt, kiểm thử công thức bộ đánh giá 12 đạt, promtool SUCCESS. Các số này do tài liệu ghi lại, không còn tệp kết quả, và được chạy trên cây làm việc trước commit `019fdc6`.
- **Mức tin cậy:** cao cho phần giao diện đã kiểm (chạy trên đúng commit hiện tại). Thấp cho mọi kết luận về backend, bảo mật, xóa dữ liệu và chất lượng câu trả lời — những phần quyết định việc phát hành.

## 10. Rủi ro còn lại

| Rủi ro | Mức | Giảm thiểu / theo dõi |
|---|---|---|
| Backend và E2E chưa được xác nhận lại trên commit hiện tại; hồi quy có thể đã xảy ra mà không biết | Cao | Chạy trên CI (`ci.yml` có backend, `nightly.yml` có E2E) và lấy kết quả |
| Chất lượng câu trả lời với mô hình thật chưa đo (bịa, sai nguồn) | Cao | Chạy QE-001..QE-008 khi có khóa API và dữ liệu thật |
| Máy phát triển không đủ tài nguyên cho Docker → không tự kiểm được ở máy cục bộ | Trung bình | Dùng máy ≥ 16 GB hoặc CI; giữ `.wslconfig` giới hạn 4 GB |
| CI chưa xuất JUnit nên kết quả CI không đưa vào báo cáo tự động được | Trung bình | Thêm `--junitxml` / reporter junit và `upload-artifact` vào workflow |
| Dữ liệu tài liệu đã xóa còn trong bản sao lưu (AQ-003) | Trung bình | OPS-005; quyết định chính sách sao lưu |

## 11. Khuyến nghị

| # | Việc | Người | Hạn |
|---|---|---|---|
| 1 | Chạy backend (`scripts/backend-docker.sh pytest -q -p no:cacheprovider --junitxml=test-results/backend.xml`) và E2E (`PLAYWRIGHT_JUNIT_OUTPUT_NAME=../test-results/e2e-playwright.xml npx playwright test --reporter=list,junit`) trên máy ≥ 16 GB hoặc qua CI, rồi lập lại báo cáo này | Trưởng nhóm QA / DevOps | Trước G4 |
| 2 | Thêm xuất JUnit và lưu artifact vào `.github/workflows/ci.yml`, `nightly.yml` | DevOps | Sprint hiện tại |
| 3 | Chốt OQ-001..OQ-007, đặc biệt ngưỡng chất lượng và thời gian phản hồi (OQ-002) | Sponsor, chủ sản phẩm | G3 |
| 4 | Cung cấp PDF thật và bộ câu hỏi đã duyệt; cấp khóa API cho môi trường đánh giá | Business owner, sponsor | G3 |
| 5 | Chạy bộ đánh giá với `bge-m3` + Claude (QE-001..QE-008), có chấm tay mẫu 20% (QE-008) | Kỹ sư AI, business owner | G3 |
| 6 | Thực hiện ca thủ công (UAT, ACC-002, PERF, OPS) và ghi vào `docs/testing/results/manual_results.csv` | QA, người dùng BD | Trước G4 |
| 7 | Bộ phận bảo mật rà soát `data_handling.md` và ký (UAT-011) | Bộ phận bảo mật | G4 |
| 8 | Bổ sung khoảng 12 kiểm thử backend chưa gắn vào cột "Tự động hóa" của ca tương ứng | QA | Sprint hiện tại |

## 12. Hoạt động kiểm thử đã thực hiện

| Hoạt động | Thời điểm | Người thực hiện | Ghi chú |
|---|---|---|---|
| Soạn Master Test Plan và 149 ca kiểm thử | 2026-10-24 – 10-26 | QA | `docs/testing/` |
| Chạy Vitest (79 kiểm thử) | 2026-10-28 19:33 | QA | 79/79 đạt, 70 giây |
| Kiểm tra tài nguyên trước khi chạy Docker | 2026-10-28 | QA | 1,6 GB RAM trống → chủ dự án quyết định không chạy Docker |
| Tổng hợp kết quả theo ca (`collect_results.mjs`) | 2026-10-28 | QA | `test-results/summary/` |
| Lần chạy toàn bộ trước đó (tham khảo) | 2026-10-23 | Phát triển | Ghi trong `docs/implement/launch_checklist.md` |

## 13. Phê duyệt

| Vai trò | Họ tên | Quyết định | Ngày |
|---|---|---|---|
| Trưởng nhóm QA | | | |
| Chủ sản phẩm | | | |
| Sponsor | | | |
| Bảo mật | | | |

## Phụ lục B — Lịch sử phiên bản

| Phiên bản | Ngày | Mốc | Thay đổi chính |
|---|---|---|---|
| 1.0 | 2026-10-28 | Trước G4, lần 1 | Bản đầu tiên; chỉ có kết quả Vitest |

## Phụ lục A — Trạng thái từng ca

Sinh từ `test-results/summary/summary.md` (`collect_results.mjs`, 2026-10-28).

| Mã | Tên | Ưu tiên | Trạng thái | Ghi chú |
|---|---|---|---|---|
| UT-001 | Trích xuất PDF giữ số trang | Cao | Chưa có kết quả | thiếu kết quả: test_extract.py::test_plain_pdf_keeps_page_numbers |
| UT-002 | Chuẩn hóa tiếng Việt về NFC | Cao | Chưa có kết quả | thiếu kết quả: test_extract.py::test_vietnamese_text_is_nfc_and_keeps_diacritics |
| UT-003 | Phân loại lỗi PDF | Cao | Chưa có kết quả | thiếu kết quả: test_extract.py::test_encrypted_pdf, test_extract.py::test_corrupted_pdf, test_extract.py::test_random_bytes_are_corrupted, test_extract.py::test_image_only_pdf_has_no_text |
| UT-004 | Chunk không vượt ranh giới trang | Cao | Chưa có kết quả | thiếu kết quả: test_chunking.py::test_no_chunk_spans_two_pages |
| UT-005 | Trang ngắn và trang rỗng | Trung bình | Chưa có kết quả | thiếu kết quả: test_chunking.py::test_short_page_gives_exactly_one_chunk, test_chunking.py::test_empty_page_gives_no_chunk |
| UT-006 | Giới hạn token, chồng lấp và ghép lại văn bản | Cao | Chưa có kết quả | thiếu kết quả: test_chunking.py::test_chunks_respect_token_limit_and_overlap, test_chunking.py::test_chunks_without_overlap_reconstruct_page_text, test_chunking.py::test_invalid_parameters |
| UT-007 | Lớp từ chối 1: dưới ngưỡng không gọi mô hình | Cao | Chưa có kết quả | thiếu kết quả: test_qa_service.py::test_layer1_below_threshold_does_not_call_model, test_qa_service.py::test_layer1_no_chunks_does_not_call_model |
| UT-008 | Lớp từ chối 2: câu từ chối cố định | Cao | Chưa có kết quả | thiếu kết quả: test_qa_service.py::test_layer2_fixed_refusal_sentence, test_qa_service.py::test_not_found_sentence_matching_is_normalized |
| UT-009 | Lớp từ chối 3: có nội dung nhưng không có nguồn hợp lệ | Cao | Chưa có kết quả | thiếu kết quả: test_qa_service.py::test_layer3_content_without_citation, test_qa_service.py::test_layer3_citation_index_out_of_range_is_invalid, test_qa_service.py::test_answer_with_content_always_has_citation |
| UT-010 | Ánh xạ và gộp citation | Cao | Chưa có kết quả | thiếu kết quả: test_qa_service.py::test_map_citations_dedupes_and_keeps_order, test_qa_service.py::test_answer_with_citation |
| UT-011 | Ghép câu hỏi trước vào truy vấn | Trung bình | Chưa có kết quả | thiếu kết quả: test_qa_service.py::test_retrieval_query_appends_previous_user_question |
| UT-012 | Adapter Claude: ánh xạ citation | Cao | Chưa có kết quả | thiếu kết quả: test_claude_adapter.py::test_citations_map_to_chunk_index |
| UT-013 | Adapter Claude: từ chối và cắt cụt | Cao | Chưa có kết quả | thiếu kết quả: test_claude_adapter.py::test_refusal_is_reported_before_reading_content, test_claude_adapter.py::test_max_tokens_is_an_error |
| UT-014 | Adapter Claude: hình dạng yêu cầu | Cao | Chưa có kết quả | thiếu kết quả: test_claude_adapter.py::test_request_shape, test_claude_adapter.py::test_documents_have_title_and_citations_enabled |
| UT-015 | Adapter OIDC: kiểm tra ID token | Cao | Chưa có kết quả | thiếu kết quả: test_oidc_adapter.py::test_authorization_url_uses_pkce, test_oidc_adapter.py::test_exchange_returns_identity_and_sends_verifier, test_oidc_adapter.py::test_exchange_rejects_invalid_token |
| UT-016 | Định dạng lỗi chung, không lộ chi tiết kỹ thuật | Cao | Chưa có kết quả | thiếu kết quả: test_framework.py::test_unhandled_error_has_standard_format_without_stack_trace, test_framework.py::test_not_found_uses_error_format, test_framework.py::test_validation_error_does_not_echo_input |
| UT-017 | Log không chứa nội dung câu hỏi | Cao | Chưa có kết quả | thiếu kết quả: test_framework.py::test_request_log_does_not_contain_question_value, test_framework.py::test_redact_processor_strips_nested_content_keys |
| UT-018 | Tiến trình API nạp đủ model | Cao | Chưa có kết quả | thiếu kết quả: test_smoke.py::test_api_process_loads_every_model |
| UT-019 | Mọi ngưỡng là trường cấu hình | Cao | Chưa có kết quả | thiếu kết quả: test_framework.py::test_every_threshold_is_configurable |
| UT-020 | Bảng thông báo lỗi tải lên | Trung bình | Đạt |  |
| UT-021 | Tô sáng đoạn trích trong trang nguồn | Trung bình | Đạt |  |
| UT-022 | Công thức chỉ số của bộ đánh giá | Cao | Chưa có kết quả | thiếu kết quả: test_run_eval.py |
| INT-API-001 | Đăng nhập thành công | Cao | Chưa có kết quả | thiếu kết quả: test_auth.py::test_login_me_logout |
| INT-API-002 | Sai thông tin đăng nhập không tiết lộ tài khoản | Cao | Chưa có kết quả | thiếu kết quả: test_auth.py::test_login_wrong_password_is_generic, test_auth.py::test_local_identity_right_and_wrong_password, test_auth.py::test_password_hash_is_argon2id |
| INT-API-003 | Đăng nhập đúng nhưng chưa được cấp quyền | Cao | Chưa có kết quả | thiếu kết quả: test_auth.py::test_login_without_grant_is_no_access |
| INT-API-004 | Bảo vệ CSRF theo Origin | Cao | Chưa có kết quả | thiếu kết quả: test_auth.py::test_post_without_valid_origin_is_rejected |
| INT-API-005 | Phiên hết hạn | Cao | Chưa có kết quả | thiếu kết quả: test_auth.py::test_expired_session_is_session_expired, test_auth.py::test_no_session_is_401 |
| INT-API-006 | Người bị thu hồi mất truy cập ngay | Cao | Chưa có kết quả | thiếu kết quả: test_auth.py::test_revoked_user_loses_access_on_next_request |
| INT-API-007 | Tải nhiều tệp, mỗi tệp xét độc lập | Cao | Chưa có kết quả | thiếu kết quả: test_ingestion_flow.py::test_mixed_upload_each_file_judged_independently |
| INT-API-008 | Giới hạn số tài liệu mỗi người | Trung bình | Chưa có kết quả | thiếu kết quả: test_ingestion_flow.py::test_max_docs_per_user |
| INT-API-009 | Nạp PDF hợp lệ tới trạng thái sẵn sàng | Cao | Chưa có kết quả | thiếu kết quả: test_ingestion_flow.py::test_valid_pdf_becomes_ready_with_paged_chunks, test_ingestion_flow.py::test_lifecycle_invariants, test_ingestion_flow.py::test_upload_events_have_no_content |
| INT-API-010 | Lý do lỗi do worker xác định | Cao | Chưa có kết quả | thiếu kết quả: test_ingestion_flow.py::test_worker_failure_reasons |
| INT-API-011 | Lỗi tạm thời được thử lại rồi chuyển failed | Cao | Chưa có kết quả | thiếu kết quả: test_ingestion_flow.py::test_transient_storage_error_retries_then_fails_internal, test_storage_and_queue.py::test_transient_error_is_retried_then_succeeds, test_storage_and_queue.py::test_job_fails_after_max_attempts_and_calls_give_up, test_storage_and_queue.py::test_backoff_delays_next_attempt |
| INT-API-012 | Tài liệu bị xóa trong lúc đang nạp | Cao | Chưa có kết quả | thiếu kết quả: test_ingestion_flow.py::test_document_moved_to_deleting_during_ingest_is_discarded |
| INT-API-013 | Nhiều worker không lấy trùng việc | Cao | Chưa có kết quả | thiếu kết quả: test_storage_and_queue.py::test_two_workers_never_claim_the_same_job, test_ingestion_flow.py::test_many_files_with_two_concurrent_workers |
| INT-API-014 | Thử lại tài liệu lỗi | Trung bình | Chưa có kết quả | thiếu kết quả: test_ingestion_flow.py::test_retry_only_for_failed_and_requeues |
| INT-API-015 | Truy xuất không bao giờ trả tài liệu ngoài phạm vi | Cao | Chưa có kết quả | thiếu kết quả: test_retrieval.py::test_chunks_outside_allowed_documents_never_appear, test_retrieval.py::test_empty_allowed_set |
| INT-API-016 | Chỉ truy xuất tài liệu sẵn sàng | Cao | Chưa có kết quả | thiếu kết quả: test_retrieval.py::test_only_ready_documents_are_searched |
| INT-API-017 | Đủ TOP_K khi danh sách được phép nhỏ trong kho lớn | Trung bình | Chưa có kết quả | thiếu kết quả: test_retrieval.py::test_small_allowed_set_in_large_store_still_returns_top_k |
| INT-API-018 | Giới hạn số chunk mỗi tài liệu | Trung bình | Chưa có kết quả | thiếu kết quả: test_retrieval.py::test_max_chunks_per_document, test_qa_flow.py::test_question_across_documents_cites_the_right_one |
| INT-API-019 | Câu trả lời có nguồn đúng tài liệu và trang | Cao | Chưa có kết quả | thiếu kết quả: test_qa_flow.py::test_answer_has_source_document_and_page |
| INT-API-020 | Câu ngoài phạm vi không gọi mô hình | Cao | Chưa có kết quả | thiếu kết quả: test_qa_flow.py::test_out_of_scope_question_is_not_found_without_calling_model, test_qa_flow.py::test_model_answers_without_valid_citation_become_not_found |
| INT-API-021 | Kiểm tra độ dài câu hỏi | Trung bình | Chưa có kết quả | thiếu kết quả: test_qa_flow.py::test_question_validation |
| INT-API-022 | Dịch vụ AI từ chối hoặc quá thời gian | Cao | Chưa có kết quả | thiếu kết quả: test_qa_flow.py::test_model_refusal_returns_generic_error, test_qa_flow.py::test_timeout_returns_504, test_qa_flow.py::test_slow_generator_hits_answer_timeout |
| INT-API-023 | Mỗi câu hỏi đúng một bản ghi kiểm toán, không nội dung | Cao | Chưa có kết quả | thiếu kết quả: test_qa_flow.py::test_each_question_writes_exactly_one_audit_record_without_content, test_migrations.py::test_audit_and_usage_tables_have_no_content_columns |
| INT-API-024 | Lỗi commit không bị nuốt | Cao | Chưa có kết quả | thiếu kết quả: test_qa_flow.py::test_commit_failure_is_reported_not_swallowed |
| INT-API-025 | Lịch sử hội thoại và câu hỏi tiếp theo | Trung bình | Chưa có kết quả | thiếu kết quả: test_qa_flow.py::test_history_and_follow_up_question, test_qa_flow.py::test_history_is_limited_to_history_turns, test_qa_flow.py::test_conversation_belongs_to_owner_only |
| INT-API-026 | Trang nguồn: trang không hợp lệ và quyền | Cao | Chưa có kết quả | thiếu kết quả: test_qa_flow.py::test_source_page_and_file_access |
| INT-API-027 | Tải tệp gốc qua backend | Trung bình | Chưa có kết quả | thiếu kết quả: test_qa_flow.py::test_source_page_and_file_access |
| INT-API-028 | Xóa loại tài liệu khỏi truy vấn ngay lập tức | Cao | Chưa có kết quả | thiếu kết quả: test_delete_and_purge.py::test_deleted_document_is_excluded_immediately |
| INT-API-029 | Xóa vĩnh viễn | Cao | Chưa có kết quả | thiếu kết quả: test_delete_and_purge.py::test_purge_removes_chunks_file_and_sets_purged_at |
| INT-API-030 | Xóa vĩnh viễn chịu lỗi và làm lại được | Cao | Chưa có kết quả | thiếu kết quả: test_delete_and_purge.py::test_storage_error_midway_is_retried_and_completes, test_delete_and_purge.py::test_purge_twice_is_harmless, test_delete_and_purge.py::test_overdue_deleting_documents_are_counted |
| INT-API-031 | Quyền xóa tài liệu | Cao | Chưa có kết quả | thiếu kết quả: test_delete_and_purge.py::test_delete_permissions |
| INT-API-032 | Đánh giá câu trả lời | Thấp | Chưa có kết quả | thiếu kết quả: test_qa_flow.py::test_feedback_is_saved_and_can_be_changed |
| INT-API-033 | Bản ghi kiểm toán: lọc và phân trang | Trung bình | Chưa có kết quả | thiếu kết quả: test_admin_reports_health.py::test_audit_lists_one_record_per_question_without_content, test_admin_reports_health.py::test_audit_filters_and_cursor |
| INT-API-034 | Báo cáo sử dụng theo tuần | Trung bình | Chưa có kết quả | thiếu kết quả: test_admin_reports_health.py::test_weekly_usage_with_seed_data, test_admin_reports_health.py::test_usage_endpoint_includes_helpful_ratio |
| INT-API-035 | Quản lý quyền truy cập | Cao | Chưa có kết quả | thiếu kết quả: test_auth.py::test_admin_grant_list_revoke, test_auth.py::test_admin_cannot_revoke_self, test_auth.py::test_admin_endpoints_forbidden_for_other_roles |
| INT-API-036 | Health báo lỗi khi thành phần dừng | Trung bình | Chưa có kết quả | thiếu kết quả: test_admin_reports_health.py::test_ready_ok_when_everything_is_up, test_admin_reports_health.py::test_ready_fails_when_storage_is_down, test_admin_reports_health.py::test_ready_fails_when_database_is_down, test_admin_reports_health.py::test_ready_fails_when_queue_backlog_is_old |
| INT-API-037 | Đăng nhập OIDC | Cao | Chưa có kết quả | thiếu kết quả: test_oidc_flow.py |
| INT-API-038 | Lệnh tạo quản trị viên đầu tiên | Trung bình | Chưa có kết quả | thiếu kết quả: test_auth.py::test_cli_create_admin_on_empty_database |
| INT-API-039 | Migration và ràng buộc lược đồ | Cao | Chưa có kết quả | thiếu kết quả: test_migrations.py |
| INT-API-040 | Dọn dữ liệu định kỳ theo thời hạn lưu | Trung bình | Chưa có kết quả | thiếu kết quả: test_admin_reports_health.py::test_audit_retention_cleanup, test_qa_flow.py::test_inactive_conversations_are_cleaned_up, test_qa_flow.py::test_retention_zero_keeps_everything |
| E2E-001 | Đăng nhập đúng và sai | Cao | Chưa có kết quả | thiếu kết quả: auth.spec.ts: "đăng nhập đúng", auth.spec.ts: "đăng nhập sai" |
| E2E-002 | Người bị thu hồi quyền không vào được | Cao | Chưa có kết quả | thiếu kết quả: auth.spec.ts: "không có quyền" |
| E2E-003 | Hết phiên giữ câu hỏi đang soạn | Cao | Chưa có kết quả | thiếu kết quả: auth.spec.ts: "hết phiên" |
| E2E-004 | Trạng thái trống | Trung bình | Chưa có kết quả | thiếu kết quả: documents.spec.ts: "trạng thái trống" |
| E2E-005 | Tải PDF hợp lệ tới "Sẵn sàng" | Cao | Chưa có kết quả | thiếu kết quả: documents.spec.ts: "tải PDF hợp lệ" |
| E2E-006 | Tệp hỏng và tệp không phải PDF | Cao | Chưa có kết quả | thiếu kết quả: documents.spec.ts: "tải tệp hỏng", documents.spec.ts: "tệp không phải PDF" |
| E2E-007 | Mất mạng khi tải lên | Cao | Chưa có kết quả | thiếu kết quả: documents.spec.ts: "mất mạng giữa chừng khi tải lên" |
| E2E-008 | Hỏi đáp có nguồn và trình xem nguồn | Cao | Chưa có kết quả | thiếu kết quả: qa.spec.ts: "hỏi đáp có nguồn và trình xem nguồn" |
| E2E-009 | Mất mạng khi hỏi | Cao | Chưa có kết quả | thiếu kết quả: qa.spec.ts: "mất mạng khi hỏi" |
| E2E-010 | Xóa tài liệu | Cao | Chưa có kết quả | thiếu kết quả: delete-audit.spec.ts: "xóa tài liệu" |
| E2E-011 | Quản trị quyền và bản ghi kiểm toán | Trung bình | Chưa có kết quả | thiếu kết quả: delete-audit.spec.ts: "quản trị bảo mật" |
| E2E-012 | Khả năng tiếp cận trên mọi màn hình | Cao | Chưa có kết quả | thiếu kết quả: a11y.spec.ts, auth.spec.ts, documents.spec.ts, qa.spec.ts |
| E2E-013 | Ảnh màn hình đối chiếu với thiết kế | Trung bình | Chưa có kết quả | thiếu kết quả: screenshots.spec.ts |
| UAT-001 | Tải nhiều PDF thật |  | Thủ công — chưa ghi nhận |  |
| UAT-002 | Tệp lỗi có lý do dễ hiểu |  | Thủ công — chưa ghi nhận |  |
| UAT-003 | Trả lời câu hỏi thường gặp có nguồn |  | Thủ công — chưa ghi nhận |  |
| UAT-004 | Không bịa khi tài liệu không có thông tin |  | Thủ công — chưa ghi nhận |  |
| UAT-005 | Hỏi tiếp bằng đại từ |  | Thủ công — chưa ghi nhận |  |
| UAT-006 | Xóa tài liệu và xác nhận xóa vĩnh viễn |  | Thủ công — chưa ghi nhận |  |
| UAT-007 | Cấp/thu hồi quyền và cô lập tài liệu |  | Thủ công — chưa ghi nhận |  |
| UAT-008 | Tra cứu bản ghi kiểm toán |  | Thủ công — chưa ghi nhận |  |
| UAT-009 | Báo cáo mức sử dụng |  | Thủ công — chưa ghi nhận |  |
| UAT-010 | Nghiệm thu chất lượng theo ngôn ngữ |  | Thủ công — chưa ghi nhận |  |
| UAT-011 | Rà soát chính sách dữ liệu |  | Thủ công — chưa ghi nhận |  |
| PERF-001 | Độ trễ hỏi đáp trên bộ câu hỏi chuẩn | Cao | Thủ công — chưa ghi nhận |  |
| PERF-002 | Tải nhẹ hỏi đáp đồng thời | Trung bình | Thủ công — chưa ghi nhận |  |
| PERF-003 | Thời gian nạp tài liệu | Trung bình | Thủ công — chưa ghi nhận |  |
| PERF-004 | Truy xuất trong kho lớn có lọc quyền | Trung bình | Thủ công — chưa ghi nhận |  |
| PERF-005 | Phản hồi giao diện | Trung bình | Đạt |  |
| PERF-006 | Hết thời gian chờ đúng hạn | Cao | Chưa có kết quả | thiếu kết quả: test_qa_flow.py::test_slow_generator_hits_answer_timeout |
| SEC-001 | Mọi route yêu cầu phiên | Cao | Chưa có kết quả | thiếu kết quả: test_auth_matrix.py::test_route_list_is_not_empty, test_auth_matrix.py::test_every_protected_route_requires_session, test_auth_matrix.py::test_unprotected_route_makes_matrix_fail |
| SEC-002 | Phân quyền theo vai trò | Cao | Chưa có kết quả | thiếu kết quả: test_auth_matrix.py::test_admin_routes_forbidden_for_non_admin, test_auth.py::test_wrong_role_is_forbidden_role_and_records_access_denied, test_admin_reports_health.py::test_usage_endpoint_includes_helpful_ratio |
| SEC-003 | Cô lập dữ liệu giữa người dùng | Cao | Chưa có kết quả | thiếu kết quả: test_isolation.py |
| SEC-004 | Chính sách mật khẩu và khóa tạm | Cao | Chưa có kết quả | thiếu kết quả: test_auth.py::test_local_identity_locks_after_too_many_failures, test_auth.py::test_password_hash_is_argon2id, test_auth.py::test_local_identity_right_and_wrong_password |
| SEC-005 | Quản lý phiên | Cao | Chưa có kết quả | thiếu kết quả: test_auth.py::test_login_me_logout, test_auth.py::test_expired_session_is_session_expired, test_auth.py::test_revoked_user_loses_access_on_next_request |
| SEC-006 | Chống CSRF | Cao | Chưa có kết quả | thiếu kết quả: test_auth.py::test_post_without_valid_origin_is_rejected |
| SEC-007 | Chống XSS từ nội dung câu trả lời | Cao | Đạt |  |
| SEC-008 | Tiêu đề bảo mật của frontend production | Trung bình | Thủ công — chưa ghi nhận |  |
| SEC-009 | Không lộ thông tin qua lỗi | Cao | Chưa có kết quả | thiếu kết quả: test_framework.py::test_unhandled_error_has_standard_format_without_stack_trace, test_framework.py::test_validation_error_does_not_echo_input, test_isolation.py |
| SEC-010 | Log và sự kiện không chứa nội dung (canary) | Cao | Chưa có kết quả | thiếu kết quả: test_no_content_in_logs.py::test_canary_never_reaches_logs_events_or_audit |
| SEC-011 | Kiểm tra tệp tải lên theo nội dung | Cao | Chưa có kết quả | thiếu kết quả: test_ingestion_flow.py::test_mixed_upload_each_file_judged_independently |
| SEC-012 | Quét lỗ hổng phụ thuộc | Trung bình | Thủ công — chưa ghi nhận |  |
| SEC-013 | Dữ liệu gửi ra dịch vụ AI | Cao | Chưa có kết quả | thiếu kết quả: test_claude_adapter.py::test_request_shape, test_qa_flow.py::test_out_of_scope_question_is_not_found_without_calling_model |
| ACC-001 | Dùng được chỉ bằng bàn phím | Cao | Chưa có kết quả | thiếu kết quả: a11y.spec.ts: "chỉ dùng bàn phím" |
| ACC-002 | Trình đọc màn hình | Cao | Thủ công — chưa ghi nhận |  |
| ACC-003 | Tương phản màu | Cao | Chưa có kết quả | thiếu kết quả: a11y.spec.ts, documents.spec.ts, qa.spec.ts, auth.spec.ts |
| ACC-004 | Thuộc tính ARIA | Cao | Thủ công — chưa ghi nhận |  |
| ACC-005 | Quản lý tiêu điểm | Cao | Chưa có kết quả | thiếu kết quả: delete-audit.spec.ts |
| ACC-006 | Thông báo lỗi được trình đọc màn hình nhận | Trung bình | Đạt |  |
| ACC-007 | Thu phóng 200% | Trung bình | Chưa có kết quả | thiếu kết quả: a11y.spec.ts: "thu phóng 200%" |
| ACC-008 | Không chỉ dùng màu để truyền thông tin | Trung bình | Đạt |  |
| UI-001 | Đối chiếu ảnh mẫu theo từng trạng thái | Cao | Chưa có kết quả | thiếu kết quả: screenshots.spec.ts |
| UI-002 | Độ rộng màn hình | Thấp | Thủ công — chưa ghi nhận |  |
| UI-003 | Trạng thái của thành phần | Trung bình | Đạt |  |
| UI-004 | Tương tác | Trung bình | Thủ công — chưa ghi nhận |  |
| UI-005 | Trạng thái lỗi | Cao | Thủ công — chưa ghi nhận |  |
| UI-006 | Trạng thái chờ | Trung bình | Đạt |  |
| UI-007 | Thông báo | Thấp | Đạt |  |
| UI-008 | Điều hướng | Cao | Chưa có kết quả | thiếu kết quả: qa.spec.ts |
| API-001 | `POST /auth/login` |  | Chưa có kết quả | Theo INT-API-001: Chưa có kết quả, INT-API-002: Chưa có kết quả, INT-API-003: Chưa có kết quả, INT-API-004: Chưa có kết quả, SEC-004: Chưa có kết quả, INT-API-037: Chưa có kết quả |
| API-002 | `GET /auth/me`, `POST /auth/logout` |  | Chưa có kết quả | Theo INT-API-001: Chưa có kết quả, INT-API-005: Chưa có kết quả, INT-API-006: Chưa có kết quả, SEC-005: Chưa có kết quả |
| API-003 | `GET /auth/oidc/login`, `GET /auth/oidc/callback` |  | Chưa có kết quả | Theo INT-API-037: Chưa có kết quả, UT-015: Chưa có kết quả |
| API-004 | `POST /documents` |  | Chưa có kết quả | Theo INT-API-007: Chưa có kết quả, INT-API-008: Chưa có kết quả, INT-API-009: Chưa có kết quả, SEC-011: Chưa có kết quả |
| API-005 | `GET /documents`, `GET /documents/{id}` |  | Chưa có kết quả | Theo INT-API-009: Chưa có kết quả, INT-API-028: Chưa có kết quả, SEC-003: Chưa có kết quả |
| API-006 | `POST /documents/{id}/retry` |  | Chưa có kết quả | Theo INT-API-014: Chưa có kết quả |
| API-007 | `DELETE /documents/{id}` |  | Chưa có kết quả | Theo INT-API-028: Chưa có kết quả, INT-API-029: Chưa có kết quả, INT-API-030: Chưa có kết quả, INT-API-031: Chưa có kết quả |
| API-008 | `GET /documents/{id}/pages/{page}`, `GET /documents/{id}/file` |  | Chưa có kết quả | Theo INT-API-019: Chưa có kết quả, INT-API-026: Chưa có kết quả, INT-API-027: Chưa có kết quả |
| API-009 | `POST /events/source-opened` |  | Chưa có kết quả | Theo SEC-003: Chưa có kết quả |
| API-010 | `POST /conversations`, `POST\|GET /conversations/{id}/messages` |  | Chưa có kết quả | Theo INT-API-019: Chưa có kết quả, INT-API-020: Chưa có kết quả, INT-API-021: Chưa có kết quả, INT-API-022: Chưa có kết quả, INT-API-023: Chưa có kết quả, INT-API-024: Chưa có kết quả, INT-API-025: Chưa có kết quả |
| API-011 | `PUT /messages/{id}/feedback` |  | Chưa có kết quả | Theo INT-API-032: Chưa có kết quả |
| API-012 | `GET\|POST /admin/access`, `DELETE /admin/access/{user_id}` |  | Chưa có kết quả | Theo INT-API-035: Chưa có kết quả, SEC-002: Chưa có kết quả |
| API-013 | `GET /admin/audit` |  | Chưa có kết quả | Theo INT-API-033: Chưa có kết quả |
| API-014 | `GET /reports/usage` |  | Chưa có kết quả | Theo INT-API-034: Chưa có kết quả |
| API-015 | `GET /health/live`, `GET /health/ready`, `GET /metrics` |  | Chưa có kết quả | Theo INT-API-036: Chưa có kết quả, OPS-001: Chưa có kết quả |
| QE-001 | Đúng và có nguồn (MET-002) |  | Thủ công — chưa ghi nhận |  |
| QE-002 | Tỷ lệ bịa |  | Thủ công — chưa ghi nhận |  |
| QE-003 | Ngoài phạm vi hỏi tiếp trong cùng hội thoại |  | Thủ công — chưa ghi nhận |  |
| QE-004 | Độ phủ nguồn khi hỏi nhiều tài liệu |  | Thủ công — chưa ghi nhận |  |
| QE-005 | Câu hỏi tiếp theo |  | Thủ công — chưa ghi nhận |  |
| QE-006 | Đúng trang và câu trả lời có nội dung có nguồn |  | Thủ công — chưa ghi nhận |  |
| QE-007 | Kết quả theo ngôn ngữ |  | Thủ công — chưa ghi nhận |  |
| QE-008 | Đối chiếu chấm tự động với chấm tay |  | Thủ công — chưa ghi nhận |  |
| OPS-001 | Health báo lỗi khi một thành phần dừng | Trung bình | Chưa có kết quả | Theo INT-API-036: Chưa có kết quả |
| OPS-002 | Luật cảnh báo phát đúng | Trung bình | Chưa có kết quả | thiếu kết quả: test_admin_reports_health.py::test_maintenance_exports_component_health_for_alerting |
| OPS-003 | Theo dõi tài liệu xóa quá hạn | Trung bình | Chưa có kết quả | thiếu kết quả: test_delete_and_purge.py::test_overdue_deleting_documents_are_counted |
| OPS-004 | Triển khai theo tài liệu vận hành | Trung bình | Thủ công — chưa ghi nhận |  |
| OPS-005 | Khôi phục sao lưu không "hồi sinh" tài liệu đã xóa | Trung bình | Thủ công — chưa ghi nhận |  |
