# DANH SÁCH TASK TRIỂN KHAI — "CHAT VỚI TÀI LIỆU" (MVP)

> Tài liệu này tách `docs/implement/implement_plan.md` thành các task nhỏ, mỗi task một người nhận được và làm xong trong tối đa vài ngày.
> Đọc kèm: `implement_plan.md` (mục 3 dữ liệu, 4 API, 5 luồng xử lý, 6 cổng/adapter, 10.3 cấu hình), `docs/requirements/UserStories.md` (AC), `docs/design/html_design/` (giao diện mẫu và ảnh trong `screenshots/`).
> Quy ước: `[TBD: …]` = chờ quyết định, dùng giá trị tạm trong cấu hình (implement_plan mục 10.3 và 13); `[Đề xuất]` = giá trị khởi điểm có thể chỉnh.

## Cách đọc một task

| Trường | Ý nghĩa |
|---|---|
| **ID** | `T<sprint>-<số>`; không đổi sau khi đã phát hành kế hoạch |
| **Story / Loại** | Story liên quan và loại việc: BE (backend), FE (frontend), QA, OPS (hạ tầng/vận hành), SPK (spike khảo sát) |
| **Phụ thuộc** | Task phải xong trước |
| **Cỡ** | S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người (tương đối, chưa quy đổi — OQ-009) |
| **Làm gì** | Mô tả việc và các bước |
| **Sản phẩm** | Tệp/hạng mục phải có trong kho mã |
| **Xong khi** | Điều kiện kiểm tra được; người nhận không chuyển trạng thái "Done" nếu một điều kiện chưa đạt |

Mọi task đều phải tuân theo **Định nghĩa hoàn thành chung** ở cuối tài liệu.

## Tổng quan

| Sprint | Số task | Mục tiêu demo | Story |
|---|---|---|---|
| 0 | T0-01..T0-10 | Ứng dụng rỗng chạy được; spike xong | — |
| 1 | T1-01..T1-21 | Đăng nhập; tải nhiều PDF; trạng thái và lỗi | US-017, 001..005 |
| 2 | T2-01..T2-14 | Hỏi đáp có nguồn và trình xem nguồn | US-008, 009, 011, 012, 014, 015 |
| 3 | T3-01..T3-08 | Xóa; phạm vi quyền; kiểm toán; hỏi tiếp | US-006, 007, 010, 013, 018, 020 |
| 4 | T4-01..T4-08 | Chất lượng, báo cáo, sẵn sàng phát hành | US-016, 019, 021..024 |

---

## SPRINT 0 — Nền tảng và spike

### T0-01 · Khởi tạo kho mã và công cụ · OPS · M
- **Phụ thuộc:** —
- **Làm gì:**
  1. Tạo monorepo theo cấu trúc ở `implement_plan.md` mục 2: `backend/`, `frontend/`, `evaluation/`, `e2e/`, `deploy/`.
  2. Backend: `pyproject.toml` (Python 3.12), phụ thuộc FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, structlog; công cụ ruff, mypy, pytest, import-linter.
  3. Frontend: Vite + React 18 + TypeScript; eslint, Vitest, Testing Library.
  4. Cấu hình `import-linter` với hai hợp đồng: `modules` không import `adapters`; `api` không import trực tiếp `adapters`.
  5. Tệp `README.md` gốc: cách chạy cục bộ, cách chạy kiểm thử.
- **Sản phẩm:** cây thư mục, `pyproject.toml`, `package.json`, `.importlinter`, `README.md`.
- **Xong khi:** `pytest` (với một kiểm thử mẫu), `ruff`, `mypy`, `import-linter`, `npm test`, `npm run lint` đều chạy xanh trên máy sạch theo README.

### T0-02 · Docker Compose môi trường cục bộ · OPS · M
- **Phụ thuộc:** T0-01
- **Làm gì:** `deploy/docker-compose.yml` với `postgres` (ảnh có `pgvector`), `minio`, `backend` (uvicorn), `worker` (`python -m app.worker.run`), `frontend` (Vite, proxy `/api` → backend). Tệp `deploy/env.example` liệt kê mọi biến ở `implement_plan.md` mục 10.3. Volume dùng chung cho mô hình embedding.
- **Sản phẩm:** `deploy/docker-compose.yml`, `deploy/env.example`, `deploy/Dockerfile.backend`, `deploy/Dockerfile.frontend`.
- **Xong khi:** `docker compose up` trên máy sạch khởi động đủ dịch vụ; `GET http://localhost:8000/health/live` trả 200; trang frontend rỗng mở được.

### T0-03 · Pipeline CI · OPS · M
- **Phụ thuộc:** T0-01
- **Làm gì:** pipeline có các bước: lint, kiểm tra kiểu, import-linter, unit, tích hợp (testcontainers), build ảnh Docker (`implement_plan.md` mục 10.4, bước 1–3). Công cụ CI theo AQ-004; nếu chưa chốt, dùng GitHub Actions.
- **Sản phẩm:** tệp cấu hình CI.
- **Xong khi:** pull request thử với một lỗi lint cố ý làm CI đỏ; sửa lỗi thì xanh.

### T0-04 · Khung backend: cấu hình, log, lỗi, health · BE · M
- **Phụ thuộc:** T0-01
- **Làm gì:**
  1. `app/config.py`: lớp `Settings` (Pydantic) đọc môi trường; **mọi ngưỡng** ở `implement_plan.md` mục 10.3 là trường có giá trị mặc định tạm thời.
  2. `app/main.py`: khởi tạo FastAPI, đăng ký router rỗng, middleware ID yêu cầu.
  3. `app/api/errors.py`: định dạng lỗi `{"error": {"code", "message"}}`, bộ xử lý ngoại lệ chung (mục 4 của plan). Thông báo lỗi không chứa chi tiết kỹ thuật.
  4. `app/observability/`: log JSON bằng structlog **kèm bộ lọc che nội dung** (xóa trường `question`, `content`, `text`, `body` khỏi log), số liệu Prometheus, `/health/live` và `/health/ready` (kiểm cơ sở dữ liệu).
  5. Middleware không ghi thân yêu cầu cho `POST /documents` và `POST /conversations/*/messages`.
- **Sản phẩm:** `config.py`, `main.py`, `api/errors.py`, `observability/*`.
- **Xong khi:** kiểm thử đơn vị chứng minh (a) lỗi chưa xử lý trả đúng định dạng và không lộ stack trace; (b) log của một yêu cầu có trường `question` không chứa giá trị đó.

### T0-05 · Khung frontend và token giao diện · FE · M
- **Phụ thuộc:** T0-01
- **Làm gì:**
  1. Chuyển biến màu, kiểu chữ, khoảng cách từ `docs/design/html_design/styles.css` thành token (CSS variables) ở `frontend/src/styles/`.
  2. AppShell (C-00): header, vùng nội dung, vùng thông báo; router với các tuyến `/login`, `/`, `/admin/access`, `/admin/audit`, `/reports`.
  3. Thành phần dùng chung: `ErrorBanner` (C-16), `EmptyState` (C-10), `StatusBadge` (C-06) — mỗi cái có story/test dựng (Testing Library).
  4. Liên kết "bỏ qua tới nội dung chính" và `:focus-visible` như giao diện mẫu.
  5. Client API: sinh kiểu TypeScript từ OpenAPI của backend (`openapi-typescript`); bọc `fetch` có xử lý 401 → điều hướng `/login`.
- **Sản phẩm:** `frontend/src/app/*`, `components/*`, `styles/*`, `api/client.ts`.
- **Xong khi:** `npm run dev` hiển thị shell; ba thành phần dùng chung có kiểm thử đơn vị; kiểm tra axe không báo lỗi trên shell.

### T0-06 · Spike trích xuất PDF · SPK · M
- **Phụ thuộc:** T0-01; tập PDF mẫu từ business owner (DEP-001; nếu chưa có, dùng PDF công khai không nhạy cảm)
- **Làm gì:** viết script `evaluation/spikes/extract.py` thử `pypdf` và `pdfplumber` trên ít nhất 20 PDF. Đo: tỷ lệ trang có văn bản, lỗi với tiếng Việt (dấu), chất lượng với bảng và nhiều cột, thời gian mỗi trang.
- **Sản phẩm:** `evaluation/spikes/extract.py` và báo cáo `docs/implement/spike_pdf.md` (một đến hai trang): kết luận chọn thư viện, các loại PDF kém, đề xuất giới hạn MVP.
- **Xong khi:** báo cáo nêu rõ chọn thư viện nào và vì sao; nêu tỷ lệ PDF thuộc loại "không có văn bản" để xác nhận ADR-010.

### T0-07 · Spike embedding và truy xuất tiếng Việt · SPK · M
- **Phụ thuộc:** T0-06
- **Làm gì:** nạp 1–2 mô hình embedding đa ngôn ngữ (ví dụ `BAAI/bge-m3`); cắt chunk 400/500/600 token trên cùng tập PDF; với 20–30 câu hỏi mẫu có đáp án đã biết, đo tỷ lệ chunk đúng nằm trong top-K (K = 4, 8, 12). Ghi số chiều vector và thời gian embedding mỗi chunk.
- **Sản phẩm:** `evaluation/spikes/retrieval.py` và `docs/implement/spike_embedding.md`.
- **Xong khi:** báo cáo chốt `EMBEDDING_MODEL`, `EMBEDDING_DIM`, giá trị khởi điểm cho `CHUNK_TOKENS` và `TOP_K`.

### T0-08 · Spike sinh câu trả lời có trích dẫn · SPK · S
- **Phụ thuộc:** T0-07; dữ liệu **không nhạy cảm**; khóa API (không commit)
- **Làm gì:** script gọi Claude (`claude-opus-5-5`, SDK `anthropic`) với các chunk là khối `document` bật `citations` (phác thảo ở `implement_plan.md` mục 6.4). Kiểm: (a) citation trỏ đúng chunk (`document_index`); (b) câu hỏi ngoài phạm vi có nhận câu từ chối cố định không; (c) `effort` `low` so với `medium`; (d) `usage.cache_read_input_tokens` ở lượt thứ hai.
- **Sản phẩm:** `evaluation/spikes/generate.py` và `docs/implement/spike_generation.md`.
- **Xong khi:** báo cáo xác nhận ánh xạ citation → trang hoạt động; nêu `ANSWER_EFFORT` khởi điểm; ghi chi phí mỗi câu hỏi mẫu (đầu vào RSK-005).

### T0-09 · Khung bộ đánh giá · QA · S
- **Phụ thuộc:** T0-01
- **Làm gì:** `evaluation/run_eval.py` đọc `datasets/*.jsonl` (định dạng ở `implement_plan.md` mục 9.4), gọi một hàm `ask(question, history)` trừu tượng, tính các chỉ số mục 9.4 và ghi báo cáo JSON + Markdown. Kèm 5 câu mẫu và bộ gọi giả để chạy thử không cần AI thật.
- **Sản phẩm:** `evaluation/run_eval.py`, `evaluation/datasets/sample.jsonl`, `evaluation/README.md`.
- **Xong khi:** chạy với bộ gọi giả cho ra báo cáo có đủ các chỉ số; kiểm thử đơn vị cho từng công thức chỉ số.

### T0-10 · Nền cơ sở dữ liệu và kiểm thử tích hợp · BE · S
- **Phụ thuộc:** T0-04
- **Làm gì:** cấu hình Alembic; migration đầu tiên tạo `CREATE EXTENSION vector`; fixture pytest dùng testcontainers (PostgreSQL có pgvector và MinIO) chạy migration trước mỗi phiên kiểm thử; hàm tạo dữ liệu mẫu.
- **Sản phẩm:** `backend/alembic/*`, `backend/tests/conftest.py`.
- **Xong khi:** kiểm thử tích hợp mẫu chạy được trên CI và cục bộ; `alembic upgrade head` và `downgrade base` đều thành công.

**Cổng G0 (cuối Sprint 0):** chốt bộ công nghệ, DQ-003, kết quả ba spike.

---

## SPRINT 1 — Truy cập và nạp tài liệu

### Story US-017 — Chỉ người được cấp quyền

### T1-01 · Migration `users`, `access_grants` · BE · S
- **Phụ thuộc:** T0-10
- **Làm gì:** tạo hai bảng đúng như `implement_plan.md` mục 3 và các mô hình SQLAlchemy; chỉ mục theo `login`.
- **Xong khi:** migration lên/xuống thành công; ràng buộc `CHECK` từ chối vai trò hoặc trạng thái sai (kiểm thử).

### T1-02 · Cổng xác thực và adapter tài khoản nội bộ · BE · M
- **Phụ thuộc:** T1-01
- **Làm gì:** `ports/identity.py` (`IdentityProvider`); `adapters/local_identity.py`: băm Argon2id, kiểm tra mật khẩu, giới hạn đăng nhập sai `[Đề xuất: 5 lần / 15 phút]` theo tài khoản và địa chỉ; so sánh thời gian không đổi.
- **Sản phẩm:** `ports/identity.py`, `adapters/local_identity.py`, kiểm thử đơn vị.
- **Xong khi:** kiểm thử: đúng mật khẩu → thành công; sai → thất bại; quá giới hạn → bị khóa tạm; thông báo lỗi không phân biệt "sai tên" với "sai mật khẩu".

### T1-03 · Adapter OIDC (chỉ làm nếu DQ-003 chọn OIDC) · BE · M
- **Phụ thuộc:** T1-02, G0
- **Làm gì:** `adapters/oidc_identity.py`: Authorization Code + PKCE; `GET /auth/oidc/login`, `GET /auth/oidc/callback`; ánh xạ `sub`/email → `users.login`; **vai trò không lấy từ IdP** mà từ `access_grants`.
- **Xong khi:** kiểm thử với một IdP giả (mock server): đăng nhập thành công tạo/khớp `users`, người không có `access_grants` nhận 403 `no_access`. Nếu DQ-003 = tài khoản nội bộ, đánh dấu task "Won't do" và ghi lý do.

### T1-04 · Phiên, endpoint xác thực và `require_role` · BE · M
- **Phụ thuộc:** T1-02
- **Làm gì:**
  1. Phiên lưu phía máy chủ, cookie `HttpOnly; Secure; SameSite=Lax`, hết hạn sau `SESSION_IDLE_HOURS` không hoạt động.
  2. `POST /auth/login`, `POST /auth/logout`, `GET /auth/me` (`{user, role}`).
  3. Phụ thuộc FastAPI `current_user` và `require_role(*roles)`: 401 `session_expired` khi hết phiên, 403 `no_access` khi chưa được cấp quyền hoặc đã `revoked`, 403 `forbidden_role` khi sai vai trò.
  4. Bảo vệ CSRF (kiểm tra header `Origin` hoặc token) cho yêu cầu thay đổi dữ liệu.
  5. Phát sự kiện `session_started` và `access_denied` vào `usage_events` (bảng tạo ở T2-01 — tạm ghi log, bổ sung ghi bảng khi T2-01 xong).
- **Xong khi:** kiểm thử tích hợp: không có phiên → 401; người `revoked` → 403 ở yêu cầu kế tiếp (AC-014); thiếu `Origin` hợp lệ khi `POST` → bị từ chối.

### T1-05 · Endpoint quản lý quyền và tài khoản đầu tiên · BE · M
- **Phụ thuộc:** T1-04
- **Làm gì:** `GET /admin/access`, `POST /admin/access` (`{login, role}`; tạo `users` nếu chưa có), `DELETE /admin/access/{user_id}` (đặt `revoked`, không xóa bản ghi); chỉ vai trò `security_admin`. Lệnh quản trị `python -m app.cli create-admin <login>` tạo tài khoản quản trị bảo mật đầu tiên.
- **Xong khi:** kiểm thử: vai trò khác gọi → 403; thu hồi xong người đó không đăng nhập hoặc không gọi API được; lệnh `create-admin` chạy được trên cơ sở dữ liệu trống.

### T1-06 · Màn hình S-01 Đăng nhập và AuthGate · FE · M
- **Phụ thuộc:** T0-05, T1-04
- **Làm gì:** dựng S-01 theo `html_design/S-01-dang-nhap.html` và ảnh `s01-default`, `s01-wrong`, `s01-noaccess`, `s01-expired`: bốn trạng thái từ mã lỗi 401/403 của API. `AuthGate` (C-01): kiểm tra `/auth/me`; 401 → điều hướng `/login` và lưu tạm câu hỏi đang soạn trong `sessionStorage`. Điều hướng sau đăng nhập: `bd` → `/`, `security_admin` → `/admin/access`, `manager` → `/reports`.
- **Xong khi:** kiểm thử Testing Library cho cả bốn trạng thái; E2E: đăng nhập đúng, sai, không có quyền, hết phiên; axe không có lỗi nghiêm trọng.

### T1-07 · Màn hình S-05 Quản lý quyền · FE · M
- **Phụ thuộc:** T1-05, T1-06
- **Làm gì:** dựng S-05 theo `S-05-quan-ly-quyen.html` và ảnh `s05-default`, `s05-confirm`, `s05-empty`: biểu mẫu cấp quyền, bảng người dùng, thu hồi có xác nhận, trạng thái trống. Cột "Phạm vi tài liệu" hiển thị `[TBD: OQ-003]` cho tới khi có quyết định.
- **Xong khi:** thao tác cấp và thu hồi chạy với backend thật; thu hồi phải qua bước xác nhận; kiểm thử cho ba trạng thái.

### T1-08 · Kiểm thử bảo mật xác thực · QA · S
- **Phụ thuộc:** T1-04, T1-05
- **Làm gì:** kiểm thử tự động liệt kê **mọi route** của ứng dụng (từ OpenAPI) và khẳng định: mọi route trừ `/auth/login`, `/auth/oidc/*`, `/health/*` trả 401 khi không có phiên; mọi route `/admin/*` trả 403 với `bd` và `manager`. Kiểm thử này tự mở rộng khi thêm route mới.
- **Sản phẩm:** `backend/tests/security/test_auth_matrix.py`.
- **Xong khi:** kiểm thử chạy trong CI; thêm một route chưa bảo vệ cố ý làm nó đỏ.

### Story US-001..005 — Nạp và quản lý tài liệu

### T1-09 · Migration `documents`, `jobs`, `chunks` · BE · S
- **Phụ thuộc:** T0-10
- **Làm gì:** tạo ba bảng đúng như mục 3 của plan, gồm các ràng buộc `CHECK` (trạng thái, lý do lỗi) và chỉ mục HNSW. `chunks.page` là `NOT NULL`. Số chiều vector đọc từ kết quả spike T0-07.
- **Xong khi:** migration lên/xuống; chèn `chunks` thiếu `page` bị từ chối; chèn `status` ngoài danh sách bị từ chối.

### T1-10 · Cổng lưu tệp và adapter kho đối tượng · BE · S
- **Phụ thuộc:** T0-02
- **Làm gì:** `ports/storage.py` (`FileStore.put/get/delete`); `adapters/s3_file_store.py` dùng giao thức S3 (MinIO khi phát triển). `delete` không báo lỗi khi khóa không còn. Mã hóa phía máy chủ bật theo cấu hình.
- **Xong khi:** kiểm thử tích hợp với MinIO: ghi, đọc, xóa, xóa lần hai không lỗi.

### T1-11 · Endpoint `POST /documents` (kiểm tra tệp) · BE · M
- **Phụ thuộc:** T1-04, T1-09, T1-10
- **Làm gì:** theo `implement_plan.md` mục 5.1 phần "Trong `POST /documents`":
  1. Nhận nhiều tệp (multipart), xử lý **từng tệp độc lập**.
  2. Kiểm tra `MAX_FILE_BYTES` (`too_large`), 5 byte đầu `%PDF-` (`not_pdf`, không tin đuôi tệp hay `Content-Type`), `MAX_DOCS_PER_USER`.
  3. Tệp hợp lệ: lưu vào kho với khóa `documents/{owner_id}/{document_id}.pdf`; tạo `documents` ở trạng thái `processing`; thêm `jobs(kind='ingest')` **trong cùng giao dịch** với bản ghi tài liệu.
  4. Trả danh sách kết quả từng tệp `{id, file_name, status, failure_reason?}`.
  5. Phát sự kiện `document_upload_started`, `_succeeded`, `_failed` (nhóm lý do, không có nội dung).
- **Xong khi:** kiểm thử tích hợp: một yêu cầu gồm 1 PDF hợp lệ + 1 `.txt` đổi đuôi `.pdf` + 1 tệp vượt giới hạn → kết quả đúng cho từng tệp; tệp hợp lệ vẫn được nhận.

### T1-12 · Hàng đợi việc và vòng lặp worker · BE · M
- **Phụ thuộc:** T1-09
- **Làm gì:** `app/worker/run.py`: vòng lặp lấy việc bằng `UPDATE … FOR UPDATE SKIP LOCKED` (đoạn SQL ở mục 5.1 của plan); đăng ký bộ xử lý theo `kind` (`ingest`, `purge`); thử lại với thời gian chờ tăng dần tới `JOB_MAX_ATTEMPTS`, quá số lần → `failed` kèm `last_error`; chạy `WORKER_CONCURRENCY` việc song song; tắt êm khi nhận tín hiệu dừng. Phát số liệu độ dài hàng đợi.
- **Xong khi:** kiểm thử tích hợp: hai worker chạy đồng thời không bao giờ lấy cùng một việc; việc lỗi tạm thời được thử lại; việc quá số lần thử chuyển `failed`.

### T1-13 · Mô-đun trích xuất PDF theo trang · BE · M
- **Phụ thuộc:** T0-06
- **Làm gì:** `modules/ingestion/extract.py`: `extract_pages(stream) -> list[PageText]` dùng thư viện đã chọn ở spike. Phát hiện tài liệu mã hóa (`encrypted`), hỏng (`corrupted`), không có văn bản (`no_text`, tổng ký tự < `MIN_TEXT_CHARS`). Chuẩn hóa Unicode NFC và khoảng trắng. Số trang bắt đầu từ 1.
- **Xong khi:** kiểm thử đơn vị trên bộ PDF tổng hợp ở `backend/tests/fixtures/` (PDF thường, tiếng Việt, mã hóa, hỏng, chỉ ảnh): mỗi tệp cho đúng kết quả hoặc đúng loại lỗi; số trang khớp.

### T1-14 · Mô-đun cắt chunk theo trang · BE · S
- **Phụ thuộc:** T1-13
- **Làm gì:** `modules/ingestion/chunking.py`: cắt mỗi trang thành các chunk `CHUNK_TOKENS` có chồng lấp `CHUNK_OVERLAP`, **không vượt qua ranh giới trang**; mỗi chunk có `page`, `ordinal`, `text`. Đếm token bằng bộ đếm tương thích với mô hình embedding đã chọn.
- **Xong khi:** kiểm thử đơn vị: không chunk nào chứa văn bản của hai trang; trang ngắn cho đúng một chunk; trang rỗng không sinh chunk; tổng văn bản các chunk (bỏ phần chồng lấp) bằng văn bản trang.

### T1-15 · Embedding và hoàn tất việc nạp · BE · L
- **Phụ thuộc:** T1-12, T1-13, T1-14, T0-07
- **Làm gì:**
  1. `ports/ai.py`: `EmbeddingProvider`; `adapters/local_embedding.py`: nạp mô hình một lần khi khởi động, `embed(texts)` theo lô `EMBED_BATCH`, chuẩn hóa vector độ dài 1.
  2. Bộ xử lý `ingest`: đọc tệp từ kho → trích xuất → chunk → embedding → ghi **toàn bộ** chunk và cập nhật `status='ready'`, `page_count` trong một giao dịch (mục 5.1 bước 7). Nếu tài liệu đã chuyển `deleting` trong lúc xử lý, bỏ kết quả.
  3. Ánh xạ lỗi từ T1-13 sang `status='failed'` + `failure_reason`.
  4. Lỗi tạm thời → thử lại theo T1-12.
- **Xong khi:** kiểm thử tích hợp: PDF hợp lệ → `ready`, mọi chunk có `page` và vector đúng số chiều; PDF mã hóa → `failed/encrypted`; không có trường hợp tài liệu `ready` mà thiếu chunk (giao dịch nguyên tử).

### T1-16 · Endpoint danh sách, chi tiết, thử lại tài liệu · BE · S
- **Phụ thuộc:** T1-11, T1-15
- **Làm gì:** `GET /documents`, `GET /documents/{id}`, `POST /documents/{id}/retry` (chỉ khi `failed`; đặt `processing` và thêm việc mới). Chỉ trả tài liệu của người dùng (tạm thời `owner_id = user`; hàm `allowed_document_ids` đầy đủ ở T3-03); không trả `deleting`/`deleted`. Tài liệu của người khác → 404.
- **Xong khi:** kiểm thử: người dùng A không thấy và không gọi được tài liệu của B (404); thử lại chỉ chấp nhận khi `failed`.

### T1-17 · FE: nút tải lên và tiến độ · FE · M
- **Phụ thuộc:** T0-05, T1-11
- **Làm gì:** `UploadControl` (C-03) theo vùng "Tải PDF lên" ở `html_design/S-02-man-hinh-chinh.html`: chọn nhiều tệp, kéo thả, hiển thị tiến độ và kết quả **từng tệp**; kiểm tra phía trình duyệt (đuôi, kích thước) chỉ để phản hồi sớm, quyết định cuối ở backend; không khóa vùng hội thoại khi đang tải; xử lý mất kết nối: tệp chưa xong hiển thị "Chưa tải xong" kèm "Tải lại" (ảnh `s02-offline-upload`).
- **Xong khi:** kiểm thử Testing Library; E2E (Playwright chặn mạng giữa chừng): tệp chưa tải xong **không** xuất hiện là "Sẵn sàng".

### T1-18 · FE: danh sách tài liệu, trạng thái, lỗi, trạng thái trống · FE · M
- **Phụ thuộc:** T1-16, T1-17
- **Làm gì:** `DocumentList` (C-04) và `StatusBadge` (C-06) khớp ảnh `s02-default` và `s02-empty`: tên, số trang, dung lượng, nhãn Sẵn sàng/Đang xử lý/Lỗi; tệp lỗi có lý do, nút Thử lại và Xóa (nút Xóa nối vào T3-01). Hỏi trạng thái mỗi `POLL_INTERVAL_S` khi còn tài liệu `processing`, dừng khi không còn. Trạng thái trống (C-10) hướng dẫn tải PDF.
- **Xong khi:** kiểm thử cho ba trạng thái; hỏi định kỳ dừng khi không còn tài liệu đang xử lý; danh sách 200 mục không giật (ảo hóa nếu cần).

### T1-19 · Bảng thông báo lỗi tải lên (US-004) · FE · S
- **Phụ thuộc:** T1-18
- **Làm gì:** một tệp `frontend/src/features/documents/failureMessages.ts` ánh xạ `failure_reason` → câu tiếng Việt kèm cách khắc phục cho `corrupted`, `encrypted`, `not_pdf`, `too_large`, `no_text`, `network`, `internal`. Câu mẫu: "Tài liệu bị khóa hoặc mã hóa. Hãy mở khóa rồi tải lại." Mã không biết → câu chung, không hiện mã kỹ thuật.
- **Xong khi:** kiểm thử đơn vị: mỗi mã trả đúng một câu không rỗng; mã lạ trả câu chung (AC-018).

### T1-20 · Kiểm thử tích hợp luồng nạp · QA · M
- **Phụ thuộc:** T1-15, T1-16
- **Làm gì:** bộ kiểm thử tích hợp gọi API thật + worker thật + PostgreSQL/MinIO thật bằng bộ PDF tổng hợp: tải một tệp, tải nhiều tệp, từng loại lỗi, hai worker đồng thời, thử lại. Thêm kiểm thử vòng đời: mọi tài liệu `ready` có ≥ 1 chunk và mọi chunk có `page` hợp lệ (1..`page_count`).
- **Xong khi:** phủ AC-001, AC-002, AC-003, AC-004, AC-018; chạy trong CI dưới thời gian cho phép [Đề xuất: 5 phút].

### T1-21 · Kiểm thử E2E tải tài liệu · QA · S
- **Phụ thuộc:** T1-18, T1-19, T1-20
- **Làm gì:** Playwright: đăng nhập → tải PDF hợp lệ → thấy "Đang xử lý" rồi "Sẵn sàng"; tải tệp hỏng → thấy "Lỗi" cùng lý do; trạng thái trống khi chưa có tài liệu. Chạy axe trên màn hình chính.
- **Xong khi:** các kịch bản đạt; không có vi phạm axe mức nghiêm trọng.

---

## SPRINT 2 — Hỏi đáp có nguồn

**Cổng G1 (trước Sprint 2):** OQ-006 (kịch bản A/B), OQ-005 sơ bộ, OQ-007. Chưa có thì dùng Kịch bản A với dữ liệu mẫu không nhạy cảm.

### T2-01 · Migration hội thoại, trích dẫn, kiểm toán, sự kiện · BE · S
- **Phụ thuộc:** T1-09
- **Làm gì:** tạo `conversations`, `messages`, `citations`, `feedback`, `audit_records`, `usage_events` đúng mục 3 của plan. `audit_records` và `usage_events` **không có cột nội dung**. Bổ sung ghi `usage_events` cho T1-04.
- **Xong khi:** migration lên/xuống; xóa `messages` kéo theo `citations` và `feedback` (`ON DELETE CASCADE`).

### T2-02 · Mô-đun truy xuất · BE · M
- **Phụ thuộc:** T1-15, T2-01
- **Làm gì:** `modules/retrieval/search.py`: `search(query_embedding, allowed_document_ids, top_k) -> list[RetrievedChunk]` thực hiện đúng truy vấn ở mục 5.2 của plan; **bộ lọc quyền nằm trong truy vấn**, chỉ lấy tài liệu `ready`. Giới hạn `MAX_CHUNKS_PER_DOC` nếu cấu hình bật. Bật `hnsw.iterative_scan` hoặc tăng `ef_search` khi lọc bằng danh sách tài liệu.
- **Xong khi:** kiểm thử tích hợp: (a) chunk của tài liệu không thuộc danh sách cho phép **không bao giờ** xuất hiện; (b) tài liệu `deleting` không xuất hiện; (c) với danh sách tài liệu nhỏ trong kho lớn, vẫn trả đủ `top_k` kết quả.

### T2-03 · Cổng sinh câu trả lời và adapter Claude · BE · L
- **Phụ thuộc:** T0-08, T1-15
- **Làm gì:** `ports/ai.py` thêm `SourceChunk`, `GeneratedAnswer`, `AnswerGenerator` (mục 6.4 của plan). `adapters/claude_llm.py`:
  1. Mỗi chunk là một khối `document` văn bản bật `citations`, tiêu đề "tên tệp — trang N".
  2. Mô hình `ANSWER_MODEL` (mặc định `claude-opus-5-5`); đặt `effort` từ `ANSWER_EFFORT`; **không** đặt `thinking`; **không** dùng prefill; **không** dùng `output_config.format` (xung đột với citations).
  3. Chỉ dẫn hệ thống ở mục 5.3 của plan, có `cache_control`.
  4. Đọc `stop_reason` trước nội dung: `refusal` → `refused=True`; `max_tokens` → coi là lỗi.
  5. Bật chuyển mô hình dự phòng phía máy chủ khi bị từ chối (xác nhận cách truyền tham số theo phiên bản SDK đã cài).
  6. `timeout`, `max_retries`; bắt lỗi theo thứ tự `RateLimitError` → `APIStatusError` → `APIConnectionError`.
  7. Một adapter giả lập `fake_llm.py` trả citation định sẵn, dùng cho kiểm thử.
- **Xong khi:** kiểm thử đơn vị với phản hồi SDK được giả lập: citation được ánh xạ đúng chỉ số chunk; `refusal` xử lý đúng; kiểm thử có đánh dấu "cần khóa API" chạy thật trên dữ liệu mẫu ở môi trường kiểm thử.

### T2-04 · Điều phối hỏi đáp: ba lớp từ chối và ánh xạ nguồn · BE · L
- **Phụ thuộc:** T2-02, T2-03
- **Làm gì:** `modules/qa/service.py` thực hiện mục 5.3 của plan: nhúng câu hỏi → truy xuất → (1) điểm cao nhất < `MIN_RELEVANCE_SCORE` hoặc không có chunk → `not_found`, **không gọi mô hình**; (2) mô hình trả câu từ chối cố định → `not_found`; (3) có nội dung nhưng không có citation hợp lệ → `not_found`. Ánh xạ citation → `document_id`, `document_name`, `page`; gộp trùng; trả `latency_ms`.
- **Xong khi:** kiểm thử đơn vị với `fake_llm`: ba lớp từ chối đều cho `not_found=true`; câu trả lời có nội dung luôn có ≥ 1 citation; thứ tự và số trang của citation đúng.

### T2-05 · Endpoint hội thoại và ghi kiểm toán · BE · M
- **Phụ thuộc:** T2-04, T1-04
- **Làm gì:**
  1. `POST /conversations`, `POST /conversations/{id}/messages` (`{question}` → `{message_id, answer, not_found, citations, latency_ms}`).
  2. Kiểm tra câu hỏi không rỗng, ≤ `MAX_QUESTION_CHARS` (400).
  3. Trước khi gọi dịch vụ AI: ghi `audit_records` (người dùng, danh sách tài liệu được phép, thời điểm) và `usage_events(question_submitted)` — **không ghi nội dung câu hỏi** vào hai bảng này.
  4. Lưu `messages` và `citations`; phát `answer_returned` (thời gian phản hồi, số nguồn, cờ `not_found`).
  5. `ANSWER_TIMEOUT_S` → 504 `answer_timeout`.
  6. Hội thoại chỉ do chủ hội thoại truy cập.
- **Xong khi:** kiểm thử tích hợp (adapter giả): mỗi câu hỏi sinh đúng một `audit_records` không chứa nội dung; người dùng khác gọi vào hội thoại → 404; câu hỏi quá dài → 400.

### T2-06 · Endpoint trang nguồn và tệp gốc · BE · M
- **Phụ thuộc:** T1-16
- **Làm gì:** `GET /documents/{id}/pages/{page}` (`{page, page_count, text}`) và `GET /documents/{id}/file` (luồng tệp PDF qua backend, không trả đường dẫn kho). Kiểm quyền và `status='ready'`, nếu không → 404. Văn bản trang lấy bằng cách đọc lại tệp và trích đúng trang bằng mô-đun T1-13.
- **Xong khi:** kiểm thử: trang ngoài khoảng → 404; tài liệu người khác → 404; tài liệu `deleting` → 404.

### T2-07 · FE: khung hội thoại và ô nhập · FE · M
- **Phụ thuộc:** T1-18, T2-05
- **Làm gì:** `ChatPanel` (C-07), `MessageList` (C-08), `QuestionInput` (C-09) khớp ảnh `s02-default`: gửi bằng nút và Ctrl/Cmd+Enter; ô nhập vô hiệu kèm giải thích khi chưa có tài liệu `ready` (`s02-empty`); kiểm tra độ dài `[TBD: PQ-002]`; trạng thái "Đang xử lý câu hỏi…" xuất hiện ngay khi gửi.
- **Xong khi:** kiểm thử cho các trạng thái trống, mặc định, đang chờ; vô hiệu hóa đúng; focus quay về ô nhập sau khi có câu trả lời.

### T2-08 · FE: thẻ câu trả lời, nguồn, "không tìm thấy" · FE · M
- **Phụ thuộc:** T2-07
- **Làm gì:** `AnswerCard` (C-11) với `SourceChip` (C-12) "tên tài liệu, tr.N" (chọn chip điều hướng S-03); `NotFoundNotice` (C-15) như `s02-default` kèm gợi ý. Phát `source_opened` khi mở nguồn. Nội dung câu trả lời được hiển thị **dưới dạng văn bản đã thoát ký tự** (không render HTML từ mô hình).
- **Xong khi:** kiểm thử: câu trả lời có nguồn hiển thị chip đúng; `not_found` hiển thị khối cảnh báo, không hiển thị chip; chuỗi chứa `<script>` hiển thị nguyên văn, không thực thi.

### T2-09 · FE: màn hình S-03 Trình xem nguồn · FE · M
- **Phụ thuộc:** T2-06, T2-08
- **Làm gì:** dựng S-03 theo `S-03-trinh-xem-nguon.html`, ảnh `s03-default`, `s03-deleted`: thanh công cụ "Trang N / M" và nút trang trước/sau; hiển thị văn bản trang, tô sáng `cited_text` (tìm trong văn bản trang, nếu không thấy thì không tô sáng, không báo lỗi); cột nguồn bên phải; trạng thái tài liệu đã bị xóa khi API trả 404. Cách hiển thị (văn bản trang hay trình xem PDF) theo DQ-005; mặc định văn bản trang.
- **Xong khi:** kiểm thử cho hai trạng thái; chuyển trang không tải lại toàn bộ ứng dụng; trang nêu trong chip khớp trang hiển thị.

### T2-10 · FE: trạng thái lỗi khi hỏi · FE · S
- **Phụ thuộc:** T2-07
- **Làm gì:** trạng thái mất kết nối khi hỏi như `s02-offline-ask`: `ErrorBanner`, giữ câu hỏi trong ô nhập, nút đổi thành "Gửi lại", không hiển thị câu trả lời dở dang; xử lý 504, 401 (về S-01 giữ câu hỏi), lỗi chung.
- **Xong khi:** E2E chặn mạng khi gửi → câu hỏi được giữ lại và gửi lại được sau khi có mạng.

### T2-11 · Sự kiện phân tích phía FE · FE · S
- **Phụ thuộc:** T2-08
- **Làm gì:** endpoint `POST /events/source-opened` (chỉ nhận `{document_id, page}`; kiểm quyền; ghi `usage_events`) và gọi từ `SourceChip`. Không gửi nội dung.
- **Xong khi:** chọn chip tạo đúng một `usage_events(source_opened)`; kiểm thử log không chứa nội dung (xem T4-05).

### T2-12 · Kiểm thử tích hợp hỏi đáp · QA · M
- **Phụ thuộc:** T2-05, T2-06
- **Làm gì:** kiểm thử tích hợp với `fake_llm` trên PostgreSQL thật: câu hỏi có nguồn; câu hỏi dưới ngưỡng → không gọi mô hình (đếm số lần gọi); mô hình trả không có citation → `not_found`; truy cập trang nguồn hợp lệ/không hợp lệ.
- **Xong khi:** phủ AC-006, AC-009, AC-012, AC-019 ở tầng backend.

### T2-13 · Bộ câu hỏi chuẩn phiên bản 1 và đường cơ sở · QA · M
- **Phụ thuộc:** T0-09, T2-05; tập PDF và câu hỏi từ business owner (DEP-001, ASM-005)
- **Làm gì:** cùng business owner tạo `evaluation/datasets/v1.jsonl` với các loại `in_scope`, `out_of_scope`, `multi_doc` (≥ 10 câu mỗi loại [Đề xuất]); nối `run_eval.py` với API thật; chạy và lưu báo cáo đường cơ sở cùng phiên bản mã và cấu hình.
- **Xong khi:** có báo cáo đường cơ sở với MET-002, tỷ lệ bịa, độ phủ nguồn, độ trễ; business owner xác nhận đáp án mẫu.

### T2-14 · Kiểm thử E2E hỏi đáp · QA · S
- **Phụ thuộc:** T2-09, T2-10, T2-12
- **Làm gì:** Playwright với backend dùng `fake_llm`: tải PDF → hỏi → thấy câu trả lời kèm nguồn → chọn nguồn mở S-03 đúng trang → hỏi ngoài phạm vi thấy "không tìm thấy" → mất mạng khi hỏi. axe trên S-02 và S-03.
- **Xong khi:** các kịch bản đạt; phủ AC-006, AC-009, AC-012, AC-019 ở tầng giao diện.

---

## SPRINT 3 — Xóa, phạm vi quyền, kiểm toán, hội thoại

**Cổng G2 (trước Sprint 3):** OQ-003, OQ-012. Chưa có thì dùng giá trị tạm: chỉ tài liệu của chính mình; xóa ngay khi worker chạy; lưu bản ghi 365 ngày.

### T3-01 · Xóa tài liệu: endpoint và hộp thoại · BE+FE · M
- **Phụ thuộc:** T1-16, T2-02
- **Làm gì:**
  - **BE:** `DELETE /documents/{id}` (chủ sở hữu hoặc `security_admin`): trong một giao dịch đặt `status='deleting'`, `deleted_at=now()` và thêm `jobs(kind='purge')`; trả 202; phát `document_deleted`.
  - **FE:** `DeleteConfirmDialog` (C-05) khớp ảnh `s04-default` và `s04-failed`: tiêu điểm mặc định ở "Hủy", nêu tên tài liệu và "không thể hoàn tác", nêu thời hạn xóa `[TBD: OQ-012]`, lỗi hiển thị ngay trong hộp thoại.
- **Xong khi:** sau `DELETE` trả về, câu hỏi chỉ có đáp án trong tài liệu đó nhận `not_found` **ngay**, kể cả khi worker chưa chạy (AC-005); hộp thoại đóng bằng phím Esc và trả focus về nút gọi.

### T3-02 · Worker xóa vĩnh viễn · BE · M
- **Phụ thuộc:** T3-01, T1-12
- **Làm gì:** bộ xử lý `purge`: xóa `chunks` của tài liệu → xóa tệp trên kho → đặt `status='deleted'`, `purged_at=now()`. Mỗi bước làm lại được nhiều lần không lỗi. Cảnh báo nếu có tài liệu `deleting` quá `PURGE_SLA_HOURS`. Ghi vào `docs/implement/ops_runbook.md` cách xử lý bản sao lưu (AQ-003).
- **Xong khi:** kiểm thử tích hợp: sau khi worker chạy không còn chunk, không còn tệp trên MinIO, `purged_at` có giá trị (AC-024); giả lập lỗi kho tệp giữa chừng → thử lại và hoàn tất; chạy `purge` hai lần không lỗi.

### T3-03 · `allowed_document_ids` và ACL · BE · M
- **Phụ thuộc:** T1-16, T2-06; G2
- **Làm gì:** một hàm duy nhất `modules/access/scope.py: allowed_document_ids(user) -> set[UUID]` (tài liệu của chính mình ∪ `document_acl` nếu OQ-003 cho phép chia sẻ). **Thay thế mọi chỗ** đang lọc tạm theo `owner_id` (T1-16, T2-02, T2-05, T2-06, xóa). Thêm migration `document_acl` và endpoint chia sẻ nếu OQ-003 yêu cầu; nếu chưa, bảng để trống.
- **Xong khi:** tìm kiếm trong mã không còn chỗ nào lọc quyền theo cách khác; kiểm thử T3-07 đạt.

### T3-04 · Bản ghi kiểm toán: endpoint và màn hình S-06 · BE+FE · M
- **Phụ thuộc:** T2-05, T1-07
- **Làm gì:**
  - **BE:** `GET /admin/audit?from&to&user&document&cursor` (chỉ `security_admin`; phân trang con trỏ); tác vụ dọn bản ghi quá `AUDIT_RETENTION_DAYS`.
  - **FE:** S-06 theo `S-06-ban-ghi-kiem-toan.html`, ảnh `s06-default`, `s06-empty`, `s06-error`: bộ lọc, bảng (thời điểm, người dùng, tài liệu liên quan), trạng thái trống và lỗi (kèm "Thử lại"); không hiển thị nội dung câu hỏi.
- **Xong khi:** mỗi câu hỏi sinh đúng một bản ghi hiển thị được; bộ lọc hoạt động; vai trò khác gọi → 403 (AC-023).

### T3-05 · Hội thoại: lịch sử và câu hỏi tiếp theo · BE+FE · M
- **Phụ thuộc:** T2-05, T2-08
- **Làm gì:**
  - **BE:** đưa `HISTORY_TURNS` lượt gần nhất vào `messages` của lời gọi mô hình; truy vấn truy xuất ghép câu hỏi hiện tại với câu hỏi người dùng ở lượt trước; `GET /conversations/{id}/messages`.
  - **FE:** hiển thị chuỗi hỏi đáp; nút "Hội thoại mới". Lưu hội thoại giữa các phiên theo PQ-004; mặc định chỉ trong phiên.
- **Xong khi:** bộ đánh giá có nhóm `follow_up` (≥ 10 câu) và kết quả được báo cáo (AC-008); hội thoại mới không mang ngữ cảnh cũ.

### T3-06 · Đo thời gian, hạn thời gian chờ và trạng thái chờ · BE+FE · M
- **Phụ thuộc:** T2-05, T2-07
- **Làm gì:**
  - **BE:** span OpenTelemetry cho từng bước (nhúng câu hỏi, truy xuất, sinh); số liệu phân bố `answer_latency_seconds`; `ANSWER_TIMEOUT_S`. Endpoint SSE `POST /conversations/{id}/messages:stream` **chỉ làm nếu AQ-006 chọn hiển thị theo luồng**.
  - **FE:** chỉ báo chờ xuất hiện ≤ 300 ms sau khi gửi; nút Hủy (hủy yêu cầu phía trình duyệt, ảnh `s02-waiting`); thông báo khi quá thời gian kèm "Thử lại".
- **Xong khi:** đo được phân vị thời gian từng bước trên bộ câu hỏi chuẩn (AC-011, LG-05); kiểm thử giao diện cho chỉ báo chờ.

### T3-07 · Kiểm thử cô lập quyền · QA · M
- **Phụ thuộc:** T3-03
- **Làm gì:** `backend/tests/security/test_isolation.py`: hai người dùng A và B, mỗi người một tài liệu có chuỗi đặc trưng. Khẳng định: A hỏi nội dung của B → `not_found`; A gọi `GET /documents/{idB}`, `/pages/…`, `/file`, `DELETE`, `POST …/retry` → 404; danh sách của A không có tài liệu của B; bản ghi kiểm toán của A không liệt kê tài liệu của B. Kiểm thử tự sinh từ danh sách route để khỏi bỏ sót route mới.
- **Xong khi:** tất cả đạt (AC-020, LG-07); thêm cố ý một route không kiểm quyền thì kiểm thử đỏ.

### T3-08 · Kiểm thử E2E xóa và kiểm toán · QA · S
- **Phụ thuộc:** T3-01, T3-02, T3-04
- **Làm gì:** Playwright: xóa tài liệu có xác nhận → biến khỏi danh sách → hỏi nội dung của nó → "không tìm thấy"; quản trị bảo mật cấp/thu hồi quyền và xem bản ghi kiểm toán.
- **Xong khi:** các kịch bản đạt (AC-005, AC-014, AC-023, AC-024).

---

## SPRINT 4 — Chất lượng, đo lường, sẵn sàng phát hành

**Cổng G3 (trước Sprint 4):** OQ-002 (ngưỡng), bộ câu hỏi chuẩn đầy đủ.

### T4-01 · Hiệu chỉnh và nghiệm thu chất lượng · QA+BE · L
- **Phụ thuộc:** T2-13, T3-05; G3
- **Làm gì:**
  1. Mở rộng bộ câu hỏi chuẩn với business owner (đủ loại: `in_scope`, `out_of_scope`, `multi_doc`, `follow_up`, theo từng ngôn ngữ đã chốt).
  2. Hiệu chỉnh lần lượt: `CHUNK_TOKENS`, `CHUNK_OVERLAP`, `TOP_K`, `MAX_CHUNKS_PER_DOC`, `MIN_RELEVANCE_SCORE`, `ANSWER_EFFORT` (so `low` với `medium`), chỉ dẫn hệ thống. **Mỗi lần chỉ đổi một yếu tố**, chạy `run_eval.py`, ghi kết quả vào `docs/implement/tuning_log.md`.
  3. Chấm tay một mẫu 20% để đối chiếu với giám khảo tự động trước khi dùng kết quả tự động.
  4. Đóng băng cấu hình đạt ngưỡng; ghi cấu hình và chi phí mỗi lần chạy.
- **Xong khi:** báo cáo cuối đạt MET-002 ≥ ngưỡng, tỷ lệ bịa ≤ ngưỡng, đúng trang 100%, theo từng ngôn ngữ (AC-009, AC-010, AC-013, LG-02, LG-03, LG-04).

### T4-02 · Báo cáo mức sử dụng: endpoint và S-07 · BE+FE · M
- **Phụ thuộc:** T2-05, T1-06
- **Làm gì:**
  - **BE:** `GET /reports/usage?weeks=4` (vai trò `manager`): đếm người dùng khác nhau và số câu hỏi theo tuần từ `usage_events`; thêm tỷ lệ `helpful` khi có T4-03.
  - **FE:** S-07 theo `S-07-bao-cao-su-dung.html`, ảnh `s07-default`, `s07-empty`, `s07-error`: thẻ số liệu, biểu đồ cột có chú giải **và** bảng số liệu tương ứng (không phụ thuộc màu), trạng thái trống, lỗi.
- **Xong khi:** với dữ liệu hạt giống đã biết, số liệu đúng (AC-016, AC-021); vai trò khác → 403.

### T4-03 · Đánh giá câu trả lời · BE+FE · S
- **Phụ thuộc:** T2-08
- **Làm gì:**
  - **BE:** `PUT /messages/{id}/feedback` (`{value: helpful|not_helpful}`; chỉ chủ hội thoại; ghi đè được); phát `answer_feedback_submitted`.
  - **FE:** `FeedbackControl` (C-13) với `aria-pressed`, hai nút "Hữu ích" / "Không hữu ích".
- **Xong khi:** đánh giá được lưu, đổi lại được, và hiện trong tổng hợp ở T4-02 (AC-017).

### T4-04 · Health, giám sát và cảnh báo · OPS · M
- **Phụ thuộc:** T0-04, T3-02
- **Làm gì:** `/health/ready` kiểm cơ sở dữ liệu, kho tệp, hàng đợi và tuổi việc cũ nhất; bảng giám sát: thời gian phản hồi, tỷ lệ lỗi, tỷ lệ `not_found`, độ dài hàng đợi, thời gian nạp tài liệu, số tài liệu `deleting` quá hạn; cảnh báo theo AQ-005 và OQ-011 (chưa có thì dùng giá trị tạm trong tài liệu).
- **Xong khi:** dừng một thành phần → `/health/ready` báo lỗi và cảnh báo phát (AC-022).

### T4-05 · Hồ sơ xử lý dữ liệu và kiểm thử "log không chứa nội dung" · QA+OPS · M
- **Phụ thuộc:** T3-02, T3-04; G1 (OQ-005, OQ-006)
- **Làm gì:**
  1. Kiểm thử tự động theo `implement_plan.md` mục 9.3: chạy luồng tải lên, hỏi đáp, xóa với chuỗi đánh dấu duy nhất (`CANARY-…`) trong tài liệu và câu hỏi; thu toàn bộ log, sự kiện phân tích, bản ghi kiểm toán, `usage_events`; khẳng định chuỗi không xuất hiện.
  2. Viết `docs/implement/data_handling.md`: dữ liệu nào đi đâu (đặc biệt phần gửi tới dịch vụ AI ở Kịch bản A), nơi lưu, mã hóa, thời gian lưu, quy trình xóa, sao lưu.
  3. Trình bộ phận bảo mật rà soát.
- **Xong khi:** kiểm thử canary đạt; có xác nhận bằng văn bản của bộ phận bảo mật (AC-015, LG-06).

### T4-06 · Kiểm tra cổng launch · QA · M
- **Phụ thuộc:** T4-01..T4-05
- **Làm gì:** chạy từng mục LG-01..LG-11 (`PRD.md` mục 5.1) và ghi kết quả, bằng chứng (đường dẫn báo cáo, ảnh chụp) vào `docs/implement/launch_checklist.md`. Chạy toàn bộ E2E, kiểm thử bảo mật, bộ đánh giá, kiểm tra axe trên mọi màn hình S-01..S-07, kiểm tra các ảnh màn hình chuẩn trong `html_design/screenshots/` so với giao diện thật.
- **Xong khi:** mỗi mục LG có trạng thái Đạt/Không đạt kèm bằng chứng; mục không đạt có người chịu trách nhiệm và hạn.

### T4-07 · Tài liệu vận hành · OPS · S
- **Phụ thuộc:** T4-04
- **Làm gì:** `docs/implement/ops_runbook.md`: triển khai và quay lui, migration, biến cấu hình (nguồn quyết định), xử lý việc `failed`, xử lý tài liệu `deleting` quá hạn, sao lưu và khôi phục (AQ-003), xoay khóa API, xử lý sự cố lộ dữ liệu.
- **Xong khi:** một người ngoài đội làm theo runbook triển khai được lên môi trường kiểm thử.

### T4-08 · Rà soát khả năng tiếp cận toàn bộ · QA · S
- **Phụ thuộc:** T4-02, T4-03
- **Làm gì:** axe tự động cho S-01..S-07 và mọi trạng thái; kiểm tra thủ công: chỉ dùng bàn phím, trình đọc màn hình, tương phản, thu phóng 200%.
- **Xong khi:** không còn vi phạm mức nghiêm trọng hoặc cao; danh sách vi phạm nhỏ còn lại có chủ và hạn.

**Cổng G4 (cuối Sprint 4):** tiêu chí launch LG-01..LG-11 đạt, hoặc có quyết định ngoại lệ bằng văn bản của sponsor.

---

## Định nghĩa hoàn thành chung (áp dụng cho mọi task)

1. Mọi điều kiện "Xong khi" của task đạt; mọi AC liên quan trong `UserStories.md` có kiểm thử tự động.
2. Giao diện khớp bố cục và trạng thái ảnh màn hình tương ứng (`docs/design/html_design/screenshots/`).
3. Dùng được bằng bàn phím, có nhãn cho trình đọc màn hình, đạt axe không lỗi nghiêm trọng.
4. Không có ngưỡng nào viết cứng trong mã; đọc từ `Settings` (`implement_plan.md` mục 10.3).
5. Log và sự kiện phân tích không chứa nội dung tài liệu hay câu hỏi.
6. Sự kiện phân tích (`PRD.md` 5.2) của story được phát (`implement_plan.md` mục 12).
7. Mã được rà soát bởi ít nhất một người khác; CI xanh (lint, kiểu, import-linter, kiểm thử).
8. OpenAPI và tài liệu liên quan cập nhật.

## Bảng truy vết task ↔ story

| Story | Task |
|---|---|
| US-017 | T1-01..T1-08 |
| US-001 | T1-09..T1-15, T1-17, T1-18, T1-20, T1-21 |
| US-002 | T1-11, T1-17, T1-20 |
| US-003 | T1-11, T1-13, T1-15..T1-18, T1-20 |
| US-004 | T1-13, T1-19, T1-20 |
| US-005 | T1-16, T1-18, T1-20 |
| US-008 | T2-01..T2-05, T2-07, T2-10, T2-12..T2-14 |
| US-009 | T2-02, T2-04, T2-13 |
| US-011 | T2-04, T2-08, T2-12, T2-13 |
| US-012 | T0-07, T2-13, T4-01 |
| US-014 | T2-04, T2-05, T2-08, T2-11 |
| US-015 | T2-06, T2-09, T2-12 |
| US-006 | T3-01 |
| US-007 | T3-01, T3-02, T3-08 |
| US-010 | T3-05 |
| US-013 | T3-06 |
| US-018 | T3-03, T3-07 |
| US-020 | T3-04, T3-08 |
| US-016 | T0-09, T2-13, T4-01 |
| US-019 | T4-05 |
| US-021 | T4-04 |
| US-022, US-023 | T4-02 |
| US-024 | T4-03 |

Nền tảng chung: T0-01..T0-10. Nghiệm thu cuối: T4-06, T4-07, T4-08.

**Độ phủ:** cả 24 story đều có ít nhất một task; không có task mồ côi (mỗi task nêu story hoặc là nền tảng/nghiệm thu).
