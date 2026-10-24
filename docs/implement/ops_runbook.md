# Tài liệu vận hành — "Chat với tài liệu" (MVP)

| Mục | Nội dung |
|---|---|
| Task | T4-07 (kèm phần sao lưu của T3-02) |
| Phiên bản | 0.1 (Draft) — 2026-10-23 |
| Đối tượng | Đội vận hành / DevOps, người trực sự cố |

## 1. Thành phần

| Dịch vụ | Ảnh | Vai trò |
|---|---|---|
| `postgres` | `pgvector/pgvector:pg16` (pgvector ≥ 0.8) | Siêu dữ liệu, chunk + vector, hàng đợi việc, kiểm toán |
| `objectstore` | S3 (cục bộ: `rustfs/rustfs:1.0.3`) | Tệp PDF gốc |
| `migrate` | `deploy/Dockerfile.backend` | `alembic upgrade head`, chạy một lần trước backend/worker |
| `backend` | `deploy/Dockerfile.backend` | API FastAPI (uvicorn, cổng 8000), `/health/*`, `/metrics` |
| `worker` | `deploy/Dockerfile.backend` | `python -m app.worker.run`: nạp, xóa vĩnh viễn, việc định kỳ; số liệu ở cổng 9100 |
| `frontend` | `deploy/Dockerfile.frontend.prod` (nginx) | Giao diện tĩnh, chuyển tiếp `/api`, CSP |
| `prometheus` (tùy chọn) | `prom/prometheus` | Profile `monitoring`, luật ở `deploy/monitoring/alerts.yml` |

## 2. Triển khai lên môi trường kiểm thử

1. Chuẩn bị máy có Docker ≥ 24 và Docker Compose v2. Không cần Python/Node trên máy.
2. Lấy mã nguồn đúng phiên bản (tag) cần triển khai.
3. Tạo `deploy/.env` (không commit) — ghi đè `deploy/env.example`:
   ```
   POSTGRES_PASSWORD=<bí mật>
   S3_ACCESS_KEY=<bí mật>
   S3_SECRET_KEY=<bí mật>
   DATABASE_URL=postgresql+psycopg://chat:<bí mật>@postgres:5432/chat
   ANSWER_PROVIDER=claude            # hoặc fake khi chưa được phép gửi dữ liệu ra ngoài (OQ-006)
   ANTHROPIC_API_KEY=<từ kho bí mật>
   ALLOWED_ORIGINS=["https://<tên-miền>"]
   ENVIRONMENT=staging
   ```
   Cổng bị trùng: đặt `POSTGRES_PORT`, `BACKEND_PORT`, `FRONTEND_PORT`… trong cùng tệp.
4. Khởi động: `docker compose -f deploy/docker-compose.yml up -d --build --wait`
   - Lần đầu với `EMBEDDING_PROVIDER=local`, backend và worker tải mô hình `BAAI/bge-m3` (~2,3 GB) vào volume `model_cache`; healthcheck cho phép 10 phút.
5. Tạo tài khoản quản trị bảo mật đầu tiên:
   `docker compose -f deploy/docker-compose.yml exec backend python -m app.cli create-admin <login>` (nhập mật khẩu ≥ 12 ký tự).
6. Kiểm tra: `curl -f http://localhost:8000/health/ready` trả 200 với `database`, `storage`, `queue` đều `ok`; mở giao diện, đăng nhập bằng tài khoản vừa tạo, cấp quyền cho người dùng ở S-05.

## 3. Phát hành phiên bản mới và quay lui

1. Đọc danh sách migration mới (`backend/alembic/versions`). Migration chạy **trước** khi khởi động phiên bản mới (dịch vụ `migrate`).
2. Sao lưu cơ sở dữ liệu (mục 6) trước mọi migration.
3. `docker compose ... up -d --build --wait`; theo dõi `/health/ready`, cảnh báo `HighErrorRate` trong 30 phút.
4. **Quay lui mã:** triển khai lại tag trước đó. **Quay lui lược đồ** (chỉ khi migration mới gây lỗi và chưa có dữ liệu mới phụ thuộc): `docker compose ... run --rm migrate alembic downgrade -1`. Migration `0003` tạo cột vector theo `EMBEDDING_DIM`: đổi mô hình embedding khác số chiều cần migration mới **và nạp lại toàn bộ tài liệu** (thử lại từng tài liệu).
5. Production: triển khai thủ công có phê duyệt (implement_plan.md mục 10.4).

## 4. Biến cấu hình và nguồn quyết định

Mọi ngưỡng đọc từ biến môi trường (`backend/app/config.py`, danh sách đầy đủ ở `deploy/env.example`). Giá trị hiện tại là **tạm thời**; trước launch mỗi biến có nguồn quyết định phải được chốt và ghi lại ở bảng này.

| Biến | Giá trị tạm | Nguồn quyết định | Đã chốt? |
|---|---|---|---|
| `MAX_FILE_BYTES` / `MAX_DOCS_PER_USER` | 20 MB / 50 | OQ-004 | Chưa |
| `MAX_QUESTION_CHARS` | 2000 | PQ-002 | Chưa |
| `CHUNK_TOKENS` / `CHUNK_OVERLAP` | 500 / 80 | Bộ đánh giá (T4-01) | Chưa |
| `TOP_K` / `MAX_CHUNKS_PER_DOC` | 8 / 4 | Bộ đánh giá | Chưa |
| `MIN_RELEVANCE_SCORE` | 0,35 | AQ-002, bộ đánh giá | Chưa |
| `ANSWER_MODEL` / `ANSWER_EFFORT` | `claude-opus-5-5` / `medium` | G1, bộ đánh giá | Chưa |
| `ANSWER_TIMEOUT_S` | 60 | OQ-002 | Chưa |
| `HISTORY_TURNS` | 4 | Bộ đánh giá | Chưa |
| `MESSAGE_RETENTION_DAYS` | 60 | PQ-004 | Chưa |
| `EMBEDDING_MODEL` / `EMBEDDING_DIM` | `BAAI/bge-m3` / 1024 | Spike T0-07, G0 | Đề xuất |
| `SESSION_IDLE_HOURS` | 8 | DQ-003 | Chưa |
| `PURGE_SLA_HOURS` / `AUDIT_RETENTION_DAYS` | 24 / 365 | OQ-012 | Chưa |
| `JOB_MAX_ATTEMPTS` / `WORKER_CONCURRENCY` | 3 / 2 | Vận hành | — |
| `AUTH_MODE` | `local` | DQ-003 | Chưa |
| `S3_SERVER_SIDE_ENCRYPTION` | (tắt) | OQ-005 | Chưa |

## 5. Xử lý sự cố thường gặp

### Sự cố dịch vụ không phản hồi
Cảnh báo `BackendDown`, `WorkerDown`, `ComponentUnavailable`.
1. `docker compose ps`; `docker compose logs --tail 200 backend worker`.
2. `curl http://localhost:8000/health/ready` cho biết thành phần lỗi (`database`, `storage`, `queue`).
3. Cơ sở dữ liệu/kho tệp dừng → khởi động lại dịch vụ đó; backend/worker tự kết nối lại (`pool_pre_ping`, vòng lặp worker chờ rồi thử lại).

### Hàng đợi tồn đọng
Cảnh báo `QueueBacklog` (`jobs_oldest_queued_age_seconds`).
- Worker có chạy không? Tăng `WORKER_CONCURRENCY` hoặc chạy thêm bản sao worker (lấy việc bằng `SKIP LOCKED`, chạy song song an toàn).
- Việc bị kẹt ở `running` do worker chết giữa chừng:
  ```sql
  SELECT id, kind, attempts, run_after FROM jobs WHERE status = 'running';
  -- Sau khi chắc chắn không còn worker nào xử lý việc đó:
  UPDATE jobs SET status = 'queued', run_after = now() WHERE id = <id>;
  ```

### Việc failed
Cảnh báo `IngestFailures`. `SELECT id, kind, payload, attempts, last_error FROM jobs WHERE status = 'failed' ORDER BY id DESC LIMIT 50;`
- `ingest` thất bại hẳn → tài liệu đã ở `failed/internal`; người dùng bấm "Thử lại" sau khi xử lý nguyên nhân.
- `purge` thất bại hẳn → **ưu tiên cao** (cam kết xóa): sửa nguyên nhân (thường là kho tệp), rồi `UPDATE jobs SET status='queued', attempts=0, run_after=now() WHERE id=<id>;`.

### Tài liệu deleting quá hạn
Cảnh báo `DocumentsDeletingOverdue` (quá `PURGE_SLA_HOURS`).
```sql
SELECT d.id, d.deleted_at, j.status, j.attempts, j.last_error
FROM documents d LEFT JOIN jobs j ON j.kind = 'purge' AND j.payload->>'document_id' = d.id::text
WHERE d.status = 'deleting' AND d.deleted_at < now() - interval '24 hours';
```
Không có việc `purge` → thêm lại: `INSERT INTO jobs(kind, payload) VALUES ('purge', jsonb_build_object('document_id', '<id>'));`. Tài liệu `deleting` không bao giờ được truy xuất, nên không có rủi ro trả lời từ tài liệu đã xóa trong lúc chờ.

### Tỷ lệ lỗi cao
Cảnh báo `HighErrorRate`. Lỗi 502 `answer_unavailable` thường do dịch vụ AI (hạn mức, sự cố nhà cung cấp): xem log `answer_rate_limited`, `answer_api_error` (kèm `request_id` của Anthropic). Lỗi 500: log `unhandled_error` có `error_type`, `path`, `request_id`.

### Thời gian trả lời cao
Cảnh báo `AnswerLatencyHigh`. Số liệu `qa_step_seconds{step}` cho biết bước chậm (`embed`, `retrieve`, `generate`). `retrieve` chậm khi kho lớn: kiểm tra chỉ mục HNSW, `HNSW_EF_SEARCH`. `generate` chậm: cân nhắc `ANSWER_EFFORT=low` (đo lại bằng bộ đánh giá).

### Tỷ lệ "không tìm thấy" cao
Cảnh báo `NotFoundRateHigh`. Kiểm tra tài liệu có `ready` không, `MIN_RELEVANCE_SCORE` có quá cao không (đo bằng bộ đánh giá trước khi đổi).

## 6. Sao lưu và khôi phục (AQ-003 — rủi ro mở)

- **Cơ sở dữ liệu:** `pg_dump -Fc` hằng ngày [Đề xuất], giữ N ngày [Đề xuất: 30, chờ AQ-003]. Kiểm tra khôi phục hằng tháng.
- **Kho tệp:** bật versioning/sao chép của kho S3 theo hạ tầng tổ chức, cùng thời gian giữ.
- **Dữ liệu đã xóa trong bản sao lưu:** tài liệu đã xóa vĩnh viễn vẫn còn trong bản sao lưu cho tới khi bản sao lưu hết hạn. Đây là rủi ro đang mở, phải được AQ-003 chấp thuận hoặc thay đổi trước launch.
- **Khi khôi phục từ bản sao lưu** (bắt buộc làm, để không "hồi sinh" tài liệu đã xóa):
  1. Trước khi khôi phục, xuất danh sách tài liệu đã xóa từ cơ sở dữ liệu hiện hành: `COPY (SELECT id FROM documents WHERE status IN ('deleting','deleted')) TO STDOUT;`
  2. Khôi phục.
  3. Với mỗi id trong danh sách: `UPDATE documents SET status='deleting', deleted_at=coalesce(deleted_at, now()) WHERE id=<id> AND status NOT IN ('deleted');` rồi thêm việc `purge` (mục 5). Worker sẽ xóa chunk, đoạn trích và tệp.

## 7. Xoay khóa API

1. Tạo khóa mới trên Claude Console (tài khoản của tổ chức).
2. Cập nhật kho bí mật / `deploy/.env` (`ANTHROPIC_API_KEY`), khởi động lại `backend` (worker không gọi dịch vụ AI).
3. Kiểm tra một câu hỏi thử thành công, rồi vô hiệu khóa cũ.
4. Khóa bị lộ: vô hiệu ngay (bước 3 trước), ghi nhận sự cố theo mục 8.

## 8. Sự cố lộ dữ liệu

1. **Khoanh vùng:** thu hồi quyền tài khoản liên quan ở S-05 (phiên bị xóa ngay); nếu nghi lộ khóa: xoay khóa API, mật khẩu cơ sở dữ liệu/kho tệp.
2. **Vô hiệu mọi phiên** nếu cần: `DELETE FROM sessions;` (mọi người phải đăng nhập lại).
3. **Xác định phạm vi:** `audit_records` cho biết ai đã hỏi trên tài liệu nào, khi nào (S-06 hoặc SQL theo `user_id`, `document_ids`, khoảng thời gian). Log không chứa nội dung tài liệu/câu hỏi.
4. **Thông báo** theo quy định của tổ chức (OQ-005) và cho chủ sản phẩm.
5. Xóa tài liệu bị lộ nếu cần (quản trị bảo mật có quyền xóa mọi tài liệu qua `DELETE /api/v1/documents/{id}`).
6. Lập biên bản sự cố.

## 9. Giám sát

- Bật cục bộ: `docker compose -f deploy/docker-compose.yml --profile monitoring up -d` → Prometheus ở `http://localhost:9090`.
- Luật cảnh báo: `deploy/monitoring/alerts.yml`; kiểm thử luật: `docker run --rm -v "$PWD/deploy/monitoring:/m" --entrypoint promtool prom/prometheus:v3.1.0 test rules /m/alerts_test.yml`.
- Nơi nhận cảnh báo (Alertmanager, kênh trực): **[TBD: AQ-005, OQ-011]**.
- Bảng giám sát cần có: thời gian phản hồi (`answer_latency_seconds`), tỷ lệ lỗi (`http_requests_total`), tỷ lệ `not_found` (`answers_total`), độ dài hàng đợi (`jobs_queued`), thời gian nạp (`ingest_duration_seconds`), tài liệu `deleting` quá hạn (`documents_deleting_overdue`), tình trạng thành phần (`component_up`).
