# Xử lý sự cố khi chạy kiểm thử

Các tình huống đã gặp trên máy phát triển (Windows 10, Git Bash, Docker Desktop 2 CPU / 3,8 GB).

| Triệu chứng | Nguyên nhân | Cách xử lý |
|---|---|---|
| `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine` | Docker Desktop chưa chạy | PowerShell: `Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"`; chờ `docker info` thành công |
| `[test-run] Ảnh Docker (...) cũ hơn commit mã cuối` | Mã trong `backend/ frontend/ deploy/` đổi sau khi build ảnh | Hỏi người dùng rồi chạy `run_layers.sh --build e2e`. Không build thì kết quả E2E không phản ánh mã hiện tại |
| `Hết thời gian chờ http://localhost:5173/` | Frontend container chậm khởi động, hoặc cổng bị tiến trình khác chiếm (`npm run dev` đang mở) | `docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.e2e.yml ps`; xem log `frontend`; tắt dev server cục bộ |
| `curl` trả `000` ngay sau `up -d` | Bình thường — container vừa start; script đã chờ tối đa 3 phút | — |
| Backend pytest chạy rất lâu (> 15 phút) | Docker thiếu RAM, swap | Đóng ứng dụng khác; giới hạn WSL trong `%UserProfile%\.wslconfig` |
| `Python was not found` | Máy không có Python cục bộ | Tầng `eval` chạy trong ảnh `cwd-backend-dev`; không cài Python |
| `Chưa có ảnh cwd-backend-dev` | Chưa chạy tầng backend lần nào | Chạy `run_layers.sh backend` trước (script tự build ảnh dev) |
| Đường dẫn gắn volume sai (`/d/Code/...` không tồn tại trong container) | Git Bash đổi đường dẫn | Script đặt `MSYS_NO_PATHCONV=1` và dùng `pwd -W`; khi tự viết lệnh `docker run -v` hãy làm tương tự |

## Ảnh E2E

- **Ảnh trùng sang ca sau:** `auth.spec.ts` ("không có quyền") và `delete-audit.spec.ts` ("quản trị bảo mật") mở trang bằng `browser.newPage()` mà không đóng; với `screenshot: 'on'`, Playwright chụp lại các trang đó ở mọi ca sau. `build_run_docs.mjs` bỏ ảnh có kích thước lệch ≤ 50 byte so với ảnh của ca liền trước.
  Đừng nới dung sai: hai màn hình khác nhau thật từng chỉ lệch ~185 byte và bị loại nhầm ở dung sai 300. Đừng lọc theo nội dung toàn cục: ca "đăng nhập đúng" và "chỉ dùng bàn phím" có cùng màn hình chính, lọc toàn cục làm mất ảnh của một ca.
- **Kiểm tra:** số ảnh nên bằng số ca E2E, cộng một ảnh cho mỗi ca mở thêm trang (hiện là ca 09 và 12). Thiếu ảnh của một ca → xem kích thước các ảnh đính kèm trong `e2e-playwright.json` của ca đó và ca trước.
- `screenshots.spec.ts` ghi ảnh S-01..S-07 vào `docs/implement/evidence/screenshots/` (tệp đã commit) — `git status` sẽ thấy các ảnh này thay đổi. Đây là chủ đích của spec; báo người dùng.

## Ghi chú khi sửa script

- Viết regex trong tệp `.mjs` bằng công cụ Edit/Write, không qua `node -e '...'` hoặc `sed` lồng nhiều lớp nháy — dấu `\` trong `\[TBD` và `\.` dễ bị nuốt, gây lỗi cú pháp hoặc khớp sai âm thầm.
- `build_run_docs.mjs` dùng lại quy tắc khớp tên (`parseRefs`, `matches`, `fileKeyOf`) của `collect_results.mjs`. Sửa một bên thì sửa cả bên kia, nếu không bảng "Kiểm thử đã chạy" của ca sẽ lệch với trạng thái ca.
