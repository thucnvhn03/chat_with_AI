# INT-API-005 — Phiên hết hạn

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Phiên không hoạt động quá `SESSION_IDLE_HOURS` trả 401 `session_expired`; không có cookie trả `unauthenticated` |
| Truy vết | BR-014, US-017, T1-04 |
| Ưu tiên / Loại | Cao / Âm |
| Tự động hóa | `test_auth.py::test_expired_session_is_session_expired`, `test_no_session_is_401` |

**Các bước**
1. Đăng nhập "an".
2. Đặt `sessions.last_seen_at` lùi về quá `SESSION_IDLE_HOURS` + 1 giờ.
3. `GET /auth/me`.
4. Với client không có cookie: `GET /documents`.

**Kết quả mong đợi**
- Bước 3: 401, `error.code = "session_expired"`.
- Bước 4: 401, `error.code = "unauthenticated"`.
