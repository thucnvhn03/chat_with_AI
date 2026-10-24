# Hồ sơ xử lý dữ liệu — "Chat với tài liệu" (MVP)

| Mục | Nội dung |
|---|---|
| Story / tiêu chí | US-019 (AC-015, LG-06), ADR-009 |
| Phiên bản | 0.1 (Draft) — 2026-10-22 |
| Trạng thái rà soát | **Chờ bộ phận bảo mật rà soát và xác nhận bằng văn bản** |
| Quyết định còn mở ảnh hưởng hồ sơ | OQ-005 (quy định dữ liệu), OQ-006 (gửi nội dung ra dịch vụ AI bên ngoài), OQ-012 (thời hạn xóa, lưu bản ghi), AQ-003 (sao lưu và xóa), PQ-004 (lưu hội thoại giữa các phiên) |

Tài liệu này mô tả dữ liệu nào đi đâu, lưu ở đâu, mã hóa thế nào, lưu bao lâu, xóa ra sao. Mọi khẳng định đều trỏ tới mã nguồn hoặc kiểm thử tự động để người rà soát đối chiếu.

## 1. Loại dữ liệu và nơi lưu

| Dữ liệu | Nơi lưu | Ai đọc được | Ghi chú |
|---|---|---|---|
| Tệp PDF gốc | Kho đối tượng S3, khóa `documents/{owner_id}/{document_id}.pdf` | Chỉ qua backend (`GET /documents/{id}/file`), sau khi kiểm quyền | Trình duyệt không bao giờ nhận đường dẫn trực tiếp tới kho (`app/adapters/s3_file_store.py`, `app/api/sources.py`) |
| Văn bản đã trích xuất, chia đoạn (chunk) và vector embedding | PostgreSQL, bảng `chunks` | Mô-đun truy xuất, chỉ cho tài liệu trong phạm vi người hỏi | Embedding tạo **trong hạ tầng** bằng mô hình chạy nội bộ (`BAAI/bge-m3`), không gửi ra ngoài ở bước này |
| Siêu dữ liệu tài liệu (tên tệp, dung lượng, số trang, trạng thái) | PostgreSQL, bảng `documents` | Chủ sở hữu (và người được chia sẻ khi OQ-003 cho phép) | |
| Câu hỏi và câu trả lời | PostgreSQL, bảng `messages` | Chỉ chủ hội thoại | Lưu để giữ ngữ cảnh hội thoại (US-010). Thời gian lưu chờ PQ-004 — xem mục 4 |
| Trích dẫn (tên tài liệu, số trang, đoạn trích nguyên văn) | PostgreSQL, bảng `citations` | Chỉ chủ hội thoại | Đoạn trích bị xóa khi tài liệu bị xóa vĩnh viễn (mục 5) |
| Bản ghi kiểm toán | PostgreSQL, bảng `audit_records` | Quản trị bảo mật (S-06) | Chỉ gồm người dùng, danh sách id tài liệu được phép, thời điểm. **Không có nội dung câu hỏi** (BR-023) |
| Sự kiện sử dụng | PostgreSQL, bảng `usage_events` | Quản lý (báo cáo tổng hợp S-07) | Chỉ gồm người dùng, loại sự kiện, thời điểm. **Không có nội dung** |
| Đánh giá câu trả lời | PostgreSQL, bảng `feedback` | Chủ hội thoại; tổng hợp cho quản lý | Giá trị `helpful`/`not_helpful` |
| Tài khoản, quyền, phiên | PostgreSQL, bảng `users`, `access_grants`, `sessions`, `login_failures` | Hệ thống; quản trị bảo mật (S-05) | Mật khẩu băm Argon2id; cookie phiên chỉ chứa mã ngẫu nhiên, bảng lưu bản băm SHA-256 |
| Log ứng dụng | stdout của container (JSON) → hệ thống log của tổ chức (AQ-005) | Đội vận hành | **Không chứa nội dung tài liệu hay câu hỏi** — mục 3 |
| Số liệu giám sát | Prometheus (`/metrics`, cổng worker 9100) | Đội vận hành | Chỉ số đếm và thời gian, không có nội dung |

## 2. Dữ liệu ra khỏi hạ tầng (Kịch bản A — dịch vụ AI bên ngoài)

Kịch bản A dùng Claude API (`claude-opus-5-5`) để sinh câu trả lời (`app/adapters/claude_llm.py`). Với **mỗi câu hỏi** được gửi đi:

| Gửi ra ngoài | Không gửi ra ngoài |
|---|---|
| Các chunk được truy xuất cho câu hỏi đó (mặc định tối đa `TOP_K` = 8 đoạn, mỗi đoạn tối đa `CHUNK_TOKENS` ≈ 500 token), kèm tên tệp và số trang | Toàn bộ tài liệu, tệp PDF gốc |
| Nội dung câu hỏi | Vector embedding |
| Ngữ cảnh hội thoại: `HISTORY_TURNS` = 4 lượt hỏi-đáp gần nhất trong cùng hội thoại | Bản ghi kiểm toán, sự kiện sử dụng, thông tin tài khoản |
| Chỉ dẫn hệ thống cố định | Tài liệu không thuộc phạm vi người hỏi (lọc trong truy vấn, ADR-004) |

- Câu hỏi có điểm truy xuất dưới `MIN_RELEVANCE_SCORE` **không được gửi** ra ngoài (lớp từ chối 1, `app/modules/qa/service.py`).
- Khóa API đọc từ biến môi trường/kho bí mật (`ANTHROPIC_API_KEY`), không nằm trong mã hay kho mã.
- Chính sách lưu giữ dữ liệu phía nhà cung cấp, vùng xử lý và điều khoản hợp đồng: **[TBD: OQ-005, OQ-006]** — bộ phận pháp chế/bảo mật xác nhận trước khi dùng tài liệu thật.
- **Kịch bản B** (OQ-006 = không gửi ra ngoài): thay adapter bằng máy chủ suy luận nội bộ cùng giao diện `AnswerGenerator`; khi đó không có dữ liệu nào rời hạ tầng. Phải chạy lại bộ đánh giá đầy đủ khi đổi adapter (ADR-012).
- Cho tới khi OQ-006 có quyết định: chỉ dùng **dữ liệu mẫu không nhạy cảm** (bộ PDF tổng hợp ở `evaluation/spikes/corpus`).

## 3. Log và sự kiện không chứa nội dung (ADR-009)

Cơ chế:
1. Log truy cập chỉ có phương thức, mẫu đường dẫn (ví dụ `/api/v1/documents/{document_id}`), mã trạng thái, thời gian, ID yêu cầu. Không ghi thân yêu cầu hay chuỗi truy vấn (`app/observability/middleware.py`).
2. Bộ lọc của structlog xóa mọi trường tên `question`, `content`, `text`, `body`, `answer`, `cited_text`, `password`, `history` ở mọi độ sâu (`app/observability/logging.py`).
3. Lỗi xác thực dữ liệu đầu vào chỉ ghi tên trường lỗi, không ghi giá trị; phản hồi lỗi không lặp lại dữ liệu người dùng gửi (`app/api/errors.py`).
4. Lỗi chưa xử lý trả thông điệp chung, không lộ stack trace.
5. `usage_events` và `audit_records` không có cột nội dung (kiểm thử `test_audit_and_usage_tables_have_no_content_columns`).
6. nginx (production) ghi log truy cập dạng `combined` — không có thân yêu cầu.

**Kiểm thử tự động "canary"** (`backend/tests/security/test_no_content_in_logs.py`, chạy trong CI): chạy trọn luồng tải lên → hỏi đáp (có nguồn và không tìm thấy) → mở nguồn → đánh giá → câu hỏi quá dài → xóa → xóa vĩnh viễn với chuỗi đánh dấu duy nhất trong tài liệu và câu hỏi; gom toàn bộ log mức DEBUG và nội dung các bảng `usage_events`, `audit_records`, `jobs`; khẳng định chuỗi đánh dấu không xuất hiện. **Kết quả: đạt** (2026-10-22).

Kiểm thử liên quan khác: `tests/unit/test_framework.py::test_request_log_does_not_contain_question_value`, `test_validation_error_does_not_echo_input`, `test_unhandled_error_has_standard_format_without_stack_trace`.

## 4. Thời gian lưu

| Dữ liệu | Thời gian lưu hiện tại | Cơ chế | Quyết định |
|---|---|---|---|
| Tài liệu, chunk, tệp gốc | Tới khi người dùng xóa | Xóa → `deleting` → worker xóa vĩnh viễn (mục 5) | OQ-012 |
| Bản ghi kiểm toán | `AUDIT_RETENTION_DAYS` = 365 ngày | Worker dọn định kỳ (`app/worker/maintenance.py`) | OQ-012 |
| Câu hỏi/câu trả lời (`messages`), trích dẫn, đánh giá | Giao diện chỉ giữ hội thoại trong phiên trình duyệt; hội thoại không hoạt động quá `MESSAGE_RETENTION_DAYS` = 60 ngày bị xóa định kỳ (kèm tin nhắn, trích dẫn, đánh giá) | Worker dọn định kỳ (`conversation/service.py: cleanup_inactive`), kiểm thử `test_inactive_conversations_are_cleaned_up` | PQ-004 — giá trị 60 ngày là đề xuất, chờ chốt |
| Sự kiện sử dụng | Không giới hạn (không có nội dung) | — | OQ-012 |
| Phiên đăng nhập | Hết hạn sau `SESSION_IDLE_HOURS` = 8 giờ không hoạt động; xóa khi đăng xuất hoặc bị thu hồi quyền | `app/modules/access/service.py` | DQ-003 |
| Lần đăng nhập sai | 15 phút (cửa sổ giới hạn) | Dọn khi kiểm tra | — |

## 5. Quy trình xóa tài liệu (US-006, US-007; ADR-008)

1. `DELETE /documents/{id}` (chủ sở hữu hoặc quản trị bảo mật): trong **một giao dịch**, tài liệu chuyển `deleting`, ghi `deleted_at`, thêm việc `purge`. Từ thời điểm này tài liệu **không còn được truy xuất** vì truy vấn chỉ lấy `ready` (kiểm thử `test_deleted_document_is_excluded_immediately`, AC-005).
2. Worker `purge` (`app/modules/documents/purge.py`): xóa toàn bộ chunk → xóa đoạn trích nguyên văn (`cited_text`) trong các trích dẫn đã lưu, chỉ giữ tên tài liệu và số trang → xóa tệp trên kho → `status = deleted`, ghi `purged_at`. Mỗi bước làm lại được; lỗi kho tệp được thử lại (kiểm thử `test_purge_removes_chunks_file_and_sets_purged_at`, `test_storage_error_midway_is_retried_and_completes`, AC-024).
3. Giám sát: số liệu `documents_deleting_overdue` và cảnh báo `DocumentsDeletingOverdue` khi có tài liệu `deleting` quá `PURGE_SLA_HOURS` = 24 giờ.
4. **Còn lại sau khi xóa vĩnh viễn:** bản ghi `documents` (tên tệp, dung lượng, thời điểm — phục vụ kiểm toán), id tài liệu trong `audit_records`, tên tệp và số trang trong `citations`, và **nội dung câu trả lời đã sinh** trong `messages` (có thể diễn đạt lại thông tin của tài liệu). Các câu trả lời này bị xóa cùng hội thoại sau `MESSAGE_RETENTION_DAYS` (mục 4), không xóa ngay khi tài liệu bị xóa. Có cần xóa ngay hay không phụ thuộc PQ-004 — **cần quyết định** trước launch.

## 6. Mã hóa và bảo vệ truy cập

| Lớp | Hiện trạng | Việc cần làm trước launch |
|---|---|---|
| Đường truyền trình duyệt ↔ hệ thống | TLS kết thúc ở bộ cân bằng tải; cookie phiên `HttpOnly; Secure; SameSite=Lax` | Cấu hình TLS ở hạ tầng của tổ chức (AQ-004) |
| Backend ↔ PostgreSQL / S3 / Claude API | Claude API qua HTTPS; PostgreSQL và S3 trong mạng nội bộ | Bật TLS cho PostgreSQL và S3 nếu khác mạng (OQ-005) |
| Lưu trữ tệp | Hỗ trợ mã hóa phía máy chủ qua `S3_SERVER_SIDE_ENCRYPTION` (`AES256` hoặc `aws:kms`) | Bật trên kho thật (OQ-005) |
| Cơ sở dữ liệu | Theo hạ tầng | Mã hóa ổ đĩa / dịch vụ quản lý (OQ-005) |
| Mật khẩu | Argon2id, so sánh thời gian không đổi, giới hạn 5 lần sai / 15 phút theo tài khoản (20 lần theo địa chỉ) | — |
| CSRF | Mọi yêu cầu thay đổi dữ liệu phải có `Origin`/`Referer` thuộc `ALLOWED_ORIGINS` | Cập nhật `ALLOWED_ORIGINS` theo tên miền thật |
| Phân quyền | Vai trò lấy từ `access_grants` (không lấy từ IdP); phạm vi tài liệu tính ở một hàm duy nhất `allowed_document_ids` và lọc ngay trong câu truy vấn | Kiểm thử `tests/security/test_auth_matrix.py`, `test_isolation.py` tự mở rộng khi thêm route |
| Giao diện | CSP `default-src 'self'`, `frame-ancestors 'none'`, `nosniff` (`deploy/nginx.conf`); nội dung câu trả lời hiển thị dạng văn bản đã thoát ký tự | — |

## 7. Sao lưu (AQ-003 — rủi ro mở)

Dữ liệu đã xóa vĩnh viễn vẫn có thể còn trong **bản sao lưu** cơ sở dữ liệu và kho tệp cho tới khi bản sao lưu hết hạn. Phương án đề xuất, chờ AQ-003:
- Giữ bản sao lưu tối đa N ngày [Đề xuất: 30] và ghi rõ trong thông báo cho người dùng rằng dữ liệu đã xóa sẽ biến mất khỏi bản sao lưu sau N ngày; hoặc
- Khi khôi phục từ bản sao lưu, chạy lại việc xóa cho mọi tài liệu có `deleted_at` sau thời điểm sao lưu (danh sách lấy từ cơ sở dữ liệu hiện hành trước khi khôi phục) — quy trình ở `ops_runbook.md`.

## 8. Ứng phó sự cố lộ dữ liệu

Xem `ops_runbook.md` mục "Sự cố lộ dữ liệu": thu hồi khóa, vô hiệu phiên, khoanh vùng theo `audit_records`, thông báo theo quy định của tổ chức (OQ-005).

## 9. Xác nhận

| Vai trò | Họ tên | Kết luận | Ngày |
|---|---|---|---|
| Bộ phận bảo mật | | Chờ rà soát | |
| Pháp chế (OQ-005, OQ-006) | | Chờ rà soát | |
| Chủ sản phẩm | | | |
