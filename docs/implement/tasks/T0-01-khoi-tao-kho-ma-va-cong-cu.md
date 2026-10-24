# T0-01 · Khởi tạo kho mã và công cụ

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 0 — Nền tảng và spike |
| Story | Nền tảng / nghiệm thu (không gắn riêng một story) |
| Loại việc | OPS |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | — |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:**
  1. Tạo monorepo theo cấu trúc ở `implement_plan.md` mục 2: `backend/`, `frontend/`, `evaluation/`, `e2e/`, `deploy/`.
  2. Backend: `pyproject.toml` (Python 3.12), phụ thuộc FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, structlog; công cụ ruff, mypy, pytest, import-linter.
  3. Frontend: Vite + React 18 + TypeScript; eslint, Vitest, Testing Library.
  4. Cấu hình `import-linter` với hai hợp đồng: `modules` không import `adapters`; `api` không import trực tiếp `adapters`.
  5. Tệp `README.md` gốc: cách chạy cục bộ, cách chạy kiểm thử.
- **Sản phẩm:** cây thư mục, `pyproject.toml`, `package.json`, `.importlinter`, `README.md`.
- **Xong khi:** `pytest` (với một kiểm thử mẫu), `ruff`, `mypy`, `import-linter`, `npm test`, `npm run lint` đều chạy xanh trên máy sạch theo README.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G0 (cuối Sprint 0): chốt bộ công nghệ, DQ-003, kết quả ba spike.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
