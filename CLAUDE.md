# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Tổng quan

Kho này có hai phần:

1. **Bộ prompt và checklist AI-SDLC** (`requirements/`, `analysis/`, `design/`, `verification/`, `AI_SDLC-SOP.md`) — mẫu prompt theo IEEE 29148 / 1016 / 829 và UML 2.0, kèm checklist `.xlsx`.
2. **MVP "Chat với tài liệu"** — hỏi đáp có trích nguồn (tên tệp, số trang) trên PDF người dùng tải lên. Tài liệu của MVP nằm trong `docs/`: yêu cầu (`docs/requirements/` — BRD, PRD, SADD, UserStories), kế hoạch (`docs/implement/implement_plan.md`, một tệp mỗi task trong `docs/implement/tasks/`), kiểm thử (`docs/testing/` — Master Test Plan, 149 ca trong `test_cases/`, kết quả từng lần chạy trong `results/run-<ngày>/`).

Mã, chú thích, thông báo lỗi, tên kiểm thử và tài liệu đều viết bằng **tiếng Việt**; giữ nguyên quy ước này. Chú thích thường dẫn chiếu mã yêu cầu/quyết định (US-xxx, AC-xxx, BR-xxx, ADR-xxx, OQ-/AQ-/PQ-xxx, T<n>-<nn>) — giữ và bổ sung các dẫn chiếu đó khi sửa mã.

## Lệnh thường dùng

### Chạy ứng dụng (Docker Compose)

```bash
docker compose -f deploy/docker-compose.yml up -d --build --wait
docker compose -f deploy/docker-compose.yml exec backend python -m app.cli create-admin admin
docker compose -f deploy/docker-compose.yml exec backend python -m app.cli create-user an.nguyen bd
# giao diện: http://localhost:5173, API: http://localhost:8000/api/v1 (docs: /api/v1/docs)
```

Mặc định lấy từ `deploy/env.example`; ghi đè/bí mật đặt trong `deploy/.env` (git-ignored). Không có `ANTHROPIC_API_KEY` thì dùng `ANSWER_PROVIDER=fake`. Lần đầu tải mô hình embedding `BAAI/bge-m3` (~2.3 GB, dịch vụ `model-download`).

### Backend (`backend/`, Python 3.12)

Trong Docker (cần `docker compose -f deploy/docker-compose.yml up -d postgres objectstore`):

```bash
scripts/backend-docker.sh                                  # ruff + ruff format --check + mypy + lint-imports + toàn bộ pytest
scripts/backend-docker.sh pytest tests/unit -q
scripts/backend-docker.sh pytest tests/unit/test_chunking.py::test_ten_ham -q   # một test
```

Không dùng Docker (từ `backend/`): `pip install -e ".[dev]"`, rồi `ruff check app tests alembic`, `ruff format --check app tests alembic`, `mypy` (strict), `lint-imports`, `pytest`. Kiểm thử tích hợp/bảo mật dùng PostgreSQL pgvector + S3 thật: qua `TEST_DATABASE_URL` / `TEST_S3_ENDPOINT_URL` (mỗi phiên tạo DB và bucket riêng) hoặc tự khởi động bằng testcontainers. Marker: `integration`, `needs_api_key` (chỉ chạy khi có `ANTHROPIC_API_KEY`).

Migration: Alembic trong `backend/alembic/versions/` (đánh số `000N_*.py`); CI kiểm tra lên/xuống bằng `pytest tests/integration/test_migrations.py -k roundtrip`.

### Frontend (`frontend/`, React 18 + TS + Vite)

```bash
npm ci && npm run lint && npm run typecheck && npm test   # Vitest + jsdom
npx vitest run src/features/chat/chat.test.tsx           # một tệp
npx vitest run -t "tên test"                             # theo tên
npm run build
```

**Sau khi đổi API backend** phải sinh lại kiểu (CI job `openapi-types` thất bại nếu `frontend/src/api` lệch):

```bash
cd backend && python scripts/export_openapi.py ../frontend/src/api/openapi.json
cd frontend && npm run gen:api
```

### E2E (`e2e/`, Playwright + axe)

```bash
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.e2e.yml up -d --build --wait
cd e2e && npm ci && npx playwright install chromium && npx playwright test
npx playwright test tests/qa.spec.ts      # một spec
```

Override E2E dùng AI giả, embedding `hash`, và tạo sẵn tài khoản `e2e.bd`, `e2e.bd2`, `e2e.empty`, `e2e.admin`, `e2e.manager`, `e2e.revoke` (mật khẩu `e2e-mat-khau-123`). Chạy tuần tự (`workers: 1`).

### Bộ đánh giá (`evaluation/`)

```bash
python evaluation/run_eval.py --dataset evaluation/datasets/sample.jsonl --fake
cd evaluation && pytest -q && ruff check . && ruff format --check .
```

Chạy với hệ thống thật và định dạng dataset: xem `evaluation/README.md`. Báo cáo lưu ở `evaluation/reports/`.

### MCP server (`mcp/`, Node 20+, stdio)

`npm run build`, `npm run typecheck`, `npm test` (unit, backend giả), `npm run test:integration` (cần stack đang chạy). Cấu hình qua `CWD_API_URL`, `CWD_ORIGIN`, `CWD_LOGIN`, `CWD_PASSWORD`. stdout dành cho giao thức MCP — chỉ log ra stderr.

### Skill dự án

- `/test-run` — chạy tuần tự mọi lớp kiểm thử (an toàn cho máy ít RAM) và lập hồ sơ kết quả trong `docs/testing/results/run-<ngày>/`.
- `/test-report` — lập báo cáo tổng kết IEEE 829 (`docs/testing/Test_Summary_Report.md`) từ kết quả đã có, đối chiếu tiêu chí LG-01..LG-11.

## Kiến trúc

### Backend: ports & adapters

- `app/ports/` — giao diện trừu tượng: `ai.py` (`EmbeddingProvider`, `AnswerGenerator`), `storage.py` (`FileStore`), `identity.py`.
- `app/adapters/` — cài đặt cụ thể: Claude (`claude_llm.py`), giả (`fake_llm.py`), embedding cục bộ sentence-transformers / `hash` tất định, S3, đăng nhập local/OIDC.
- `app/container.py` — **gốc lắp ghép duy nhất**: chọn adapter theo `Settings` và dựng `Runtime`. Chỉ `main.py`, worker và CLI được import tệp này.
- `app/runtime.py` — dataclass `Runtime` chỉ tham chiếu kiểu port; API và mô-đun nghiệp vụ nhận `Runtime` mà không biết adapter nào đang chạy.
- **import-linter** (`backend/.importlinter`) cấm `app.modules` và `app.api` import `app.adapters`. Muốn thêm khả năng ngoài → thêm port, cài adapter, nối ở `container.py`.
- `app/main.py` — `create_app(runtime_factory)`; kiểm thử truyền runtime với adapter giả (xem `tests/conftest.py`, đặt `EMBEDDING_PROVIDER=hash`, `ANSWER_PROVIDER=fake` trước khi import app).
- `app/config.py` — mọi ngưỡng (kể cả các giá trị còn `[TBD]` trong BRD/PRD) là trường của `Settings`, đọc từ biến môi trường. **Không viết cứng ngưỡng ở nơi khác.**

### Luồng dữ liệu

1. **Tải lên** (`api/documents.py` → `modules/documents`): lưu PDF vào S3 và `enqueue` việc `ingest` **trong cùng giao dịch** với bản ghi tài liệu.
2. **Hàng đợi** là bảng `jobs` trong PostgreSQL (`modules/jobs/queue.py`), lấy việc bằng `FOR UPDATE SKIP LOCKED`. Worker (`python -m app.worker.run`) đăng ký handler theo `kind` (`ingest`, `purge`), thử lại với giãn cách tới `JOB_MAX_ATTEMPTS`, rồi gọi `on_give_up`. Worker cũng chạy việc bảo trì định kỳ (`worker/maintenance.py`: dọn hội thoại/kiểm toán quá hạn, cảnh báo tài liệu `deleting` quá SLA).
3. **Ingestion** (`modules/ingestion/`): `extract` (pypdf) → `chunking` → embedding → lưu `chunks` với vector pgvector (HNSW).
4. **Hỏi đáp** (`modules/qa/service.py`): retrieval (`modules/retrieval/search.py`, lọc theo quyền truy cập ở `modules/access/scope.py`) → sinh câu trả lời. Có **ba lớp từ chối**, đều trả câu cố định `NOT_FOUND_SENTENCE`: (1) không có chunk hoặc điểm < `MIN_RELEVANCE_SCORE` → không gọi mô hình; (2) mô hình trả đúng câu từ chối; (3) câu trả lời không có citation hợp lệ. Mô-đun QA không đọc kho tệp, chỉ dùng chunk đã truy xuất.
5. **Xóa** tài liệu: chuyển `deleting` + việc `purge` (`modules/documents/purge.py`) xóa tệp, chunk, trong SLA `PURGE_SLA_HOURS`.

Các mô-đun khác: `access` (vai trò `bd`, `manager`, `security_admin`; cấp/thu hồi quyền; ACL tài liệu), `audit` (bản ghi kiểm toán), `usage` (sự kiện sử dụng, báo cáo S-07), `conversation`. Quan sát: `observability/` (structlog, Prometheus `/metrics`, OpenTelemetry, `/health`). Có kiểm thử bảo mật bảo đảm **không ghi nội dung tài liệu/câu hỏi vào log** (`tests/security/test_no_content_in_logs.py`) và ma trận phân quyền tự liệt kê mọi route (`tests/security/routes.py`) — route mới mặc định phải yêu cầu phiên; route công khai phải thêm vào `PUBLIC_PATHS` kèm lý do.

### Frontend

Tổ chức theo tính năng trong `src/features/` (auth, chat, documents, sources, admin, reports) tương ứng màn hình S-01..S-07 (thiết kế HTML tham chiếu ở `docs/design/html_design/`). Gọi API qua `src/api/client.ts` với kiểu sinh từ OpenAPI (`schema.d.ts` — không sửa tay); tải lên dùng XHR (`src/api/upload.ts`) để có tiến độ. Trạng thái server dùng TanStack Query. Vite proxy `/api` tới backend (`VITE_API_PROXY_TARGET`). Kiểm thử component chạy cả kiểm tra axe.

### Triển khai

`deploy/docker-compose.yml`: `postgres` (pgvector), `objectstore` (S3 tương thích), `migrate`, `model-download`, `backend`, `worker`, `frontend`, `prometheus` (profile monitoring; luật cảnh báo trong `deploy/monitoring/alerts.yml`, kiểm thử bằng promtool với `alerts_test.yml`). Vận hành: `docs/implement/ops_runbook.md`.
