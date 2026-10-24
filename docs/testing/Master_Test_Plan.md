# KẾ HOẠCH KIỂM THỬ TỔNG THỂ (MASTER TEST PLAN) — "CHAT VỚI TÀI LIỆU" (MVP)

> Chuẩn: IEEE 829-2008 (Software Test Documentation).
> Đầu vào chính: `docs/implement/implement_plan.md` (IMP-CWD-001 v0.1) — chiến lược kiểm thử (mục 9), môi trường và CI (mục 10), kế hoạch sprint và cổng quyết định (mục 7), định nghĩa hoàn thành (mục 11). Đầu vào bổ sung: `BRD.md` v0.2, `PRD.md` v0.1, `UserStories.md`, `SADD.md` v0.1, `UIUX_Blueprint.md` và giao diện mẫu `docs/design/html_design/`.
> Quy ước: `[TBD: xx]` = chờ quyết định (implement_plan.md mục 13). Mọi ngưỡng chưa chốt được kiểm bằng **giá trị cấu hình**, không viết cứng trong kịch bản kiểm thử.

---

## Phần A — Phân tích tài liệu đầu vào

### A.1 Danh mục tài liệu đầu vào

| Loại tài liệu | Tên tài liệu | Phiên bản | Nguồn | Thông tin dùng cho kiểm thử |
|---|---|---|---|---|
| Kế hoạch triển khai | `docs/implement/implement_plan.md` (IMP-CWD-001) | 0.1 Draft | Đội phát triển | Tầng kiểm thử, công cụ, dữ liệu kiểm thử, kiểm thử canary, bộ đánh giá, môi trường, CI, sprint, cổng G0–G4, DoD, biến cấu hình |
| Danh sách task | `docs/implement/implement_tasks.md`, `docs/implement/tasks/` | 0.1 | Đội phát triển | 61 task; điều kiện "Xong khi" của từng task là tiêu chí kiểm thử |
| BRD | `docs/requirements/BRD.md` | 0.2 | BA | BR-001..BR-024, AC-001..AC-024, rủi ro RSK-001..005, giả định ASM, phụ thuộc DEP |
| PRD | `docs/requirements/PRD.md` | 0.1 | Product | 24 user story, trường hợp biên (mục 4.2), tiêu chí launch LG-01..LG-11 (mục 5.1), sự kiện phân tích (mục 5.2) |
| User Stories | `docs/requirements/UserStories.md` | 0.1 | Product | Tiêu chí chấp nhận Given/When/Then, ảnh màn hình theo trạng thái |
| SAD (IEEE 1016-2009) | `docs/requirements/SADD.md` | 0.1 | Kiến trúc | Mô-đun M-01..M-13, cổng P-01..P-03, giao diện IF-01..IF-10, ADR-001..ADR-012 |
| UI/UX | `docs/design/UIUX_Blueprint.md`, `docs/design/html_design/` (S-01..S-07, 22 ảnh trạng thái) | 0.1 | Thiết kế | Thành phần C-00..C-20, trạng thái màn hình, yêu cầu khả năng tiếp cận |
| Đặc tả API | OpenAPI sinh tự động (`/api/v1/openapi.json`, `frontend/src/api/openapi.json`); implement_plan.md mục 4 | 0.1 | Đội phát triển | Endpoint, schema, mã lỗi chung |

### A.2 Yêu cầu trích từ BRD/PRD

| Mã | Loại | Mô tả (tóm tắt) | Ưu tiên | Nguồn |
|---|---|---|---|---|
| BR-001 | Chức năng | Tải một PDF vào tập truy vấn | Cao | US-001, AC-001 |
| BR-002 | Chức năng | Tải nhiều PDF trong giới hạn [TBD: OQ-004] | Cao | US-002, AC-002 |
| BR-003 | Chức năng | Báo tên tệp thất bại | Cao | US-003, AC-003 |
| BR-004 | Chức năng | Xem danh sách tài liệu của mình | Trung bình | US-005, AC-004 |
| BR-005 | Quy tắc nghiệp vụ | Tài liệu đã xóa không còn dùng để trả lời | Cao | US-006, AC-005 |
| BR-006 | Chức năng | Trả lời câu hỏi tự nhiên dựa trên tài liệu | Cao | US-008, AC-006 |
| BR-007 | Chức năng | Tổng hợp thông tin từ nhiều tài liệu | Cao | US-009, AC-007 |
| BR-008 | Chức năng | Hỏi tiếp trong cùng hội thoại | Trung bình | US-010, AC-008 |
| BR-009 | Quy tắc nghiệp vụ | Báo "không tìm thấy" thay vì bịa | Cao | US-011, AC-009 |
| BR-010 | Phi chức năng | Ngôn ngữ [TBD: OQ-007] | Cao | US-012, AC-010 |
| BR-011 | Phi chức năng (hiệu năng) | Thời gian phản hồi ≤ [TBD: OQ-002] giây | Trung bình | US-013, AC-011 |
| BR-012 | Quy tắc nghiệp vụ | Mọi câu trả lời có nội dung nêu tài liệu nguồn | Cao | US-014, AC-012 |
| BR-013 | Phi chức năng (chất lượng) | Tỷ lệ đúng và có nguồn ≥ [TBD: OQ-002] | Cao | US-016, AC-013 |
| BR-014 | Bảo mật | Chỉ người được cấp quyền dùng được ứng dụng | Cao | US-017, AC-014 |
| BR-015 | Bảo mật / tuân thủ | Xử lý dữ liệu theo chính sách [TBD: OQ-005, OQ-006] | Cao | US-019, AC-015 |
| BR-016 | Đo lường | Số người dùng hoạt động hằng tuần | Trung bình | US-022, AC-016 |
| BR-017 | Đo lường | Đánh giá hữu ích/không hữu ích | Thấp | US-024, AC-017 |
| BR-018 | Chức năng | Nêu nhóm lý do thất bại | Trung bình | US-004, AC-018 |
| BR-019 | Quy tắc nghiệp vụ | Nêu đúng số trang nguồn | Cao | US-015, AC-019 |
| BR-020 | Bảo mật | Chỉ truy vấn tài liệu trong phạm vi [TBD: OQ-003] | Cao | US-018, AC-020 |
| BR-021 | Đo lường | Số câu hỏi hằng tuần | Trung bình | US-023, AC-021 |
| BR-022 | Phi chức năng (sẵn sàng) | Mức sẵn sàng [TBD: OQ-011] | Thấp | US-021, AC-022 |
| BR-023 | Bảo mật / kiểm toán | Bản ghi ai hỏi tài liệu nào, khi nào; lưu [TBD: OQ-012] ngày | Trung bình | US-020, AC-023 |
| BR-024 | Bảo mật / tuân thủ | Xóa vĩnh viễn nội dung trong [TBD: OQ-012] | Cao | US-007, AC-024 |
| NFR-LOG | Phi chức năng (riêng tư) | Log và sự kiện không chứa nội dung tài liệu/câu hỏi | Cao | ADR-009, implement_plan 9.3 |
| NFR-ACC | Phi chức năng (tiếp cận) | WCAG 2.1 AA [Đề xuất] | Cao | implement_plan mục 11 (DoD 3) |
| NFR-CFG | Phi chức năng (vận hành) | Không ngưỡng nào viết cứng; tất cả đọc từ cấu hình | Cao | implement_plan 10.3, DoD 4 |

### A.3 Thành phần thiết kế trích từ SADD (IEEE 1016-2009)

| Góc nhìn | Thành phần | Kiểu | Giao diện | Trạng thái | Phụ thuộc |
|---|---|---|---|---|---|
| Composition | M-01 Web UI | React SPA | IF-01..IF-10 qua `/api/v1` | — | M-02 |
| Composition | M-02 API Gateway Layer | FastAPI router | REST JSON, cookie phiên | — | M-03 |
| Composition | M-03 Access & Identity | Mô-đun | `current_user`, `require_role`, `allowed_document_ids` | Phiên: hoạt động / hết hạn | P-02 |
| Composition | M-04 Document Management | Mô-đun | IF-02, IF-03, IF-04 | Tài liệu (bên dưới) | M-03, M-05, P-03 |
| Composition | M-05 Ingestion Pipeline | Worker nền | Hàng đợi `jobs` | Việc: queued → running → done/failed | P-01, P-03 |
| Composition | M-06 Question Answering | Mô-đun | IF-05 | Ba lớp từ chối | M-07, P-01 |
| Composition | M-07 Retrieval | Mô-đun | Truy vấn pgvector có lọc quyền | — | Kho vector |
| Composition | M-08 Conversation | Mô-đun | IF-05 | — | Kho metadata |
| Composition | M-09 Source Viewing | Mô-đun | IF-06 | — | M-03, P-03 |
| Composition | M-10 Feedback & Usage | Mô-đun | IF-07, IF-10 | — | Kho metadata |
| Composition | M-11 Audit | Mô-đun | IF-09 | — | Kho metadata |
| Composition | M-12 Quality Evaluation | Công cụ | `evaluation/run_eval.py` | — | M-06 |
| Composition | M-13 Cross-cutting | Nền | Log che nội dung, `/health/*`, `/metrics` | — | — |
| Interface | P-01 AI Provider | Cổng | `EmbeddingProvider`, `AnswerGenerator` | — | Claude API / mô hình nội bộ / giả lập |
| Interface | P-02 Identity | Cổng | `IdentityProvider`, `OidcClient` | — | Tài khoản nội bộ / OIDC |
| Interface | P-03 Storage | Cổng | `FileStore` | — | Kho S3 |
| State Dynamics | Tài liệu | Máy trạng thái | upload → `processing` → `ready` / `failed`; `failed` → thử lại → `processing`; `ready`/`failed` → xóa → `deleting` → `deleted` | 6 trạng thái | `documents.status` |
| Information | Lược đồ dữ liệu | PostgreSQL + pgvector | 14 bảng (implement_plan mục 3) | — | Alembic |

### A.4 Thành phần UI/UX

| Thành phần | Màn hình | Tương tác | Trạng thái cần kiểm | Tiếp cận | Luồng |
|---|---|---|---|---|---|
| C-01 AuthGate, form đăng nhập | S-01 | Nhập, gửi | mặc định, sai thông tin, không có quyền, hết phiên | nhãn trường, `role=alert` | Đăng nhập → trang theo vai trò |
| C-03 UploadControl | S-02 | Chọn nhiều tệp, kéo thả | đang tải (tiến độ), bị từ chối, chưa tải xong (mất mạng) | `progressbar` có nhãn | Tải lên → danh sách |
| C-04 DocumentList, C-06 StatusBadge | S-02 | Thử lại, Xóa | Sẵn sàng, Đang xử lý, Lỗi + lý do, trống | nhãn có chữ, không chỉ màu | Theo dõi trạng thái |
| C-05 DeleteConfirmDialog | S-04 | Hủy, Xóa vĩnh viễn, Esc | mặc định, thất bại | `alertdialog`, focus mặc định ở Hủy, bẫy tiêu điểm | Xóa → danh sách |
| C-07..C-09 ChatPanel, MessageList, QuestionInput | S-02 | Gửi (nút, Ctrl+Enter), Hủy, Hội thoại mới | trống/vô hiệu, đang chờ, mất mạng, quá thời gian, quá dài | `aria-live`, nhãn ô nhập | Hỏi → trả lời |
| C-11 AnswerCard, C-12 SourceChip, C-13 Feedback, C-15 NotFoundNotice | S-02 | Mở nguồn, đánh giá | có nguồn, không tìm thấy | `aria-pressed`, tên truy cập chứa chữ hiển thị | Trả lời → S-03 |
| C-14 SourceViewer | S-03 | Trang trước/sau, quay lại | mặc định (tô sáng), tài liệu đã xóa | tiêu đề nhận tiêu điểm | Nguồn → trang |
| C-18 AccessManager | S-05 | Cấp, thu hồi (xác nhận) | mặc định, xác nhận, trống | lỗi tại trường | Quản trị |
| C-19 AuditLogView | S-06 | Lọc, xem thêm | mặc định, trống, lỗi + thử lại | bảng có caption | Quản trị |
| C-20 UsageReportView | S-07 | Đổi khoảng thời gian | mặc định, trống, lỗi | biểu đồ kèm bảng số liệu | Quản lý |

### A.5 Endpoint API (implement_plan.md mục 4)

| Endpoint | Phương thức | Vào | Ra | Lỗi chính | Cần phiên / vai trò |
|---|---|---|---|---|---|
| `/auth/login` | POST | login, password | `{user, role, config}` + cookie | 401 `invalid_credentials`, 403 `no_access`, 429 `login_locked`, 403 `csrf_rejected` | Không |
| `/auth/oidc/login`, `/auth/oidc/callback` | GET | code, state | 302 | 400 `oidc_state_mismatch`, 401 `oidc_failed` | Không (chỉ khi AUTH_MODE=oidc) |
| `/auth/logout`, `/auth/me` | POST, GET | — | 204 / `{user, role, config}` | 401 `unauthenticated` / `session_expired` | Có |
| `/documents` | POST (multipart) | `files[]` | mỗi tệp `{id, file_name, status, failure_reason}` | `too_large`, `not_pdf`, `too_many_documents` theo từng tệp | bd |
| `/documents`, `/documents/{id}` | GET | — | danh sách / một tài liệu | 404 `document_not_found` | bd |
| `/documents/{id}/retry` | POST | — | tài liệu `processing` | 404, 409 `not_retryable` | bd |
| `/documents/{id}` | DELETE | — | 202 `deleting` | 404, 403 `not_owner` | bd (chủ) hoặc security_admin |
| `/documents/{id}/pages/{page}` | GET | — | `{page, page_count, text, document_name}` | 404 | bd |
| `/documents/{id}/file` | GET | — | PDF | 404 | bd |
| `/events/source-opened` | POST | `{document_id, page}` | 204 | 404 | bd |
| `/conversations` | POST | — | `{id}` | — | bd |
| `/conversations/{id}/messages` | POST | `{question}` | `{message_id, answer, not_found, citations, latency_ms}` | 400 `question_empty`/`question_too_long`, 404, 502 `answer_unavailable`, 504 `answer_timeout` | bd |
| `/conversations/{id}/messages` | GET | — | lịch sử | 404 | bd |
| `/messages/{id}/feedback` | PUT | `{value}` | 204 | 400, 404 | bd |
| `/admin/access` | GET, POST, DELETE `/{user_id}` | `{login, role}` | danh sách / 201 / 204 | 400 `invalid_role`, 404, 409 `cannot_revoke_self` | security_admin |
| `/admin/audit` | GET | `from, to, user, document, cursor` | `{items, next_cursor}` | — | security_admin |
| `/reports/usage` | GET | `weeks` | `{weeks:[...]}` | — | manager |
| `/health/live`, `/health/ready` | GET | — | 200 / 503 + thành phần | — | Không |

Định dạng lỗi chung: `{"error": {"code", "message"}}`, thông điệp không chứa chi tiết kỹ thuật (implement_plan.md mục 4).

### A.6 User story và tiêu chí chấp nhận

| Story | Mô tả | AC | Ưu tiên | Sprint | Phụ thuộc |
|---|---|---|---|---|---|
| US-001 | Tải một PDF | AC-001 | P0 | 1 | US-017 |
| US-002 | Tải nhiều PDF | AC-002 | P0 | 1 | US-001 |
| US-003 | Biết tệp nào thất bại | AC-003 | P0 | 1 | US-001 |
| US-004 | Lý do thất bại | AC-018 | P1 | 1 | US-003 |
| US-005 | Xem danh sách tài liệu | AC-004 | P1 | 1 | US-001 |
| US-006 | Loại tài liệu khỏi truy vấn | AC-005 | P1 | 3 | US-005, US-008 |
| US-007 | Xóa vĩnh viễn | AC-024 | P0 | 3 | US-006 |
| US-008 | Đặt câu hỏi | AC-006 | P0 | 2 | US-001 |
| US-009 | Tổng hợp nhiều tài liệu | AC-007 | P0 | 2 | US-008 |
| US-010 | Hỏi tiếp | AC-008 | P1 | 3 | US-008 |
| US-011 | Báo khi không có thông tin | AC-009 | P0 | 2 | US-008 |
| US-012 | Ngôn ngữ | AC-010 | P0 | 2 | US-008 |
| US-013 | Thời gian phản hồi | AC-011 | P1 | 3 | US-008 |
| US-014 | Biết tài liệu nguồn | AC-012 | P0 | 2 | US-008 |
| US-015 | Biết số trang | AC-019 | P0 | 2 | US-014 |
| US-016 | Chất lượng đạt ngưỡng | AC-013 | P0 | 4 | US-009, US-011, US-014 |
| US-017 | Chỉ người được cấp quyền | AC-014 | P0 | 1 | — |
| US-018 | Phạm vi tài liệu | AC-020 | P0 | 3 | US-017 |
| US-019 | Tuân thủ chính sách dữ liệu | AC-015 | P0 | 4 | US-007, US-020 |
| US-020 | Bản ghi kiểm toán | AC-023 | P1 | 3 | US-008 |
| US-021 | Mức sẵn sàng | AC-022 | P2 | 4 | — |
| US-022 | Người dùng hoạt động hằng tuần | AC-016 | P1 | 4 | US-008 |
| US-023 | Số câu hỏi hằng tuần | AC-021 | P1 | 4 | US-008 |
| US-024 | Đánh giá câu trả lời | AC-017 | P2 | 4 | US-014 |

### A.7 Đánh giá rủi ro

Thang điểm: khả năng (1–5) × tác động (1–5); ≥ 15 = cao, 8–14 = trung bình, < 8 = thấp.

| Mã | Rủi ro | Khả năng | Tác động | Điểm | Chiến lược giảm thiểu bằng kiểm thử |
|---|---|---|---|---|---|
| TR-01 (RSK-001) | AI trả lời bịa hoặc sai nguồn | 4 | 5 | 20 | Ba lớp từ chối có kiểm thử đơn vị/tích hợp; bộ đánh giá đo tỷ lệ bịa và đúng trang; kiểm "câu ngoài phạm vi hỏi tiếp trong cùng hội thoại" |
| TR-02 (RSK-002) | Lộ tài liệu giữa người dùng hoặc ra ngoài | 3 | 5 | 15 | Ma trận xác thực tự sinh từ OpenAPI; kiểm thử cô lập A/B tự sinh theo route; kiểm thử canary log; rà soát hồ sơ dữ liệu |
| TR-03 | Tài liệu đã xóa vẫn được truy xuất hoặc còn trên kho | 2 | 5 | 10 | Kiểm thử AC-005 trước khi worker chạy; AC-024 sau worker; lỗi kho giữa chừng |
| TR-04 (RSK-003) | Trích xuất sai với PDF phức tạp (bảng, nhiều cột, scan) | 4 | 3 | 12 | Bộ PDF tổng hợp có bảng, hai cột, mã hóa, scan; spike trên PDF thật (DEP-001) |
| TR-05 | Thất thoát dữ liệu do giao dịch (commit sau phản hồi, thiếu chunk) | 3 | 4 | 12 | Kiểm thử giao dịch nguyên tử của nạp; kiểm thử hồi quy "lỗi commit trả 500"; kiểm thử tiến trình API nạp đủ model |
| TR-06 | Ngưỡng chất lượng/hiệu năng chưa chốt (OQ-002) | 5 | 3 | 15 | Kiểm thử đọc ngưỡng từ cấu hình; báo cáo số đo thô; cổng G3 |
| TR-07 | Thời gian phản hồi dài, treo khi dịch vụ AI chậm | 3 | 3 | 9 | Kiểm thử hạn `ANSWER_TIMEOUT_S` → 504; nút Hủy phía giao diện; đo phân vị |
| TR-08 | Không đạt WCAG 2.1 AA | 3 | 3 | 9 | axe trong Vitest và Playwright cho mọi màn hình; kiểm thủ công trình đọc màn hình |
| TR-09 | Tài nguyên máy kiểm thử không đủ (mô hình embedding ~2,3 GB) | 4 | 2 | 8 | Embedding giả lập cho E2E/CI; chạy bộ đánh giá với mô hình thật trên máy kiểm thử riêng |
| TR-10 (RSK-005) | Chi phí gọi dịch vụ AI khi chạy bộ đánh giá | 3 | 2 | 6 | Ghi chi phí mỗi lần chạy; chỉ chạy khi đổi mô-đun liên quan |

---

## Phần B — Kế hoạch kiểm thử theo IEEE 829

| Mục | Điều khoản IEEE 829 | Nội dung |
|---|---|---|
| 1 | 5.1 | Định danh |
| 2 | 5.2 | Giới thiệu |
| 3 | 5.3 | Hạng mục kiểm thử |
| 4 | 5.4 | Tính năng được kiểm thử |
| 5 | 5.5 | Tính năng không kiểm thử |
| 6 | 5.6 | Cách tiếp cận |
| 7 | 5.7 | Tiêu chí đạt/không đạt |
| 8 | 5.8 | Tiêu chí tạm dừng và tiếp tục |
| 9 | 5.9 | Sản phẩm bàn giao của kiểm thử |
| 10 | 5.10 | Công việc kiểm thử |
| 11 | 5.11 | Nhu cầu môi trường |
| 12 | 5.12 | Trách nhiệm |
| 13 | 5.13 | Nhân sự và đào tạo |
| 14 | 5.14 | Lịch |
| 15 | 5.15 | Rủi ro và dự phòng |
| 16 | 5.16 | Phê duyệt |

## 1. Định danh kế hoạch kiểm thử

| Thuộc tính | Giá trị |
|---|---|
| Mã tài liệu | CWD-MTP-001 |
| Phiên bản | 0.1 |
| Ngày | 2026-10-24 |
| Trạng thái | Draft — chờ rà soát |
| Phân loại | Nội bộ |
| Người soạn | Nhóm QA (soạn kèm Claude Code) |
| Người duyệt | Trưởng nhóm QA, chủ sản phẩm [TBD: OQ-008] |

## 2. Giới thiệu

### 2.1 Mục đích
- Xác định chiến lược kiểm thử tổng thể cho MVP "Chat với tài liệu".
- Xác định các tầng, loại và chu kỳ kiểm thử; vai trò, trách nhiệm, lịch.
- Đặt tiêu chí vào/ra cho từng giai đoạn và cho các cổng G0–G4.
- Xác định công cụ, môi trường, dữ liệu kiểm thử.
- Bảo đảm truy vết từ yêu cầu (BR/AC/US) tới ca kiểm thử và tới mã kiểm thử tự động.

### 2.2 Phạm vi

**Trong phạm vi**
- Chức năng: đăng nhập và phân quyền, nạp và quản lý tài liệu, hỏi đáp có nguồn, trình xem nguồn, xóa và xóa vĩnh viễn, kiểm toán, báo cáo sử dụng, đánh giá câu trả lời.
- API: mọi endpoint ở mục A.5, kể cả mã lỗi và định dạng lỗi chung.
- Giao diện: S-01..S-07 và mọi trạng thái trong ảnh mẫu.
- Phi chức năng: chất lượng câu trả lời (bộ đánh giá), thời gian phản hồi, bảo mật (xác thực, phân quyền, cô lập, CSRF, CSP), riêng tư (log không chứa nội dung), khả năng tiếp cận, sẵn sàng/giám sát.
- Tích hợp: PostgreSQL + pgvector, kho S3, worker và hàng đợi, Claude API (Kịch bản A), IdP OIDC (nếu DQ-003 chọn).
- Kiểm thử đầu-cuối, hồi quy, chấp nhận (theo AC và LG-01..LG-11).

**Ngoài phạm vi**
- Kiểm thử chất lượng nội tại của mô hình Claude và hạ tầng Anthropic (trách nhiệm nhà cung cấp); chỉ kiểm cách hệ thống dùng nó.
- PDF dạng ảnh scan / OCR (ADR-010: chưa hỗ trợ; chỉ kiểm thông báo `no_text`).
- Kiểm thử xâm nhập chuyên sâu (bộ phận bảo mật thực hiện riêng trong rà soát US-019).
- Tải vượt quy mô MVP (OQ-009 chưa chốt; xem mục 6.1.6).
- Kịch bản B (mô hình tự vận hành) cho tới khi OQ-006 chọn — khi đó chạy lại toàn bộ bộ đánh giá (ADR-012).
- Endpoint SSE `messages:stream` (chỉ làm nếu AQ-006 chọn hiển thị theo luồng).

### 2.3 Mục tiêu

| Mã | Mục tiêu | Tiêu chí thành công | Truy vết |
|---|---|---|---|
| OBJ-001 | Xác nhận mọi yêu cầu chức năng | 100% AC của story P0 có kiểm thử tự động và đạt | BR-001..BR-024, LG-01 |
| OBJ-002 | Xác nhận hợp đồng API | 100% endpoint có kiểm thử dương và âm; ma trận xác thực phủ mọi route | A.5 |
| OBJ-003 | Xác nhận giao diện khớp thiết kế | Mọi trạng thái trong `html_design/screenshots/` có ca kiểm thử và ảnh đối chiếu | UI-001..UI-008 |
| OBJ-004 | Xác nhận khả năng tiếp cận | Không có vi phạm axe mức nghiêm trọng/cao trên S-01..S-07 | NFR-ACC, ACC-001..ACC-006 |
| OBJ-005 | Xác nhận chất lượng câu trả lời | MET-002 ≥ [TBD: OQ-002], tỷ lệ bịa ≤ [TBD: OQ-002], đúng trang 100% | BR-009, BR-012, BR-013, BR-019, LG-02..LG-04 |
| OBJ-006 | Xác nhận hiệu năng | Phân vị thời gian phản hồi ≤ [TBD: OQ-002] | BR-011, LG-05 |
| OBJ-007 | Xác nhận bảo mật và riêng tư | Không có lỗ hổng mức nghiêm trọng/cao; kiểm thử canary đạt; bộ phận bảo mật xác nhận | BR-014, BR-015, BR-020, NFR-LOG, LG-06, LG-07 |
| OBJ-008 | Xác nhận xóa dữ liệu | Không còn chunk, tệp, đoạn trích sau xóa vĩnh viễn | BR-005, BR-024, LG-08 |

### 2.4 Tài liệu tham chiếu

| Tài liệu | Phiên bản | Nguồn |
|---|---|---|
| `docs/implement/implement_plan.md` | 0.1 | Đội phát triển |
| `docs/implement/implement_tasks.md`, `docs/implement/tasks/` | 0.1 | Đội phát triển |
| `docs/requirements/BRD.md` | 0.2 | BA |
| `docs/requirements/PRD.md` | 0.1 | Product |
| `docs/requirements/UserStories.md` | 0.1 | Product |
| `docs/requirements/SADD.md` | 0.1 | Kiến trúc |
| `docs/design/UIUX_Blueprint.md`, `docs/design/html_design/` | 0.1 | Thiết kế |
| `docs/implement/launch_checklist.md`, `data_handling.md`, `ops_runbook.md` | 0.1 | QA, vận hành |
| IEEE 829-2008 | 2008 | IEEE |
| WCAG 2.1 | 2018 | W3C |

## 3. Hạng mục kiểm thử

### 3.1 Phần mềm được kiểm thử

| Mã | Hạng mục | Vị trí | Thành phần |
|---|---|---|---|
| SI-001 | Backend API (FastAPI) | `backend/app/api`, `app/main.py` | M-02, M-13 |
| SI-002 | Mô-đun nghiệp vụ | `backend/app/modules/*` | M-03..M-11 |
| SI-003 | Worker nền và hàng đợi | `backend/app/worker`, `modules/jobs` | M-05, xóa vĩnh viễn, việc định kỳ |
| SI-004 | Adapter | `backend/app/adapters/*` | Claude, embedding nội bộ/giả lập, S3, tài khoản nội bộ, OIDC |
| SI-005 | Lược đồ cơ sở dữ liệu | `backend/alembic/versions/0001..0005` | 14 bảng, ràng buộc CHECK, chỉ mục HNSW |
| SI-006 | Ứng dụng web (React) | `frontend/src` | M-01, C-00..C-20 |
| SI-007 | Cấu hình và triển khai | `deploy/` (compose, Dockerfile, nginx, giám sát), `backend/app/config.py` | Biến cấu hình mục 10.3 |
| SI-008 | Bộ đánh giá chất lượng | `evaluation/run_eval.py`, `datasets/` | M-12 |
| SI-009 | Tài liệu vận hành và dữ liệu | `docs/implement/ops_runbook.md`, `data_handling.md` | US-019, T4-07 |

### 3.2 Tạo phẩm kiểm thử

| Mã | Tạo phẩm | Định dạng | Vị trí |
|---|---|---|---|
| TA-001 | Kiểm thử đơn vị backend | pytest | `backend/tests/unit` |
| TA-002 | Kiểm thử tích hợp backend | pytest + PostgreSQL/S3 thật | `backend/tests/integration` |
| TA-003 | Kiểm thử bảo mật | pytest | `backend/tests/security` |
| TA-004 | Kiểm thử thành phần giao diện | Vitest + Testing Library + axe-core | `frontend/src/**/*.test.tsx` |
| TA-005 | Kiểm thử đầu-cuối | Playwright + @axe-core/playwright | `e2e/tests` |
| TA-006 | Bộ PDF tổng hợp cho kiểm thử | Sinh lúc chạy (reportlab) | `backend/tests/pdf_factory.py`, `e2e/tests/pdf.ts` |
| TA-007 | Bộ PDF tổng hợp có đáp án | PDF + `ground_truth.json` | `evaluation/spikes/make_corpus.py` |
| TA-008 | Bộ câu hỏi chuẩn | JSONL | `evaluation/datasets/sample.jsonl`, `v1.jsonl` (bản nháp) |
| TA-009 | Adapter giả lập | Python | `adapters/fake_llm.py`, `adapters/hash_embedding.py`, IdP giả trong kiểm thử |
| TA-010 | Cấu hình môi trường kiểm thử | Docker Compose | `deploy/docker-compose.e2e.yml`, `scripts/backend-docker.sh` |
| TA-011 | Luật cảnh báo và kiểm thử luật | YAML | `deploy/monitoring/alerts.yml`, `alerts_test.yml` |

## 4. Tính năng được kiểm thử

### 4.1 Ma trận ưu tiên (theo rủi ro)

| Ưu tiên | Tính năng | Story | Yêu cầu | Điểm rủi ro |
|---|---|---|---|---|
| Cao | F-04 Hỏi đáp có nguồn, ba lớp từ chối | US-008, 009, 011, 014, 015 | BR-006, 007, 009, 012, 019 | 95 |
| Cao | F-01 Xác thực, phân quyền, phạm vi tài liệu | US-017, US-018 | BR-014, BR-020 | 90 |
| Cao | F-06 Xóa và xóa vĩnh viễn | US-006, US-007 | BR-005, BR-024 | 85 |
| Cao | F-10 Riêng tư dữ liệu (log, hồ sơ) | US-019 | BR-015, NFR-LOG | 85 |
| Cao | F-02 Nạp tài liệu | US-001..US-004 | BR-001..003, BR-018 | 75 |
| Trung bình | F-11 Chất lượng (bộ đánh giá) | US-016, US-012 | BR-010, BR-013 | 70 |
| Trung bình | F-05 Trình xem nguồn | US-015 | BR-019 | 65 |
| Trung bình | F-07 Hội thoại, hỏi tiếp | US-010 | BR-008 | 60 |
| Trung bình | F-08 Kiểm toán | US-020 | BR-023 | 60 |
| Trung bình | F-12 Thời gian phản hồi | US-013 | BR-011 | 55 |
| Trung bình | F-03 Danh sách tài liệu | US-005 | BR-004 | 45 |
| Thấp | F-09 Báo cáo và đánh giá | US-022..US-024 | BR-016, 017, 021 | 35 |
| Thấp | F-13 Sẵn sàng, giám sát | US-021 | BR-022 | 30 |

### 4.2 Ma trận tính năng × loại kiểm thử

| Tính năng | Đơn vị | Tích hợp | Hệ thống (E2E) | Chấp nhận | Hồi quy | Hiệu năng | Bảo mật | Tiếp cận |
|---|---|---|---|---|---|---|---|---|
| F-01 Xác thực, phân quyền | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ |
| F-02 Nạp tài liệu | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| F-03 Danh sách tài liệu | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| F-04 Hỏi đáp có nguồn | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| F-05 Trình xem nguồn | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ |
| F-06 Xóa, xóa vĩnh viễn | – | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ |
| F-07 Hội thoại | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ |
| F-08 Kiểm toán | – | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ |
| F-09 Báo cáo, đánh giá | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ |
| F-10 Riêng tư dữ liệu | ✓ | ✓ | – | ✓ (rà soát) | ✓ | – | ✓ | – |
| F-11 Chất lượng | ✓ (công thức) | – | – | ✓ | ✓ (bộ đánh giá) | – | – | – |
| F-12 Thời gian phản hồi | ✓ | ✓ | ✓ | ✓ | – | ✓ | – | ✓ |
| F-13 Sẵn sàng, giám sát | ✓ | ✓ | – | ✓ | ✓ | – | – | – |

### 4.3 Mô tả tính năng

| Mã | Tính năng | Mô tả | Điểm kiểm | AC |
|---|---|---|---|---|
| F-01 | Xác thực, phân quyền | Tài khoản nội bộ (Argon2id, khóa sau 5 lần sai/15 phút), OIDC + PKCE (tùy DQ-003), phiên phía máy chủ hết hạn sau `SESSION_IDLE_HOURS`, vai trò bd/manager/security_admin, CSRF theo `Origin`, cấp/thu hồi quyền, `allowed_document_ids` | Đăng nhập, hết phiên, thu hồi, sai vai trò, cô lập A/B | AC-014, AC-020 |
| F-02 | Nạp tài liệu | Kiểm tra từng tệp (`%PDF-`, `MAX_FILE_BYTES`, `MAX_DOCS_PER_USER`), lưu S3, worker trích xuất theo trang (NFC), chunk không vượt trang, embedding, ghi nguyên tử | Hợp lệ, nhiều tệp, từng lý do lỗi, thử lại, hai worker | AC-001..003, AC-018 |
| F-03 | Danh sách tài liệu | Chỉ tài liệu trong phạm vi, không trả `deleting`/`deleted`, hỏi định kỳ khi còn `processing` | Hiển thị, 200 mục, cô lập | AC-004 |
| F-04 | Hỏi đáp có nguồn | Truy xuất lọc quyền trong SQL, chỉ `ready`; lớp 1 dưới ngưỡng không gọi mô hình; lớp 2 câu từ chối cố định; lớp 3 không có citation hợp lệ; gộp citation trùng; kiểm toán trước khi gọi AI | Có nguồn, không tìm thấy, nhiều tài liệu, lỗi/hết giờ | AC-006, 007, 009, 012 |
| F-05 | Trình xem nguồn | Văn bản trang, "Trang N / M", tô sáng `cited_text`, 404 khi tài liệu đã xóa | Đúng trang, tô sáng, đã xóa | AC-019 |
| F-06 | Xóa | `deleting` ngay trong giao dịch; worker xóa chunk, đoạn trích, tệp, đặt `deleted` + `purged_at`; cảnh báo quá `PURGE_SLA_HOURS` | Loại khỏi truy vấn ngay, xóa vĩnh viễn, lỗi giữa chừng | AC-005, AC-024 |
| F-07 | Hội thoại | `HISTORY_TURNS` lượt gần nhất, truy vấn ghép câu trước, lịch sử trong phiên, hội thoại mới, dọn sau `MESSAGE_RETENTION_DAYS` | Hỏi tiếp, khôi phục, cô lập | AC-008 |
| F-08 | Kiểm toán | Một bản ghi mỗi câu hỏi, không nội dung; lọc ngày/người/tài liệu; con trỏ; dọn sau `AUDIT_RETENTION_DAYS` | Đúng một bản ghi, lọc, quyền | AC-023 |
| F-09 | Báo cáo, đánh giá | Người dùng hoạt động (BD) và số câu hỏi theo tuần ISO; tỷ lệ hữu ích; đánh giá ghi đè được | Dữ liệu hạt giống, vai trò | AC-016, 017, 021 |
| F-10 | Riêng tư | Log JSON lọc trường nội dung; không ghi thân yêu cầu; bảng sự kiện/kiểm toán không có cột nội dung | Canary | AC-015 |
| F-11 | Chất lượng | Bộ đánh giá: MET-002, tỷ lệ bịa, độ phủ nguồn, hỏi tiếp, đúng trang, theo ngôn ngữ | Báo cáo đạt ngưỡng | AC-010, AC-013 |
| F-12 | Thời gian phản hồi | Span từng bước, `answer_latency_seconds`, `ANSWER_TIMEOUT_S` → 504, chỉ báo chờ ≤ 300 ms, Hủy | Phân vị, hết giờ | AC-011 |
| F-13 | Sẵn sàng | `/health/ready` (CSDL, kho tệp, hàng đợi), số liệu `component_up`, luật cảnh báo | Dừng thành phần → cảnh báo | AC-022 |

## 5. Tính năng không kiểm thử

| Mã | Tính năng | Lý do | Rủi ro | Kế hoạch |
|---|---|---|---|---|
| NT-01 | OCR cho PDF scan | Không thuộc MVP (ADR-010) | Trung bình (RSK-003) | Chỉ kiểm thông báo `no_text`; xem xét sau MVP |
| NT-02 | Hiển thị theo luồng (SSE) | Chờ AQ-006 | Thấp | Thêm ca kiểm thử nếu được chọn |
| NT-03 | Kịch bản B (mô hình nội bộ) | Chờ OQ-006 | Trung bình | Chạy lại toàn bộ bộ đánh giá khi đổi adapter |
| NT-04 | Chia sẻ tài liệu giữa người dùng (`document_acl`) | Chờ OQ-003; bảng để trống, chưa có endpoint ghi | Cao nếu mở | Thêm ca cô lập theo ACL khi OQ-003 chốt |
| NT-05 | Người dùng nhiều vai trò | Chờ DQ-002 | Thấp | Bổ sung khi chốt |
| NT-06 | Kiểm thử tải quy mô lớn | Quy mô người dùng chưa chốt (OQ-009) | Thấp | Kiểm thử tải nhẹ (PERF-001..004) |
| NT-07 | Chất lượng mô hình Claude | Trách nhiệm nhà cung cấp | — | Chỉ đo kết quả đầu-cuối qua bộ đánh giá |

## 6. Cách tiếp cận

### 6.1 Tầng và loại kiểm thử

Theo implement_plan.md mục 9.1:

| Tầng | Công cụ | Phạm vi | Chạy khi |
|---|---|---|---|
| Đơn vị | pytest, Vitest | Chunk theo trang, ánh xạ citation, ba lớp từ chối, `allowed_document_ids`, thông báo lỗi | Mỗi commit |
| Tích hợp | pytest + PostgreSQL (pgvector) và S3 thật (testcontainers hoặc compose); adapter AI **giả lập** | Endpoint, worker, giao dịch, xóa | Mỗi pull request |
| Bảo mật | pytest | 401/403/404 mọi endpoint, cô lập A/B, log không chứa nội dung | Mỗi pull request |
| Đầu-cuối | Playwright + axe | Kịch bản theo AC P0 trên giao diện thật | Hằng đêm và trước phát hành |
| Đánh giá chất lượng | `evaluation/run_eval.py` với adapter AI thật | MET-002, tỷ lệ bịa, độ trễ | Khi đổi chỉ dẫn, tham số, mô hình; trước phát hành |

#### 6.1.1 Kiểm thử đơn vị

| Thuộc tính | Mô tả |
|---|---|
| Đội phụ trách | Phát triển (backend, frontend) |
| Công cụ | pytest (+ pytest-cov), Vitest + Testing Library + axe-core |
| Mục tiêu độ phủ | [TBD: OQ-002] cho LG-09; đề xuất ≥ 80% dòng lệnh ở `app/modules` |
| Tiêu chí vào | Mã hoàn thành, qua ruff/mypy (strict)/eslint/tsc, import-linter |
| Tiêu chí ra | 100% kiểm thử đơn vị đạt |
| Trọng tâm | Hàm thuần: trích xuất, chunk, ba lớp từ chối, ánh xạ citation, ghép truy vấn, thông báo lỗi, định dạng, xử lý phản hồi Claude |
| Giả lập | Adapter AI giả lập (`fake_llm`, `hash_embedding`), phản hồi SDK Claude giả, IdP OIDC giả (httpx MockTransport), `fetch`/`XMLHttpRequest` giả ở frontend |

**Ca kiểm thử đơn vị chính**

| Mã | Đối tượng | Mô tả | Kết quả mong đợi | Truy vết |
|---|---|---|---|---|
| UT-001 | Trích xuất PDF | PDF nhiều trang | Số trang bắt đầu từ 1, đúng thứ tự | BR-019 |
| UT-002 | Trích xuất PDF | Văn bản tiếng Việt dạng NFD | Kết quả ở dạng NFC, giữ đủ dấu | BR-010 |
| UT-003 | Trích xuất PDF | PDF có mật khẩu / hỏng / chỉ ảnh | `encrypted` / `corrupted` / `no_text` | BR-018 |
| UT-004 | Chunk | Nhiều trang | Không chunk nào chứa văn bản của hai trang; ordinal liên tục | BR-019 |
| UT-005 | Chunk | Trang ngắn, trang rỗng | Đúng một chunk; không sinh chunk | — |
| UT-006 | Chunk | Ghép phần không chồng lấp | Bằng đúng văn bản trang; tôn trọng `CHUNK_TOKENS`/`CHUNK_OVERLAP` | NFR-CFG |
| UT-007 | Hỏi đáp | Điểm dưới `MIN_RELEVANCE_SCORE` hoặc không có chunk | `not_found`, **không gọi** mô hình | BR-009 |
| UT-008 | Hỏi đáp | Mô hình trả câu từ chối cố định (khác khoảng trắng, dấu nháy) | `not_found` | BR-009 |
| UT-009 | Hỏi đáp | Có nội dung, không có citation / chỉ số sai | `not_found` | BR-012 |
| UT-010 | Hỏi đáp | Citation trùng (cùng tài liệu, trang) | Gộp, giữ thứ tự xuất hiện | BR-012 |
| UT-011 | Hỏi đáp | Lịch sử hội thoại | Truy vấn = câu trước + câu hiện tại | BR-008 |
| UT-012 | Adapter Claude | Phản hồi nhiều khối text/thinking có citation | Citation ánh xạ đúng `document_index` | BR-012 |
| UT-013 | Adapter Claude | `stop_reason = refusal` / `max_tokens` | `refused` / lỗi; đọc trước nội dung | — |
| UT-014 | Adapter Claude | Hình dạng yêu cầu | `output_config.effort`, không `thinking`, không prefill, không `format`; system có `cache_control`; beta fallback | implement_plan 6.4 |
| UT-015 | Adapter OIDC | ID token sai nonce/aud/iss/hết hạn | Từ chối | BR-014 |
| UT-016 | Khung | Lỗi chưa xử lý | 500, định dạng lỗi chung, không lộ stack trace | implement_plan 4 |
| UT-017 | Khung | Log của yêu cầu có trường `question` | Giá trị không xuất hiện trong log | NFR-LOG |
| UT-018 | Khung | Tiến trình API chỉ import `app.main` | Mọi model nạp đủ, khóa ngoại phân giải được | TR-05 |
| UT-019 | Cấu hình | Mọi ngưỡng ở mục 10.3 | Là trường cấu hình | NFR-CFG |
| UT-020 | Frontend | Bảng thông báo lỗi tải lên | Mỗi mã một câu; mã lạ → câu chung | BR-018, AC-018 |
| UT-021 | Frontend | Tô sáng đoạn trích | Khớp linh hoạt khoảng trắng; không thấy → không tô sáng | BR-019 |
| UT-022 | Bộ đánh giá | Công thức MET-002, tỷ lệ bịa, độ phủ, đúng trang, phân vị | Đúng trên dữ liệu đã biết | BR-013 |

#### 6.1.2 Kiểm thử tích hợp

| Thuộc tính | Mô tả |
|---|---|
| Đội phụ trách | Phát triển, QA |
| Công cụ | pytest + FastAPI TestClient; PostgreSQL 16 + pgvector 0.8, kho S3 thật; adapter AI giả lập |
| Phạm vi | Endpoint, worker, hàng đợi, giao dịch, migration, xóa |
| Tiêu chí vào | Kiểm thử đơn vị đạt; migration `upgrade head` chạy được |
| Tiêu chí ra | 100% đạt; thời gian chạy trong CI ≤ [Đề xuất: 5 phút] cho luồng nạp (T1-20) |
| Trọng tâm | Hợp đồng API, luồng dữ liệu, lọc quyền trong SQL, giao dịch nguyên tử, xử lý lỗi, thử lại |

**Ca kiểm thử API tích hợp**

| Mã | Endpoint | Loại | Kiểm tra | Kết quả mong đợi |
|---|---|---|---|---|
| INT-API-001 | `POST /auth/login` | Dương | Đúng mật khẩu, có quyền | 200, cookie `HttpOnly; SameSite=Lax`, `{user, role, config}` |
| INT-API-002 | `POST /auth/login` | Âm | Sai mật khẩu; tài khoản không tồn tại | Cùng 401 `invalid_credentials`, cùng thông điệp |
| INT-API-003 | `POST /auth/login` | Âm | Đúng mật khẩu, không có quyền | 403 `no_access`, không đặt cookie |
| INT-API-004 | `POST /auth/login` | Âm | Thiếu/sai `Origin` | 403 `csrf_rejected` |
| INT-API-005 | `GET /auth/me` | Âm | Phiên quá `SESSION_IDLE_HOURS` | 401 `session_expired` |
| INT-API-006 | Mọi route bd | Âm | Người bị thu hồi gọi lại | 401/403 ở yêu cầu kế tiếp |
| INT-API-007 | `POST /documents` | Dương/âm | 1 PDF hợp lệ + 1 `.txt` đổi đuôi + 1 tệp quá lớn | Từng tệp: `processing` / `not_pdf` / `too_large` |
| INT-API-008 | `POST /documents` | Biên | Vượt `MAX_DOCS_PER_USER` | Tệp vượt: `too_many_documents` |
| INT-API-009 | Worker nạp | Dương | PDF 3 trang | `ready`, `page_count=3`, chunk có `page` 1..3, vector đúng `EMBEDDING_DIM` |
| INT-API-010 | Worker nạp | Âm | PDF mã hóa / hỏng / scan | `failed` + `encrypted` / `corrupted` / `no_text`, không có chunk |
| INT-API-011 | Worker nạp | Lỗi tạm thời | Kho tệp lỗi liên tục | Thử lại tới `JOB_MAX_ATTEMPTS`, rồi `failed/internal` |
| INT-API-012 | Worker nạp | Đồng thời | Tài liệu chuyển `deleting` khi đang nạp | Kết quả bị bỏ, không ghi chunk |
| INT-API-013 | Hàng đợi | Đồng thời | 4 worker, 40 việc | Không việc nào bị lấy hai lần |
| INT-API-014 | `POST /documents/{id}/retry` | Dương/âm | `failed` / `ready` | 200 `processing` / 409 `not_retryable` |
| INT-API-015 | Truy xuất | Bảo mật | Chunk của tài liệu ngoài danh sách được phép | Không bao giờ xuất hiện |
| INT-API-016 | Truy xuất | Trạng thái | Tài liệu `deleting`/`deleted`/`processing`/`failed` | Không được truy xuất |
| INT-API-017 | Truy xuất | Biên | Danh sách được phép nhỏ trong kho lớn (HNSW) | Vẫn đủ `TOP_K` kết quả |
| INT-API-018 | Truy xuất | Cấu hình | `MAX_CHUNKS_PER_DOC` | Không tài liệu nào vượt giới hạn |
| INT-API-019 | `POST /conversations/{id}/messages` | Dương | Câu hỏi có đáp án | `not_found=false`, citation đúng tài liệu và trang, `cited_text` có trong trang |
| INT-API-020 | `POST .../messages` | Âm | Câu ngoài phạm vi | `not_found=true`, mô hình không được gọi |
| INT-API-021 | `POST .../messages` | Âm | Rỗng / dài hơn `MAX_QUESTION_CHARS` | 400 `question_empty` / `question_too_long` |
| INT-API-022 | `POST .../messages` | Lỗi | Mô hình từ chối / chậm hơn `ANSWER_TIMEOUT_S` | 502 `answer_unavailable` / 504 `answer_timeout` |
| INT-API-023 | `POST .../messages` | Kiểm toán | Mỗi câu hỏi | Đúng một `audit_records`, một `question_submitted`, không nội dung |
| INT-API-024 | `POST .../messages` | Giao dịch | Lỗi commit | 500, không trả 200 khi dữ liệu không được lưu |
| INT-API-025 | `GET .../messages` | Dương | Hỏi tiếp | Lịch sử đúng thứ tự, đúng `HISTORY_TURNS` gửi cho mô hình |
| INT-API-026 | `GET /documents/{id}/pages/{page}` | Âm | Trang 0 / vượt `page_count` / tài liệu người khác | 404 |
| INT-API-027 | `GET /documents/{id}/file` | Dương | Tài liệu của mình | 200 `application/pdf`, `Cache-Control: private, no-store` |
| INT-API-028 | `DELETE /documents/{id}` | Dương | Chủ sở hữu | 202, câu hỏi về nội dung đó → `not_found` **trước khi worker chạy** |
| INT-API-029 | Worker xóa | Dương | Sau khi worker chạy | Không còn chunk, tệp trên S3, `cited_text` = null, `purged_at` có giá trị |
| INT-API-030 | Worker xóa | Lỗi | Kho tệp lỗi lần đầu; chạy hai lần | Thử lại và hoàn tất; chạy lại không lỗi |
| INT-API-031 | `DELETE /documents/{id}` | Quyền | Người khác / quản lý / quản trị bảo mật | 404 / 403 / 202 |
| INT-API-032 | `PUT /messages/{id}/feedback` | Dương | Đổi giá trị | Ghi đè; người khác → 404 |
| INT-API-033 | `GET /admin/audit` | Dương | 60 bản ghi, lọc người/tài liệu/ngày, con trỏ | Đúng số lượng, không trùng, mới nhất trước |
| INT-API-034 | `GET /reports/usage` | Dương | Dữ liệu hạt giống 4 tuần | Đúng người dùng hoạt động và số câu hỏi từng tuần; tỷ lệ hữu ích |
| INT-API-035 | `/admin/access` | Dương/âm | Cấp, thu hồi, tự thu hồi, vai trò sai | 201 / 204 / 409 / 400 |
| INT-API-036 | `/health/ready` | Lỗi | Kho tệp dừng / CSDL dừng / hàng đợi tồn đọng | 503 và thành phần lỗi tương ứng |
| INT-API-037 | OIDC | Dương/âm | Có quyền / không quyền / state sai | Phiên được tạo / `?error=no_access` / 400; PKCE khớp |
| INT-API-038 | CLI | Dương | `create-admin` trên CSDL trống | Tài khoản quản trị bảo mật đăng nhập được |
| INT-API-039 | Migration | Dương | `upgrade head` → `downgrade base` → `upgrade head` | Thành công; ràng buộc CHECK, `chunks.page NOT NULL`, CASCADE đúng |
| INT-API-040 | Việc định kỳ | Dương | Hội thoại quá `MESSAGE_RETENTION_DAYS`; bản ghi quá `AUDIT_RETENTION_DAYS` | Bị xóa; dữ liệu mới giữ nguyên |

#### 6.1.3 Kiểm thử hệ thống (đầu-cuối)

| Thuộc tính | Mô tả |
|---|---|
| Đội phụ trách | QA |
| Công cụ | Playwright (Chromium), @axe-core/playwright |
| Môi trường | `docker-compose.yml` + `docker-compose.e2e.yml` (adapter AI và embedding giả lập, tài khoản mẫu) |
| Tiêu chí vào | Tích hợp đạt; giao diện ổn định |
| Tiêu chí ra | 100% kịch bản đạt; không có vi phạm axe nghiêm trọng/cao |
| Lưu ý dữ liệu | Mỗi kịch bản dùng tên tệp và từ vựng sinh ngẫu nhiên để không bị nhiễu bởi dữ liệu của lần chạy trước |

| Mã | Hành trình | Các bước | Kết quả mong đợi | AC |
|---|---|---|---|---|
| E2E-001 | Đăng nhập đúng/sai | Đăng nhập BD; đăng nhập sai mật khẩu | Vào S-02; thông báo sai thông tin chung | AC-014 |
| E2E-002 | Thu hồi quyền | Quản trị thu hồi `e2e.revoke` → người đó đăng nhập → cấp lại | Thông báo "chưa được cấp quyền" | AC-014 |
| E2E-003 | Hết phiên | Làm hỏng cookie phiên → gửi câu hỏi | Về S-01 với thông báo hết phiên; câu hỏi đang soạn được giữ | US-017 |
| E2E-004 | Trạng thái trống | Đăng nhập người chưa có tài liệu | Hướng dẫn tải PDF; ô hỏi vô hiệu kèm giải thích | AC-001 |
| E2E-005 | Tải PDF hợp lệ | Tải → chờ | "Đang xử lý" rồi "Sẵn sàng", số trang đúng | AC-001 |
| E2E-006 | Tải tệp hỏng / không phải PDF | Tải | "Lỗi" kèm lý do; không phải PDF bị từ chối ngay | AC-003, AC-018 |
| E2E-007 | Mất mạng khi tải lên | Chặn yêu cầu tải lên → Tải lại | "Chưa tải xong", không bao giờ "Sẵn sàng"; tải lại thành công | US-003 |
| E2E-008 | Hỏi đáp và trình xem nguồn | Tải → hỏi → mở chip → trang sau → quay lại → hội thoại mới → hỏi ngoài phạm vi | Câu trả lời có chip "tên, tr.N"; S-03 đúng trang, tô sáng; lịch sử còn; "không tìm thấy" | AC-006, 009, 012, 019 |
| E2E-009 | Mất mạng khi hỏi | Chặn yêu cầu hỏi → Gửi lại | Câu hỏi giữ trong ô nhập, nút "Gửi lại", không có câu trả lời dở dang | US-008 |
| E2E-010 | Xóa tài liệu | Hỏi → Xóa (Esc trả tiêu điểm) → Xóa vĩnh viễn → hỏi lại | Biến khỏi danh sách; "không tìm thấy" | AC-005 |
| E2E-011 | Quản trị và kiểm toán | Cấp → thu hồi → lọc bản ghi kiểm toán theo người dùng | Trạng thái đúng; bản ghi có tài liệu, không có nội dung câu hỏi | AC-023 |
| E2E-012 | Khả năng tiếp cận | axe trên S-01..S-07; điều hướng bàn phím; thu phóng 200% | Không vi phạm nghiêm trọng/cao; dùng được | NFR-ACC |
| E2E-013 | Ảnh màn hình đối chiếu | Chụp S-01..S-07 | Khớp bố cục và trạng thái ảnh mẫu | OBJ-003 |

#### 6.1.4 Kiểm thử chấp nhận

| Thuộc tính | Mô tả |
|---|---|
| Đội phụ trách | Chủ sản phẩm, business owner, QA, bộ phận bảo mật |
| Công cụ | Kiểm thử thủ công theo kịch bản; báo cáo bộ đánh giá; `launch_checklist.md` |
| Phạm vi | Mọi AC và LG-01..LG-11 |
| Tiêu chí vào | Kiểm thử hệ thống đạt; cổng G3 (OQ-002, bộ câu hỏi chuẩn) đã qua |
| Tiêu chí ra | Mọi AC P0 đạt; xác nhận bằng văn bản của bảo mật (LG-06) và business owner (LG-10); sponsor (LG-11) |

| Mã | Story | Kịch bản | Tiêu chí chấp nhận | Kết quả |
|---|---|---|---|---|
| UAT-001 | US-001, US-002 | BD tải 10 PDF thật của đội | Tất cả "Sẵn sàng", hỏi được | Chờ chạy |
| UAT-002 | US-003, US-004 | BD tải tệp hỏng, có mật khẩu, không phải PDF | Thông báo nêu tên tệp và lý do dễ hiểu | Chờ chạy |
| UAT-003 | US-008, US-009, US-014, US-015 | BD hỏi 10 câu thường gặp trên tài liệu thật | Câu trả lời đúng, có nguồn đúng tài liệu và trang | Chờ chạy |
| UAT-004 | US-011 | BD hỏi câu không có trong tài liệu | "Không tìm thấy", không bịa | Chờ chạy |
| UAT-005 | US-010 | BD hỏi tiếp bằng đại từ | Hiểu đúng đối tượng | Chờ chạy |
| UAT-006 | US-006, US-007 | BD xóa tài liệu rồi hỏi lại | "Không tìm thấy"; kiểm tra kho sau thời hạn | Chờ chạy |
| UAT-007 | US-017, US-018 | Quản trị cấp/thu hồi; hai BD thử xem tài liệu của nhau | Không truy cập được | Chờ chạy |
| UAT-008 | US-020 | Quản trị lọc bản ghi kiểm toán | Đủ người, tài liệu, thời điểm; không có nội dung | Chờ chạy |
| UAT-009 | US-022..US-024 | Quản lý xem báo cáo 4/8 tuần | Số liệu khớp dữ liệu đã biết | Chờ chạy |
| UAT-010 | US-016, US-012 | Business owner duyệt báo cáo bộ đánh giá theo ngôn ngữ | Đạt ngưỡng OQ-002 | Chờ G3 |
| UAT-011 | US-019 | Bộ phận bảo mật rà soát `data_handling.md` | Xác nhận bằng văn bản | Chờ rà soát |

#### 6.1.5 Kiểm thử hồi quy

| Thuộc tính | Mô tả |
|---|---|
| Đội phụ trách | QA, phát triển |
| Công cụ | Bộ kiểm thử tự động (pytest, Vitest, Playwright) trong CI |
| Kích hoạt | Mỗi pull request (đơn vị, tích hợp, bảo mật); hằng đêm (E2E); khi đổi `modules/qa`, `modules/retrieval`, `modules/ingestion` hoặc cấu hình mô hình (bộ đánh giá) |
| Nguyên tắc | Mỗi lỗi tìm thấy phải có kiểm thử hồi quy trước khi đóng |

| Bộ | Phạm vi | Vị trí | Tự động |
|---|---|---|---|
| REG-001 | Lõi nghiệp vụ backend | `backend/tests/unit`, `tests/integration` | ✓ (CI, mỗi PR) |
| REG-002 | Bảo mật API (ma trận xác thực, cô lập, canary) | `backend/tests/security` | ✓ (CI, mỗi PR) |
| REG-003 | Thành phần giao diện | `frontend/src/**/*.test.tsx` | ✓ (CI, mỗi PR) |
| REG-004 | Hành trình người dùng | `e2e/tests` | ✓ (hằng đêm) |
| REG-005 | Chất lượng câu trả lời | `evaluation/datasets/v1.jsonl` | ✓ (khi đổi mô-đun liên quan; tốn phí) |
| REG-006 | Luật cảnh báo | `deploy/monitoring/alerts_test.yml` | ✓ (promtool) |

**Lỗi đã có kiểm thử hồi quy** (phát hiện trong quá trình phát triển): lưu tin nhắn bị lỗi do tiến trình API thiếu model; commit chạy sau khi gửi phản hồi (trả 200 dù không lưu); khôi phục lịch sử ghi đè câu trả lời mới; mất bản nháp câu hỏi khi hết phiên; tên truy cập của chip nguồn không chứa chữ hiển thị.

#### 6.1.6 Kiểm thử hiệu năng

| Thuộc tính | Mô tả |
|---|---|
| Đội phụ trách | QA, DevOps |
| Công cụ | Bộ đánh giá (độ trễ đầu-cuối), số liệu Prometheus (`answer_latency_seconds`, `qa_step_seconds`), k6 cho tải nhẹ [Đề xuất] |
| Tiêu chí vào | Bản build ổn định; embedding thật và Claude thật; giám sát bật |
| Tiêu chí ra | Phân vị ≤ [TBD: OQ-002] (LG-05) |

| Mã | Loại | Người dùng | Thời lượng | Chỉ số | Ngưỡng |
|---|---|---|---|---|---|
| PERF-001 | Độ trễ hỏi đáp | 1 (tuần tự, bộ câu hỏi chuẩn) | Một lượt bộ câu hỏi | p50/p90/p95 thời gian phản hồi; thời gian từng bước (nhúng, truy xuất, sinh) | ≤ [TBD: OQ-002] |
| PERF-002 | Tải nhẹ hỏi đáp | [Đề xuất: 10] đồng thời | 15 phút | p95, tỷ lệ lỗi, 504 | p95 ≤ [TBD: OQ-002]; lỗi < 1% |
| PERF-003 | Nạp tài liệu | 1 người, 10 tệp (giới hạn tạm) | Tới khi xong | `ingest_duration_seconds`, độ dài hàng đợi | Tất cả `ready`; không việc chờ quá `QUEUE_MAX_AGE_S` |
| PERF-004 | Truy xuất | Kho [Đề xuất: 10.000 chunk] | — | Thời gian truy vấn pgvector có lọc quyền | Đủ `TOP_K`; [TBD] ms |
| PERF-005 | Giao diện | — | — | Chỉ báo chờ hiện ≤ 300 ms sau khi gửi; danh sách 200 tài liệu không giật | ≤ 300 ms |
| PERF-006 | Hết thời gian chờ | Dịch vụ AI chậm giả lập | — | Phản hồi 504 đúng hạn `ANSWER_TIMEOUT_S` | ≤ `ANSWER_TIMEOUT_S` + 1 s |

#### 6.1.7 Kiểm thử bảo mật

| Thuộc tính | Mô tả |
|---|---|
| Đội phụ trách | QA, bộ phận bảo mật |
| Công cụ | pytest (ma trận tự sinh từ OpenAPI), pip-audit, npm audit, OWASP ZAP [Đề xuất] |
| Tiêu chí vào | Ứng dụng chạy ở môi trường kiểm thử |
| Tiêu chí ra | Không có lỗ hổng nghiêm trọng/cao; kiểm thử canary đạt; xác nhận của bộ phận bảo mật |

| Mã | Nội dung | Mô tả | Kết quả mong đợi |
|---|---|---|---|
| SEC-001 | Xác thực | Mọi route (trừ đăng nhập, OIDC, health) không có phiên; thêm cố ý một route không bảo vệ | 401 `unauthenticated`; kiểm thử tự phát hiện route mới thiếu bảo vệ |
| SEC-002 | Phân quyền | Mọi route `/admin/*` với bd, manager; `/reports` với bd | 403 `forbidden_role`; sự kiện `access_denied` |
| SEC-003 | Cô lập dữ liệu | Hai người A/B, mỗi người một tài liệu có chuỗi đặc trưng; A gọi mọi route có tham số tài nguyên của B (sinh từ OpenAPI) | A hỏi nội dung B → "không tìm thấy"; mọi route → 404; tài liệu B nguyên vẹn; kiểm toán của A không liệt kê tài liệu B |
| SEC-004 | Mật khẩu | Băm, khóa tạm, thông báo | Argon2id; khóa sau `LOGIN_MAX_FAILURES`; không phân biệt sai tên/sai mật khẩu |
| SEC-005 | Phiên | Cookie, hết hạn, thu hồi | `HttpOnly; Secure; SameSite=Lax`; mã băm SHA-256 trong CSDL; thu hồi xóa phiên |
| SEC-006 | CSRF | POST/PUT/DELETE không có `Origin` hợp lệ | 403 `csrf_rejected` |
| SEC-007 | XSS | Câu trả lời chứa `<script>`, `<img onerror>` | Hiển thị nguyên văn, không thực thi |
| SEC-008 | Tiêu đề bảo mật | Phản hồi frontend production | CSP `default-src 'self'`, `frame-ancestors 'none'`, `nosniff`, `X-Frame-Options DENY` |
| SEC-009 | Lộ thông tin lỗi | Lỗi 500, lỗi xác thực dữ liệu | Không stack trace; không lặp lại dữ liệu đầu vào |
| SEC-010 | Riêng tư log (canary) | Chuỗi đánh dấu duy nhất trong tài liệu và câu hỏi qua trọn luồng | Không xuất hiện trong log, `usage_events`, `audit_records`, `jobs` |
| SEC-011 | Tệp tải lên | `.txt` đổi đuôi `.pdf`, tệp quá lớn | Từ chối theo nội dung (`%PDF-`), không theo đuôi/Content-Type |
| SEC-012 | Phụ thuộc | Quét lỗ hổng thư viện | Không có lỗ hổng mức cao (pip-audit, npm audit) |
| SEC-013 | Dữ liệu ra ngoài | Kiểm tra yêu cầu gửi Claude | Chỉ chunk được truy xuất, câu hỏi, lịch sử; không gửi khi dưới ngưỡng |

#### 6.1.8 Kiểm thử khả năng tiếp cận

| Thuộc tính | Mô tả |
|---|---|
| Đội phụ trách | QA |
| Công cụ | axe-core (Vitest, jsdom — không kiểm tương phản), @axe-core/playwright (trình duyệt thật, có tương phản), NVDA / VoiceOver (thủ công) |
| Chuẩn | WCAG 2.1 AA [Đề xuất] |
| Tiêu chí ra | Không vi phạm nghiêm trọng/cao; vi phạm nhỏ còn lại có người chịu trách nhiệm và hạn |

| Mã | Nội dung | Mô tả | Kết quả mong đợi |
|---|---|---|---|
| ACC-001 | Bàn phím | Liên kết "bỏ qua" → đăng nhập → gửi câu hỏi (Ctrl+Enter) chỉ bằng bàn phím | Dùng được toàn bộ |
| ACC-002 | Trình đọc màn hình | Đọc S-02, S-03 bằng NVDA/VoiceOver | Nhãn, vai trò, thông báo `aria-live` được đọc |
| ACC-003 | Tương phản | axe trong Playwright trên mọi màn hình | ≥ 4.5:1 cho chữ thường |
| ACC-004 | ARIA | `alertdialog`, `progressbar`, `aria-pressed`, `aria-current`, tên truy cập chứa chữ hiển thị | Đúng |
| ACC-005 | Quản lý tiêu điểm | Hộp thoại xóa: mặc định ở Hủy, bẫy Tab, Esc trả tiêu điểm; tiêu điểm về ô nhập sau câu trả lời | Đúng |
| ACC-006 | Thông báo lỗi | Lỗi đăng nhập, tải lên, hỏi, cấp quyền | Có `role=alert` hoặc gắn với trường |
| ACC-007 | Thu phóng 200% | S-02 ở 200% | Không mất chức năng |
| ACC-008 | Không chỉ dùng màu | Nhãn trạng thái, biểu đồ S-07 | Có chữ; biểu đồ có bảng số liệu tương ứng |

#### 6.1.9 Kiểm thử giao diện

| Thuộc tính | Mô tả |
|---|---|
| Đội phụ trách | QA, thiết kế |
| Công cụ | Testing Library (trạng thái), Playwright (ảnh màn hình), đối chiếu thủ công với `html_design/screenshots/` |
| Tiêu chí ra | Mọi trạng thái trong ảnh mẫu có ca kiểm thử đạt; thiết kế duyệt ảnh đối chiếu |

| Mã | Nội dung | Mô tả | Kết quả mong đợi |
|---|---|---|---|
| UI-001 | Đối chiếu ảnh mẫu | 22 ảnh trạng thái S-01..S-07 so với ảnh giao diện thật (`docs/implement/evidence/screenshots/`) | Khớp bố cục, màu (token từ `styles.css`), nhãn |
| UI-002 | Độ rộng | Thiết kế cho ≥ 1024 px (desktop) | Không cuộn ngang ở 1024–1920 px |
| UI-003 | Trạng thái thành phần | Mặc định, vô hiệu, đang tải, lỗi, trống của mọi thành phần ở A.4 | Đủ trạng thái |
| UI-004 | Tương tác | Kéo thả tải lên, hủy chờ, trang trước/sau, hội thoại mới | Hoạt động |
| UI-005 | Trạng thái lỗi | s02-offline-ask, s02-offline-upload, s03-deleted, s04-failed, s06-error, s07-error | Hiển thị đúng, có hành động khắc phục |
| UI-006 | Trạng thái chờ | s02-waiting, tiến độ tải lên, đang xử lý | Hiển thị ngay |
| UI-007 | Thông báo | Banner tại chỗ, xác nhận thu hồi, thông báo đã cấp quyền | Hiển thị đúng chỗ |
| UI-008 | Điều hướng | Theo vai trò sau đăng nhập; sai vai trò → trang của vai trò; liên kết quay lại | Đúng |

#### 6.1.10 Kiểm thử API

| Thuộc tính | Mô tả |
|---|---|
| Đội phụ trách | QA, phát triển |
| Công cụ | pytest + TestClient (tự động); OpenAPI tại `/api/v1/docs` cho kiểm tra thủ công |
| Phạm vi | Mọi endpoint ở A.5 |
| Tiêu chí ra | 100% endpoint có ca dương và ca âm; kiểu TypeScript sinh từ OpenAPI khớp (job CI `openapi-types`) |

| Mã | Endpoint | Phương thức | Loại | Kiểm tra |
|---|---|---|---|---|
| API-001 | `/auth/login` | POST | Chức năng / âm | INT-API-001..004 |
| API-002 | `/auth/me`, `/auth/logout` | GET, POST | Chức năng / âm | INT-API-005, SEC-005 |
| API-003 | `/auth/oidc/*` | GET | Chức năng / âm | INT-API-037 |
| API-004 | `/documents` | POST | Chức năng / biên / âm | INT-API-007, 008, SEC-011 |
| API-005 | `/documents`, `/documents/{id}` | GET | Chức năng / cô lập | SEC-003 |
| API-006 | `/documents/{id}/retry` | POST | Chức năng / âm | INT-API-014 |
| API-007 | `/documents/{id}` | DELETE | Chức năng / quyền | INT-API-028, 031 |
| API-008 | `/documents/{id}/pages/{page}`, `/file` | GET | Chức năng / âm | INT-API-026, 027 |
| API-009 | `/events/source-opened` | POST | Chức năng / quyền | Đúng một `source_opened`; tài liệu người khác → 404 |
| API-010 | `/conversations`, `/conversations/{id}/messages` | POST, GET | Chức năng / âm / lỗi | INT-API-019..025 |
| API-011 | `/messages/{id}/feedback` | PUT | Chức năng / âm | INT-API-032 |
| API-012 | `/admin/access` | GET, POST, DELETE | Chức năng / quyền | INT-API-035, SEC-002 |
| API-013 | `/admin/audit` | GET | Chức năng / phân trang | INT-API-033 |
| API-014 | `/reports/usage` | GET | Chức năng / quyền | INT-API-034 |
| API-015 | `/health/live`, `/health/ready` | GET | Chức năng / lỗi | INT-API-036 |

#### 6.1.11 Kiểm thử chất lượng câu trả lời (bộ đánh giá)

Theo implement_plan.md mục 9.4.

| Chỉ số | Cách tính | Tiêu chí |
|---|---|---|
| Đúng và có nguồn (MET-002) | Câu `in_scope` trả lời đúng **và** ≥ 1 nguồn khớp `expected_sources` ÷ số câu `in_scope` | ≥ [TBD: OQ-002] (LG-02) |
| Tỷ lệ bịa | Câu `out_of_scope` nhận câu trả lời có nội dung ÷ số câu `out_of_scope` | ≤ [TBD: OQ-002] (LG-03) |
| Độ phủ nguồn | Câu `multi_doc` có nguồn từ tất cả tài liệu mong đợi ÷ số câu `multi_doc` | Báo cáo (AC-007) |
| Hỏi tiếp đúng | Câu `follow_up` đúng ÷ số câu `follow_up` | Báo cáo (AC-008) |
| Đúng trang | Citation có `cited_text` trong trang được nêu ÷ tổng citation | 100% (LG-04) |
| Độ trễ | p50 / p90 / p95 | ≤ [TBD: OQ-002] (LG-05) |

- **Chấm "đúng":** business owner xác nhận đáp án mẫu; chấm tự động (từ khóa / độ phủ từ) phải đối chiếu chấm tay trên mẫu ngẫu nhiên 20% (`--review-sample 0.2`) trước khi dùng cho cổng launch.
- **Bộ câu hỏi:** tối thiểu 10 câu mỗi loại `in_scope`, `out_of_scope`, `multi_doc`, `follow_up`, theo từng ngôn ngữ đã chốt (OQ-007); bổ sung nhóm "câu ngoài phạm vi hỏi tiếp trong cùng hội thoại" (TR-01).
- **Hiệu chỉnh:** mỗi lần đổi một yếu tố (`CHUNK_TOKENS`, `CHUNK_OVERLAP`, `TOP_K`, `MAX_CHUNKS_PER_DOC`, `MIN_RELEVANCE_SCORE`, `ANSWER_EFFORT`, chỉ dẫn hệ thống), ghi vào `docs/implement/tuning_log.md` kèm chi phí.

#### 6.1.12 Kiểm thử vận hành và sẵn sàng

| Mã | Nội dung | Mô tả | Kết quả mong đợi |
|---|---|---|---|
| OPS-001 | Health | Dừng CSDL / kho tệp; tạo hàng đợi tồn đọng | `/health/ready` 503 với thành phần lỗi |
| OPS-002 | Cảnh báo | `promtool test rules` với chuỗi số liệu giả | `ComponentUnavailable`, `WorkerDown`, `DocumentsDeletingOverdue` phát đúng thời điểm |
| OPS-003 | Xóa quá hạn | Tài liệu `deleting` quá `PURGE_SLA_HOURS` | `documents_deleting_overdue` > 0; log cảnh báo |
| OPS-004 | Triển khai theo runbook | Người ngoài đội làm theo `ops_runbook.md` trên môi trường kiểm thử | Hệ thống chạy, `/health/ready` 200 |
| OPS-005 | Khôi phục sao lưu | Khôi phục bản sao lưu rồi chạy lại xóa cho tài liệu đã xóa (runbook mục 6) | Không "hồi sinh" tài liệu đã xóa |

### 6.2 Chiến lược thực thi

**Thứ tự thực thi trong mỗi sprint** (implement_plan.md mục 7, 10.4):
1. Mỗi commit: lint (ruff, eslint), kiểm tra kiểu (mypy strict, tsc), quy tắc import (import-linter), kiểm thử đơn vị.
2. Mỗi pull request: thêm kiểm thử tích hợp và bảo mật (PostgreSQL/S3 thật qua testcontainers), kiểm tra kiểu TypeScript khớp OpenAPI, quét lỗ hổng phụ thuộc, build ảnh Docker. Pull request chỉ được hợp nhất khi CI xanh.
3. Hằng đêm: E2E Playwright với adapter AI giả lập (`.github/workflows/nightly.yml`).
4. Khi đổi `modules/qa`, `modules/retrieval`, `modules/ingestion`, adapter AI hoặc cấu hình mô hình: chạy bộ đánh giá với adapter thật (tốn phí, có ghi chi phí).
5. Trước phát hành (cổng G4): chạy toàn bộ mọi tầng, kiểm thử chấp nhận, kiểm tra khả năng tiếp cận thủ công, ghi `docs/implement/launch_checklist.md`.

**Kiểm thử theo sprint**

| Sprint | Story | Trọng tâm kiểm thử | Kịch bản đầu-cuối |
|---|---|---|---|
| 0 | Nền tảng, spike | Khung kiểm thử chạy được; spike trích xuất (T0-06), embedding (T0-07), sinh câu trả lời (T0-08); khung bộ đánh giá (T0-09); CI đỏ khi lỗi lint (T0-03) | — |
| 1 | US-017, US-001..005 | Xác thực, ma trận bảo mật (T1-08), luồng nạp (T1-20) | E2E-001..007 |
| 2 | US-008, 009, 011, 012, 014, 015 | Hỏi đáp và ba lớp từ chối (T2-12), bộ câu hỏi v1 và đường cơ sở (T2-13) | E2E-008, E2E-009 |
| 3 | US-006, 007, 010, 013, 018, 020 | Xóa (T3-01, T3-02), cô lập quyền (T3-07), hội thoại, thời gian chờ | E2E-010, E2E-011 |
| 4 | US-016, 019, 021..024 | Hiệu chỉnh chất lượng (T4-01), canary và hồ sơ dữ liệu (T4-05), cổng launch (T4-06), tiếp cận (T4-08) | E2E-012, E2E-013 |

**Phân loại mức độ lỗi**

| Mức | Định nghĩa | Ví dụ | Xử lý |
|---|---|---|---|
| Nghiêm trọng | Lộ dữ liệu, mất dữ liệu, sai lệch câu trả lời không được phát hiện, hệ thống không dùng được | Người dùng thấy tài liệu của người khác; API trả 200 nhưng không lưu | Dừng phát hành; sửa ngay |
| Cao | Chức năng P0 sai, không có cách khắc phục | Tài liệu đã xóa vẫn được dùng; câu trả lời có nội dung không có nguồn | Sửa trước cổng kế tiếp |
| Trung bình | Chức năng sai nhưng có cách khắc phục, hoặc P1 | Bộ lọc kiểm toán sai | Sửa trong sprint |
| Thấp | Hiển thị, câu chữ | Nhãn ngày chưa đúng định dạng | Lên kế hoạch |

## 7. Tiêu chí đạt/không đạt

| Cấp | Đạt khi |
|---|---|
| Ca kiểm thử | Kết quả thực tế khớp kết quả mong đợi; với kiểm thử tự động: lệnh kiểm thử trả mã 0 |
| Story | Đạt định nghĩa hoàn thành (implement_plan.md mục 11): mọi AC có kiểm thử tự động đạt; giao diện khớp ảnh mẫu và đạt kiểm tra tiếp cận; không ngưỡng viết cứng; log và sự kiện không có nội dung; sự kiện phân tích được phát; mã được rà soát, CI xanh; OpenAPI cập nhật |
| Sprint | Mọi story của sprint đạt; không còn lỗi nghiêm trọng/cao mở; kịch bản E2E của sprint đạt |
| Phát hành (G4) | LG-01..LG-11 đạt hoặc có quyết định ngoại lệ bằng văn bản của sponsor |

**Tiêu chí launch (PRD mục 5.1)**

| LG | Tiêu chí | Đo bằng |
|---|---|---|
| LG-01 | 100% AC của story P0 đạt | Kiểm thử tự động + chấp nhận |
| LG-02 | MET-002 ≥ [TBD: OQ-002] | Bộ đánh giá |
| LG-03 | Tỷ lệ bịa ≤ [TBD: OQ-002] | Bộ đánh giá (câu ngoài phạm vi) |
| LG-04 | 100% câu trả lời có nội dung nêu đúng tài liệu và trang | Bộ đánh giá (đúng trang) + kiểm thử tích hợp |
| LG-05 | Thời gian phản hồi ≤ [TBD] giây ở [TBD]% số câu | PERF-001 |
| LG-06 | Bảo mật xác nhận bằng văn bản | UAT-011 |
| LG-07 | Không được cấp quyền thì không vào được; chỉ thấy tài liệu trong phạm vi | SEC-001..003 |
| LG-08 | Xóa đúng cả ở truy vấn và nơi lưu | INT-API-028..030 |
| LG-09 | Không còn lỗi nghiêm trọng/cao mở; độ phủ đạt [TBD: OQ-002] | Báo cáo QA, pytest-cov |
| LG-10 | Có bộ câu hỏi chuẩn và PDF mẫu thật | Xác nhận business owner |
| LG-11 | OQ-001..OQ-007 đã chốt | Xác nhận sponsor |

## 8. Tiêu chí tạm dừng và tiếp tục

| Tạm dừng khi | Tiếp tục khi |
|---|---|
| Môi trường kiểm thử không chạy (`/health/ready` 503 kéo dài, migration lỗi) | Môi trường khôi phục, `/health/ready` 200 |
| Phát hiện lỗi nghiêm trọng về bảo mật/riêng tư (lộ dữ liệu, nội dung xuất hiện trong log) | Đã sửa, có kiểm thử hồi quy, chạy lại toàn bộ bộ bảo mật |
| > 20% ca kiểm thử của một tầng thất bại do cùng một nguyên nhân | Nguyên nhân được sửa, bản build mới |
| Thiếu đầu vào bắt buộc của bộ đánh giá: khóa API, PDF thật (DEP-001), bộ câu hỏi đã duyệt (ASM-005) | Đầu vào được cung cấp |
| Máy kiểm thử thiếu tài nguyên (RAM, đĩa) làm dịch vụ dừng giữa chừng | Chuyển sang máy đủ tài nguyên hoặc dùng cấu hình nhẹ (embedding giả lập) |
| Chi phí gọi dịch vụ AI vượt ngân sách lần chạy [TBD: OQ-009] | Được phê duyệt thêm ngân sách |

## 9. Sản phẩm bàn giao của kiểm thử

| Sản phẩm | Vị trí | Thời điểm |
|---|---|---|
| Kế hoạch kiểm thử tổng thể (tài liệu này) | `docs/testing/Master_Test_Plan.md` | Sprint 0 |
| Mã kiểm thử tự động | `backend/tests`, `frontend/src/**/*.test.tsx`, `e2e/tests`, `evaluation/tests` | Liên tục |
| Kết quả CI | GitHub Actions (`.github/workflows/ci.yml`, `nightly.yml`) | Mỗi PR / hằng đêm |
| Báo cáo spike | `docs/implement/spike_pdf.md`, `spike_embedding.md`, `spike_generation.md` | Cổng G0 |
| Báo cáo bộ đánh giá | `evaluation/reports/*.md`, `*.json`; mẫu chấm tay `*-review.csv` | Mỗi lần chạy |
| Nhật ký hiệu chỉnh | `docs/implement/tuning_log.md` | Sprint 2–4 |
| Báo cáo Playwright và ảnh màn hình đối chiếu | `e2e/playwright-report`, `docs/implement/evidence/screenshots/` | Hằng đêm, G4 |
| Hồ sơ xử lý dữ liệu | `docs/implement/data_handling.md` | Sprint 4 |
| Danh sách kiểm tra cổng launch | `docs/implement/launch_checklist.md` | Cổng G4 |
| Báo cáo tổng kết kiểm thử (Test Summary Report) | `docs/testing/Test_Summary_Report.md` [sẽ lập] | Cổng G4 |

## 10. Công việc kiểm thử

| Mã | Công việc | Task liên quan | Phụ thuộc | Người thực hiện |
|---|---|---|---|---|
| TT-01 | Dựng khung kiểm thử, fixture CSDL/S3, bộ PDF tổng hợp | T0-01, T0-10 | — | Phát triển |
| TT-02 | Thiết lập CI và chứng minh CI đỏ khi lỗi lint | T0-03 | TT-01 | DevOps |
| TT-03 | Khung bộ đánh giá và kiểm thử công thức | T0-09 | — | QA |
| TT-04 | Spike trích xuất, embedding, sinh câu trả lời | T0-06..T0-08 | DEP-001, khóa API | Kỹ sư AI |
| TT-05 | Ma trận xác thực tự sinh | T1-08 | T1-04, T1-05 | QA |
| TT-06 | Kiểm thử tích hợp luồng nạp | T1-20 | T1-15, T1-16 | QA |
| TT-07 | E2E tải tài liệu | T1-21 | T1-18..T1-20 | QA |
| TT-08 | Kiểm thử tích hợp hỏi đáp | T2-12 | T2-05, T2-06 | QA |
| TT-09 | Bộ câu hỏi chuẩn v1 và đường cơ sở | T2-13 | T0-09, T2-05, DEP-001 | QA + business owner |
| TT-10 | E2E hỏi đáp | T2-14 | T2-09, T2-10 | QA |
| TT-11 | Kiểm thử cô lập quyền | T3-07 | T3-03 | QA |
| TT-12 | E2E xóa và kiểm toán | T3-08 | T3-01..T3-04 | QA |
| TT-13 | Hiệu chỉnh và nghiệm thu chất lượng | T4-01 | G3 | QA + kỹ sư AI |
| TT-14 | Kiểm thử canary, hồ sơ dữ liệu, trình bảo mật | T4-05 | T3-02, T3-04 | QA + bảo mật |
| TT-15 | Kiểm thử giám sát và cảnh báo | T4-04 | T3-02 | DevOps |
| TT-16 | Rà soát khả năng tiếp cận toàn bộ | T4-08 | T4-02, T4-03 | QA |
| TT-17 | Kiểm tra cổng launch, lập báo cáo tổng kết | T4-06 | T4-01..T4-05 | Trưởng nhóm QA |

## 11. Nhu cầu môi trường

### 11.1 Môi trường (implement_plan.md mục 10.1)

| Môi trường | Mục đích | Dữ liệu | Adapter AI | Embedding |
|---|---|---|---|---|
| Local | Phát triển, đơn vị, tích hợp | Tổng hợp | Giả lập (hoặc thật với khóa riêng) | Giả lập (`hash`) hoặc `bge-m3` |
| CI | Đơn vị, tích hợp, bảo mật, build | Tổng hợp, sinh lúc chạy | Giả lập | Giả lập |
| E2E (compose + `docker-compose.e2e.yml`) | Kiểm thử đầu-cuối | Tổng hợp, tài khoản mẫu `e2e.*` | Giả lập | Giả lập |
| Test/Staging | Đánh giá chất lượng, hiệu năng, chấp nhận | Tổng hợp + mẫu thật được phép (OQ-005) | Claude thật | `bge-m3` |
| Production | Thử nghiệm với BD | Thật | Theo kịch bản đã chốt (OQ-006) | `bge-m3` |

### 11.2 Phần mềm và công cụ

| Hạng mục | Phiên bản |
|---|---|
| Python | 3.12 (backend, bộ đánh giá) |
| Node.js | 22 (CI), ≥ 20 (cục bộ) |
| PostgreSQL + pgvector | 16 + ≥ 0.8 (`iterative_scan`) |
| Kho S3 | RustFS 1.0.3 (cục bộ), S3/MinIO (môi trường thật) |
| Docker / Docker Compose | ≥ 24 / v2 |
| pytest, pytest-cov, testcontainers | Theo `backend/pyproject.toml` |
| Vitest, Testing Library, axe-core | Theo `frontend/package.json` |
| Playwright, @axe-core/playwright | Theo `e2e/package.json` (Chromium) |
| Prometheus (promtool) | v3.1.0 |

### 11.3 Phần cứng

| Môi trường | Tối thiểu đề xuất | Ghi chú |
|---|---|---|
| Máy phát triển (cấu hình nhẹ, embedding giả lập) | 8 GB RAM, 10 GB đĩa trống | Giới hạn máy ảo WSL2/Docker (ví dụ 4 GB) để hệ điều hành còn tài nguyên |
| Máy chạy bộ đánh giá với `bge-m3` | 16 GB RAM, 20 GB đĩa trống | Mô hình ~2,3 GB trên đĩa, vài GB khi nạp vào RAM |
| CI | Runner `ubuntu-latest` | Có Docker cho testcontainers; phông `fonts-dejavu-core` |

### 11.4 Dữ liệu kiểm thử (implement_plan.md mục 9.2)

| Dữ liệu | Nguồn | Quy tắc |
|---|---|---|
| PDF tổng hợp: văn bản nhiều trang, tiếng Việt, mã hóa, hỏng, không phải PDF, chỉ ảnh | Sinh lúc chạy (`tests/pdf_factory.py`, `e2e/tests/pdf.ts`) | Không commit tệp nhị phân |
| Bộ PDF tổng hợp có đáp án (22 tệp: hợp đồng, báo giá có bảng, đề xuất hai cột, tiếng Anh, mã hóa, scan) | `evaluation/spikes/make_corpus.py` | Không nhạy cảm, sinh lại được |
| PDF thật của đội BD (DEP-001) | Business owner | **Không commit** nếu nhạy cảm; lưu ở nơi được phép (OQ-005), đường dẫn qua biến môi trường |
| Bộ câu hỏi chuẩn | `evaluation/datasets/*.jsonl` | Business owner duyệt đáp án (ASM-005) |
| Tài khoản kiểm thử | `seed` trong `docker-compose.e2e.yml` | Mật khẩu chỉ dùng cho kiểm thử cục bộ/CI |
| Chuỗi canary | Sinh ngẫu nhiên mỗi lần (`CANARY-…`) | Dùng cho SEC-010 |

## 12. Trách nhiệm

| Vai trò | Trách nhiệm |
|---|---|
| Trưởng nhóm QA | Duyệt kế hoạch này; theo dõi tiến độ; quyết định tạm dừng/tiếp tục; lập báo cáo tổng kết; chủ LG-01, LG-07, LG-09 |
| Kỹ sư QA | Viết và duy trì E2E, kiểm thử tích hợp/bảo mật; thực hiện kiểm thử thủ công (tiếp cận, chấp nhận); quản lý lỗi |
| Lập trình viên backend/frontend | Kiểm thử đơn vị và tích hợp cho mã của mình; sửa lỗi kèm kiểm thử hồi quy |
| Kỹ sư AI | Spike T0-06..T0-08; vận hành bộ đánh giá; hiệu chỉnh tham số; chủ LG-02..LG-05 |
| DevOps | CI, môi trường kiểm thử, giám sát và cảnh báo; chủ LG-08 (phần sao lưu, AQ-003) |
| Business owner | Cung cấp PDF thật và bộ câu hỏi chuẩn; duyệt đáp án; chủ LG-10 |
| Bộ phận bảo mật | Rà soát hồ sơ dữ liệu, kiểm thử xâm nhập; chủ LG-06 |
| Chủ sản phẩm / sponsor | Chốt các ngưỡng OQ-002 và câu hỏi mở; quyết định phát hành; chủ LG-11 |

## 13. Nhân sự và đào tạo

| Nhu cầu | Đối tượng | Nội dung |
|---|---|---|
| Kiểm thử hệ thống có thành phần AI | QA | Ba lớp từ chối, đọc báo cáo bộ đánh giá, khác biệt adapter giả lập và thật |
| Playwright + axe | QA | Viết kịch bản bền vững (dữ liệu duy nhất mỗi lần chạy, chờ theo trạng thái) |
| Kiểm thử khả năng tiếp cận thủ công | QA | NVDA/VoiceOver, kiểm tra bàn phím, WCAG 2.1 AA |
| Chấm tay câu trả lời | Business owner, QA | Tiêu chí "đúng", kiểm tra nguồn và trang |
| Vận hành môi trường | Toàn đội | `ops_runbook.md`, `scripts/backend-docker.sh`, giới hạn tài nguyên Docker |

Số lượng nhân sự: [TBD: OQ-009].

## 14. Lịch

Sprint 2 tuần [Đề xuất] (implement_plan.md mục 7).

| Mốc | Thời điểm | Hoạt động kiểm thử | Điều kiện qua |
|---|---|---|---|
| Sprint 0 | Tuần 1–2 | Khung kiểm thử, CI, spike, khung bộ đánh giá | **G0:** chốt công nghệ, DQ-003, kết quả spike |
| Sprint 1 | Tuần 3–4 | Xác thực, bảo mật, luồng nạp, E2E tải tài liệu | Mọi kiểm thử Sprint 1 đạt |
| Sprint 2 | Tuần 5–6 | Hỏi đáp, trình xem nguồn, bộ câu hỏi v1, đường cơ sở | **G1** (trước Sprint 2): OQ-006, OQ-005 sơ bộ, OQ-007 |
| Sprint 3 | Tuần 7–8 | Xóa, cô lập quyền, kiểm toán, hội thoại, thời gian chờ | **G2** (trước Sprint 3): OQ-003, OQ-012 |
| Sprint 4 | Tuần 9–10 | Hiệu chỉnh chất lượng, hiệu năng, canary, giám sát, tiếp cận, chấp nhận | **G3** (trước Sprint 4): OQ-002, bộ câu hỏi chuẩn đầy đủ |
| Phát hành | Cuối tuần 10 | Kiểm tra cổng launch, báo cáo tổng kết | **G4:** LG-01..LG-11 |

Ngày cụ thể: [TBD: OQ-009].

## 15. Rủi ro và dự phòng

| Rủi ro | Ảnh hưởng tới kiểm thử | Dự phòng |
|---|---|---|
| Ngưỡng OQ-002 chưa chốt | Không kết luận được LG-02..LG-05 | Báo cáo số đo thô; ngưỡng nằm trong cấu hình; chặn ở G3 |
| Không có PDF thật / bộ câu hỏi đã duyệt (DEP-001, ASM-005) | Chỉ đo được trên dữ liệu tổng hợp | Dùng bộ tổng hợp có đáp án cho phát triển; ghi rõ giới hạn trong báo cáo; không qua LG-10 |
| Chưa có khóa API / OQ-006 chưa chốt | Không chạy được bộ đánh giá thật, spike T0-08 | Kiểm thử adapter bằng phản hồi giả lập; kiểm thử thật đánh dấu `needs_api_key` tự chạy khi có khóa |
| Máy kiểm thử thiếu tài nguyên cho `bge-m3` (đã ghi nhận dịch vụ dừng và hệ điều hành khởi động lại trên máy phát triển 8 GB RAM) | Spike T0-07 và đường cơ sở thật bị chặn; gián đoạn công việc | Chạy trên máy kiểm thử ≥ 16 GB RAM; giới hạn tài nguyên Docker; cấu hình nhẹ cho phát triển giao diện |
| Embedding giả lập cho kết quả khác mô hình thật | E2E không phản ánh chất lượng truy xuất | E2E chỉ kiểm luồng; chất lượng đo riêng bằng bộ đánh giá |
| Dữ liệu E2E tích lũy giữa các lần chạy | Kịch bản bị nhiễu | Tên tệp và từ vựng duy nhất mỗi lần chạy; định kỳ dựng lại CSDL kiểm thử |
| Hỏi tiếp ngoài phạm vi vượt lớp từ chối 1 (truy vấn ghép câu trước) | Tỷ lệ bịa tăng ở nhóm câu này | Thêm nhóm câu vào bộ đánh giá; cân nhắc truy xuất hai lần (`tuning_log.md`) |
| Chi phí dịch vụ AI (RSK-005) | Giới hạn số lần chạy bộ đánh giá | Chỉ chạy khi đổi mô-đun liên quan; ghi chi phí |
| Bản sao lưu còn dữ liệu đã xóa (AQ-003) | LG-08 chưa trọn vẹn | Ghi là rủi ro mở; quy trình khôi phục chạy lại xóa (OPS-005) |

## 16. Phê duyệt

| Vai trò | Họ tên | Chữ ký | Ngày |
|---|---|---|---|
| Trưởng nhóm QA | | | |
| Chủ sản phẩm | | | |
| Trưởng nhóm phát triển | | | |
| Bộ phận bảo mật | | | |
| Sponsor | | | |

---

## Phụ lục 1 — Ma trận truy vết yêu cầu → ca kiểm thử → kiểm thử tự động

| Yêu cầu | AC | Story | Ca kiểm thử | Kiểm thử tự động |
|---|---|---|---|---|
| BR-001 | AC-001 | US-001 | INT-API-009, E2E-005, UAT-001 | `test_valid_pdf_becomes_ready_with_paged_chunks`; `documents.spec.ts` |
| BR-002 | AC-002 | US-002 | INT-API-007, INT-API-008, UAT-001 | `test_mixed_upload_each_file_judged_independently`, `test_many_files_with_two_concurrent_workers`, `test_max_docs_per_user` |
| BR-003 | AC-003 | US-003 | INT-API-010, E2E-006, E2E-007, UAT-002 | `test_worker_failure_reasons`; `documents.spec.ts` |
| BR-004 | AC-004 | US-005 | E2E-005, SEC-003 | `test_user_cannot_see_or_touch_other_users_documents`; `documents.test.tsx` |
| BR-005 | AC-005 | US-006 | INT-API-028, E2E-010, UAT-006 | `test_deleted_document_is_excluded_immediately`; `delete-audit.spec.ts` |
| BR-006 | AC-006 | US-008 | INT-API-019, E2E-008, UAT-003 | `test_answer_has_source_document_and_page`; `qa.spec.ts` |
| BR-007 | AC-007 | US-009 | INT-API-018, bộ đánh giá (độ phủ nguồn) | `test_question_across_documents_cites_the_right_one`, `test_max_chunks_per_document` |
| BR-008 | AC-008 | US-010 | INT-API-025, UT-011, UAT-005 | `test_history_and_follow_up_question`, `test_retrieval_query_appends_previous_user_question` |
| BR-009 | AC-009 | US-011 | UT-007..009, INT-API-020, E2E-008, UAT-004 | `test_qa_service.py`, `test_out_of_scope_question_is_not_found_without_calling_model` |
| BR-010 | AC-010 | US-012 | UT-002, bộ đánh giá theo ngôn ngữ | `test_vietnamese_text_is_nfc_and_keeps_diacritics` |
| BR-011 | AC-011 | US-013 | PERF-001, PERF-005, PERF-006, INT-API-022 | `test_timeout_returns_504`, `test_slow_generator_hits_answer_timeout`; `chat.test.tsx` (chỉ báo chờ, Hủy) |
| BR-012 | AC-012 | US-014 | UT-009, UT-010, UT-012, INT-API-019 | `test_answer_with_content_always_has_citation`, `test_map_citations_dedupes_and_keeps_order` |
| BR-013 | AC-013 | US-016 | Mục 6.1.11, UAT-010 | `evaluation/tests/test_run_eval.py` (công thức); báo cáo bộ đánh giá |
| BR-014 | AC-014 | US-017 | INT-API-001..006, SEC-001, SEC-002, E2E-001..003, UAT-007 | `test_auth.py`, `test_auth_matrix.py`; `auth.spec.ts` |
| BR-015 | AC-015 | US-019 | SEC-010, SEC-013, UAT-011 | `test_no_content_in_logs.py`, `test_request_log_does_not_contain_question_value` |
| BR-016 | AC-016 | US-022 | INT-API-034, UAT-009 | `test_weekly_usage_with_seed_data` |
| BR-017 | AC-017 | US-024 | INT-API-032 | `test_feedback_is_saved_and_can_be_changed`, `test_usage_endpoint_includes_helpful_ratio`; `chat.test.tsx` |
| BR-018 | AC-018 | US-004 | UT-003, UT-020, E2E-006 | `test_extract.py`, `failureMessages.test.ts` |
| BR-019 | AC-019 | US-015 | UT-001, UT-004, UT-021, INT-API-019, INT-API-026, E2E-008 | `test_chunking.py`, `sources.test.tsx`, `test_source_page_and_file_access` |
| BR-020 | AC-020 | US-018 | SEC-003, INT-API-015 | `test_isolation.py`, `test_chunks_outside_allowed_documents_never_appear` |
| BR-021 | AC-021 | US-023 | INT-API-034, UAT-009 | `test_weekly_usage_with_seed_data` |
| BR-022 | AC-022 | US-021 | INT-API-036, OPS-001, OPS-002 | `test_ready_fails_when_*`, `test_maintenance_exports_component_health_for_alerting`, `alerts_test.yml` |
| BR-023 | AC-023 | US-020 | INT-API-023, INT-API-033, E2E-011, UAT-008 | `test_each_question_writes_exactly_one_audit_record_without_content`, `test_audit_filters_and_cursor` |
| BR-024 | AC-024 | US-007 | INT-API-029, INT-API-030, UAT-006 | `test_purge_removes_chunks_file_and_sets_purged_at`, `test_storage_error_midway_is_retried_and_completes` |
| NFR-LOG | — | US-019 | UT-017, SEC-009, SEC-010 | `test_no_content_in_logs.py`, `test_framework.py` |
| NFR-ACC | — | Mọi story có giao diện | ACC-001..008, E2E-012 | `a11y.spec.ts`; `seriousViolations` trong Vitest |
| NFR-CFG | — | — | UT-019 | `test_every_threshold_is_configurable` |

**Độ phủ:** 24/24 BR và 24/24 AC có ít nhất một ca kiểm thử. AC-013 (chất lượng), AC-010 (ngôn ngữ), AC-011 (thời gian phản hồi) và AC-015 (xác nhận bảo mật) cần dữ liệu thật, khóa API hoặc rà soát của con người để kết luận.

## Phụ lục 2 — Trạng thái hiện tại (tại ngày soạn)

| Tầng | Số kiểm thử tự động | Kết quả gần nhất |
|---|---|---|
| Backend (đơn vị + tích hợp + bảo mật) | 183 (+1 cần khóa API) | Đạt |
| Frontend (Vitest) | 79 | Đạt |
| Đầu-cuối (Playwright) | 19 | Đạt |
| Bộ đánh giá (công thức) | 12 | Đạt |
| Luật cảnh báo (promtool) | 3 luật được kiểm | Đạt |

Chưa thực hiện: bộ đánh giá với Claude và `bge-m3` thật (thiếu khóa API, thiếu tài nguyên máy); kiểm thử chấp nhận với người dùng; kiểm thử hiệu năng PERF-002..004; kiểm thử thủ công với trình đọc màn hình; rà soát bảo mật. Chi tiết theo từng tiêu chí launch: `docs/implement/launch_checklist.md`.
