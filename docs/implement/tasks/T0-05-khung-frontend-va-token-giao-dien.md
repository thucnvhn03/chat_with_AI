# T0-05 · Khung frontend và token giao diện

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 0 — Nền tảng và spike |
| Story | Nền tảng / nghiệm thu (không gắn riêng một story) |
| Loại việc | FE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T0-01 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:**
  1. Chuyển biến màu, kiểu chữ, khoảng cách từ `docs/design/html_design/styles.css` thành token (CSS variables) ở `frontend/src/styles/`.
  2. AppShell (C-00): header, vùng nội dung, vùng thông báo; router với các tuyến `/login`, `/`, `/admin/access`, `/admin/audit`, `/reports`.
  3. Thành phần dùng chung: `ErrorBanner` (C-16), `EmptyState` (C-10), `StatusBadge` (C-06) — mỗi cái có story/test dựng (Testing Library).
  4. Liên kết "bỏ qua tới nội dung chính" và `:focus-visible` như giao diện mẫu.
  5. Client API: sinh kiểu TypeScript từ OpenAPI của backend (`openapi-typescript`); bọc `fetch` có xử lý 401 → điều hướng `/login`.
- **Sản phẩm:** `frontend/src/app/*`, `components/*`, `styles/*`, `api/client.ts`.
- **Xong khi:** `npm run dev` hiển thị shell; ba thành phần dùng chung có kiểm thử đơn vị; kiểm tra axe không báo lỗi trên shell.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G0 (cuối Sprint 0): chốt bộ công nghệ, DQ-003, kết quả ba spike.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
