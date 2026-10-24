# Kiểm tra cổng launch (T4-06) — LG-01..LG-11

| Mục | Nội dung |
|---|---|
| Ngày kiểm | 2026-10-23 |
| Phiên bản mã | Nhánh `main`, chưa commit (thay đổi đang ở cây làm việc) |
| Môi trường | Docker Compose cục bộ (`deploy/docker-compose.yml` + `docker-compose.e2e.yml`) |
| Kết luận | **Chưa đủ điều kiện phát hành.** Các mục về mã và kiểm thử tự động đạt; các mục phụ thuộc quyết định của stakeholder, dữ liệu thật và khóa API chưa đạt |

## Kết quả các lần chạy tự động

| Bộ kiểm tra | Kết quả | Lệnh |
|---|---|---|
| Backend: ruff, mypy (strict), import-linter | Sạch; 2/2 hợp đồng import giữ | `scripts/backend-docker.sh` |
| Backend: unit + tích hợp (PostgreSQL pgvector, S3 thật) + bảo mật | **183 đạt**, 1 bỏ qua (cần `ANTHROPIC_API_KEY`) | `scripts/backend-docker.sh` |
| Frontend: eslint, tsc, Vitest (Testing Library + axe-core) | **79 đạt** | `cd frontend && npm run lint && npm run typecheck && npm test` |
| E2E Playwright (Chromium, axe WCAG 2.1 AA) | **19 đạt** | `cd e2e && npx playwright test` |
| Bộ đánh giá: kiểm thử công thức chỉ số | 12 đạt | `cd evaluation && pytest` |
| Luật cảnh báo Prometheus | `promtool test rules`: SUCCESS | `deploy/monitoring/alerts_test.yml` |
| Bộ đánh giá qua API (luồng đầu-cuối, adapter giả) | 59 câu, 0 lỗi gọi, đúng trang 100% | `evaluation/reports/v1-20261023T130536Z.md` |

## Từng tiêu chí

| LG | Tiêu chí (PRD 5.1) | Trạng thái | Bằng chứng / lý do | Người chịu trách nhiệm | Hạn |
|---|---|---|---|---|---|
| LG-01 | 100% AC của story P0 đạt | **Đạt một phần** | AC-001..006, 009, 012, 014, 018..020, 023, 024 có kiểm thử tự động đạt (bảng truy vết bên dưới). AC-010 (ngôn ngữ), AC-013 (chất lượng), AC-015 (bảo mật) phụ thuộc LG-02, LG-06 | Trưởng nhóm QA | Trước G4 |
| LG-02 | Đúng và có nguồn ≥ [TBD: OQ-002] | **Không đạt (chưa đo)** | Ngưỡng chưa chốt (OQ-002); chưa chạy với embedding thật + Claude (thiếu khóa API, máy phát triển không đủ đĩa cho bge-m3). Khung và bộ câu hỏi v1 (bản nháp) sẵn sàng | Chủ sản phẩm (OQ-002), kỹ sư AI | G3 |
| LG-03 | Tỷ lệ bịa ≤ [TBD: OQ-002] | **Không đạt (chưa đo)** | Như LG-02. Ghi nhận rủi ro "câu ngoài phạm vi hỏi tiếp trong cùng hội thoại" ở `tuning_log.md` | Kỹ sư AI | G3 |
| LG-04 | 100% câu trả lời có nội dung nêu đúng tài liệu và trang | **Đạt về cơ chế, chờ đo với mô hình thật** | Lớp từ chối 3 (`modules/qa/service.py`): không có citation hợp lệ → "không tìm thấy"; kiểm thử `test_answer_has_source_document_and_page` (cited_text có trong trang); bộ đánh giá qua API: đúng trang 100% (56/56) | Kỹ sư AI | G3 |
| LG-05 | Thời gian phản hồi ≤ [TBD] ở [TBD]% câu | **Không đạt (chưa đo)** | Đo được: span OpenTelemetry + `qa_step_seconds`, `answer_latency_seconds`; `ANSWER_TIMEOUT_S` → 504. Chưa có ngưỡng (OQ-002) và chưa đo với Claude | Chủ sản phẩm, DevOps | G3 |
| LG-06 | Bảo mật xác nhận bằng văn bản | **Không đạt** | Hồ sơ `data_handling.md` đã soạn; kiểm thử canary "log không chứa nội dung" đạt. **Chờ bộ phận bảo mật rà soát và ký**; OQ-005, OQ-006, AQ-003, PQ-004 còn mở | Bộ phận bảo mật | G4 |
| LG-07 | Kiểm tra quyền | **Đạt** | `tests/security/test_auth_matrix.py` (mọi route tự sinh từ OpenAPI: 401 khi không có phiên, 403 ở `/admin/*` với bd/manager), `test_isolation.py` (A/B: không hỏi ra, không xem/xóa/thử lại, 404 mọi route tài nguyên), `test_revoked_user_loses_access_on_next_request` (AC-014), E2E thu hồi quyền | Trưởng nhóm QA | Xong |
| LG-08 | Xóa đúng cả ở truy vấn và nơi lưu | **Đạt** (sao lưu: rủi ro mở AQ-003) | `test_deleted_document_is_excluded_immediately` (AC-005, trước khi worker chạy), `test_purge_removes_chunks_file_and_sets_purged_at` (AC-024), lỗi kho giữa chừng được thử lại, E2E xóa → "không tìm thấy" | DevOps (AQ-003) | G4 |
| LG-09 | Không còn lỗi nghiêm trọng/cao; độ phủ kiểm thử đạt [TBD] | **Đạt một phần** | Không có lỗi mở đã biết. Hai lỗi nghiêm trọng phát hiện ở E2E đã sửa và có kiểm thử hồi quy (commit sau phản hồi; thiếu model ở tiến trình API). Ngưỡng độ phủ chưa chốt (OQ-002); chưa đo coverage | Trưởng nhóm QA | G4 |
| LG-10 | Bộ câu hỏi chuẩn và tập PDF mẫu thật từ business owner | **Không đạt** | Chỉ có bộ tổng hợp không nhạy cảm (`evaluation/spikes/corpus`) và `v1.jsonl` bản nháp (59 câu). DEP-001, ASM-005 chưa có | Business owner | G3 |
| LG-11 | Sponsor xác nhận đã chốt OQ-001..OQ-007 | **Không đạt** | Các giá trị đang dùng là tạm thời (`ops_runbook.md` mục 4) | Sponsor | G4 |

## Khả năng tiếp cận (T4-08)

- axe (WCAG 2.1 A/AA, mức nghiêm trọng và cao) trên S-01, S-02 (trống, có tài liệu, có câu trả lời), S-03, S-04, S-05, S-06, S-07: **không có vi phạm** (E2E `a11y.spec.ts`, `qa.spec.ts`, `documents.spec.ts`, `auth.spec.ts`).
- Phát hiện và đã sửa: chip nguồn có tên truy cập không chứa chữ hiển thị (WCAG 2.5.3).
- Bàn phím: liên kết bỏ qua → đăng nhập chỉ bằng bàn phím (E2E); hộp thoại xóa giữ tiêu điểm, Esc đóng và trả tiêu điểm (Vitest + E2E).
- Thu phóng 200%: nút tải lên và ô nhập vẫn dùng được (E2E).
- **Còn phải làm thủ công:** kiểm với trình đọc màn hình (NVDA/VoiceOver), tương phản trên trình duyệt thật cho mọi trạng thái (axe trong jsdom không kiểm tương phản; axe trong Playwright đã kiểm cho các màn hình trên). Người phụ trách: QA, trước G4.

## Đối chiếu ảnh màn hình

Ảnh giao diện thật: `docs/implement/evidence/screenshots/` (s01-default, s01-wrong, s02-default, s02-empty, s04-default, s05-default, s06-default, s07-default), so với `docs/design/html_design/screenshots/`. Bố cục, màu, nhãn trạng thái khớp. Khác biệt có chủ đích: chữ hướng dẫn dưới nút tải lên hiển thị giới hạn thật từ cấu hình thay cho nhãn `OQ-004`; ô nhập có bộ đếm ký tự.

## Truy vết AC → kiểm thử tự động

| AC | Kiểm thử |
|---|---|
| AC-001 | `test_valid_pdf_becomes_ready_with_paged_chunks`; E2E `documents.spec` "tải PDF hợp lệ" |
| AC-002 | `test_mixed_upload_each_file_judged_independently`, `test_many_files_with_two_concurrent_workers` |
| AC-003 | `test_worker_failure_reasons`, `test_mixed_upload...`; E2E "tải tệp hỏng", "mất mạng khi tải lên" |
| AC-004 | `test_user_cannot_see_or_touch_other_users_documents`, `test_isolation.py` |
| AC-005 | `test_deleted_document_is_excluded_immediately`; E2E `delete-audit.spec` |
| AC-006 | `test_answer_has_source_document_and_page`; E2E `qa.spec` |
| AC-007 | `test_max_chunks_per_document`; bộ đánh giá (độ phủ nguồn) — chờ mô hình thật |
| AC-008 | `test_history_and_follow_up_question`; bộ đánh giá nhóm `follow_up` |
| AC-009 | `test_out_of_scope_question_is_not_found_without_calling_model`, ba lớp từ chối (`test_qa_service.py`); E2E |
| AC-011 | `test_timeout_returns_504`, `test_slow_generator_hits_answer_timeout`; Vitest chỉ báo chờ + Hủy |
| AC-012, AC-019 | `test_answer_has_source_document_and_page`, `test_answer_with_content_always_has_citation`; E2E S-03 tô sáng đúng trang |
| AC-014 | `test_revoked_user_loses_access_on_next_request`; E2E `auth.spec` |
| AC-016, AC-021 | `test_weekly_usage_with_seed_data`, `test_usage_endpoint_includes_helpful_ratio` |
| AC-017 | `test_feedback_is_saved_and_can_be_changed`; Vitest đánh giá |
| AC-018 | `failureMessages.test.ts`; E2E lý do lỗi |
| AC-020 | `test_isolation.py` |
| AC-022 | `test_ready_fails_when_storage_is_down`, `..._database_is_down`, `..._queue_backlog_is_old`, `test_maintenance_exports_component_health_for_alerting`, `alerts_test.yml` |
| AC-023 | `test_each_question_writes_exactly_one_audit_record_without_content`, `test_audit_lists_one_record_per_question_without_content`; E2E kiểm toán |
| AC-024 | `test_purge_removes_chunks_file_and_sets_purged_at`, `test_storage_error_midway_is_retried_and_completes` |
