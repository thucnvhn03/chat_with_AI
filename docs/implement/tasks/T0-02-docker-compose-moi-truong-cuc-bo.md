# T0-02 · Docker Compose môi trường cục bộ

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 0 — Nền tảng và spike |
| Story | Nền tảng / nghiệm thu (không gắn riêng một story) |
| Loại việc | OPS |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T0-01 |
| Trạng thái | Review (compose khởi động đủ dịch vụ, /health/live 200, frontend mở được — kiểm với cấu hình E2E; lần đầu với bge-m3 cần ~3 GB đĩa trống) |

- **Làm gì:** `deploy/docker-compose.yml` với `postgres` (ảnh có `pgvector`), `minio`, `backend` (uvicorn), `worker` (`python -m app.worker.run`), `frontend` (Vite, proxy `/api` → backend). Tệp `deploy/env.example` liệt kê mọi biến ở `implement_plan.md` mục 10.3. Volume dùng chung cho mô hình embedding.
- **Sản phẩm:** `deploy/docker-compose.yml`, `deploy/env.example`, `deploy/Dockerfile.backend`, `deploy/Dockerfile.frontend`.
- **Xong khi:** `docker compose up` trên máy sạch khởi động đủ dịch vụ; `GET http://localhost:8000/health/live` trả 200; trang frontend rỗng mở được.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G0 (cuối Sprint 0): chốt bộ công nghệ, DQ-003, kết quả ba spike.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
