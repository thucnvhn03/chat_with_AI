# T0-04 · Khung backend: cấu hình, log, lỗi, health

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 0 — Nền tảng và spike |
| Story | Nền tảng / nghiệm thu (không gắn riêng một story) |
| Loại việc | BE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T0-01 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:**
  1. `app/config.py`: lớp `Settings` (Pydantic) đọc môi trường; **mọi ngưỡng** ở `implement_plan.md` mục 10.3 là trường có giá trị mặc định tạm thời.
  2. `app/main.py`: khởi tạo FastAPI, đăng ký router rỗng, middleware ID yêu cầu.
  3. `app/api/errors.py`: định dạng lỗi `{"error": {"code", "message"}}`, bộ xử lý ngoại lệ chung (mục 4 của plan). Thông báo lỗi không chứa chi tiết kỹ thuật.
  4. `app/observability/`: log JSON bằng structlog **kèm bộ lọc che nội dung** (xóa trường `question`, `content`, `text`, `body` khỏi log), số liệu Prometheus, `/health/live` và `/health/ready` (kiểm cơ sở dữ liệu).
  5. Middleware không ghi thân yêu cầu cho `POST /documents` và `POST /conversations/*/messages`.
- **Sản phẩm:** `config.py`, `main.py`, `api/errors.py`, `observability/*`.
- **Xong khi:** kiểm thử đơn vị chứng minh (a) lỗi chưa xử lý trả đúng định dạng và không lộ stack trace; (b) log của một yêu cầu có trường `question` không chứa giá trị đó.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G0 (cuối Sprint 0): chốt bộ công nghệ, DQ-003, kết quả ba spike.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
