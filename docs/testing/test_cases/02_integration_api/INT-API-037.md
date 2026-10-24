# INT-API-037 — Đăng nhập OIDC

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Luồng Authorization Code + PKCE: người có quyền được tạo phiên; người không quyền nhận `no_access`; state sai bị từ chối; đăng nhập nội bộ tắt khi dùng OIDC |
| Truy vết | BR-014, US-017, DQ-003, T1-03 |
| Ưu tiên / Loại | Cao / Dương, âm |
| Điều kiện trước | `AUTH_MODE = oidc`; IdP giả trả email "an.oidc@example.test" |
| Tự động hóa | `test_oidc_flow.py` (4 kiểm thử) |

**Các bước**
1. Cấp quyền `bd` cho "an.oidc@example.test"; `GET /auth/oidc/login` → lấy `state`; `GET /auth/oidc/callback?code=abc&state=…`; `GET /auth/me`.
2. Người chưa có quyền: lặp lại luồng.
3. Callback với `state=gia-mao`.
4. `POST /auth/login`.

**Kết quả mong đợi**
- Bước 1: 302 → `/`; SHA-256 của `code_verifier` khớp `code_challenge`; `/auth/me` trả `bd`.
- Bước 2: 302 → `/login?error=no_access`; `/auth/me` 401; người dùng được tạo theo email.
- Bước 3: 400. Bước 4: 404.
