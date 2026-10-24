# T1-02 · Cổng xác thực và adapter tài khoản nội bộ

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 1 — Truy cập và nạp tài liệu |
| Story | US-017 — Chỉ người được cấp quyền mới dùng được ứng dụng (P0) |
| Loại việc | BE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T1-01 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** `ports/identity.py` (`IdentityProvider`); `adapters/local_identity.py`: băm Argon2id, kiểm tra mật khẩu, giới hạn đăng nhập sai `[Đề xuất: 5 lần / 15 phút]` theo tài khoản và địa chỉ; so sánh thời gian không đổi.
- **Sản phẩm:** `ports/identity.py`, `adapters/local_identity.py`, kiểm thử đơn vị.
- **Xong khi:** kiểm thử: đúng mật khẩu → thành công; sai → thất bại; quá giới hạn → bị khóa tạm; thông báo lỗi không phân biệt "sai tên" với "sai mật khẩu".

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** không có

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
