# MCP server — "Chat với tài liệu"

Cho phép Claude (Claude Code, Claude Desktop hoặc client MCP bất kỳ) dùng hệ thống "Chat với tài liệu" thay người dùng:
tải PDF lên, hỏi đáp **có nguồn (tên tệp, số trang)**, đọc trang nguồn, xem lịch sử, đánh giá câu trả lời, xem báo cáo sử dụng.

MCP server chỉ là một client của API `/api/v1`, giống giao diện web. Server đăng nhập bằng tài khoản người dùng, nên mọi quy tắc của backend vẫn áp dụng như khi dùng giao diện web:
- vai trò;
- cô lập tài liệu giữa người dùng;
- bản ghi kiểm toán;
- giới hạn tệp và độ dài câu hỏi;
- ngưỡng "không tìm thấy" khi tài liệu không có thông tin.

```
Claude ──MCP (stdio)──> mcp/dist/index.js ──HTTP + cookie phiên──> backend /api/v1
```

## Tool

| Tool | Vai trò | Việc làm | Loại |
|---|---|---|---|
| `whoami` | mọi vai trò | Tài khoản, vai trò, giới hạn hệ thống | đọc |
| `list_documents` | bd | Tài liệu: trạng thái, số trang, dung lượng, lý do lỗi (tiếng Việt), id | đọc |
| `upload_documents` | bd | Tải PDF từ đường dẫn trên máy; mặc định chờ tới "Sẵn sàng"/"Lỗi". Kiểm sớm đuôi, chữ ký `%PDF-`, dung lượng | ghi |
| `retry_document` | bd | Xử lý lại tài liệu lỗi | ghi |
| `delete_document` | bd, security_admin | **Xóa vĩnh viễn**; phải truyền đúng tên tệp (`confirm_file_name`) | xóa |
| `ask` | bd | Hỏi; trả lời kèm nguồn; câu hỏi tiếp dùng chung hội thoại | ghi |
| `new_conversation` | bd | Hội thoại mới, không mang ngữ cảnh cũ | ghi |
| `get_conversation` | bd | Lịch sử hỏi đáp kèm nguồn | đọc |
| `get_source_page` | bd | Văn bản một trang (kiểm tra nguồn); ghi sự kiện "mở nguồn" như giao diện web | đọc |
| `send_feedback` | bd | Hữu ích / Không hữu ích cho một câu trả lời | ghi |
| `usage_report` | manager | Báo cáo sử dụng theo tuần | đọc |

Gọi tool không đúng vai trò → backend trả `forbidden_role`, tool báo lỗi rõ ràng.

Ví dụ kết quả `ask` (stack E2E, AI giả lập):

```
Cac ben giai quyet tranh chap bang thuong luong.

Nguồn:
[1] HopDong_mvkxbm4k34tk.pdf, tr. 3 — "Cac ben giai quyet tranh chap bang thuong luong." (document_id 60c11bed-…)

(conversation_id 62e86a71-… · message_id 3881b126-… · 386 ms)
```

## Cài đặt

Cần Node ≥ 20 và backend đang chạy, ví dụ `docker compose -f deploy/docker-compose.yml up -d`.

```bash
cd mcp
npm ci
npm run build        # tạo mcp/dist/index.js
```

### Biến môi trường

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `CWD_LOGIN` | — (bắt buộc) | Tên đăng nhập (tài khoản nội bộ, `AUTH_MODE=local`) |
| `CWD_PASSWORD` | — (bắt buộc) | Mật khẩu. Đặt trong biến môi trường của máy, **không** ghi vào tệp cấu hình đã commit |
| `CWD_API_URL` | `http://localhost:8000/api/v1` | Gốc API |
| `CWD_ORIGIN` | `http://localhost:5173` | Header `Origin` cho yêu cầu thay đổi dữ liệu; phải thuộc `ALLOWED_ORIGINS` của backend (chống CSRF) |
| `CWD_UPLOAD_WAIT_SECONDS` | `180` | Thời gian tối đa chờ tài liệu xử lý xong khi tải lên |

### Claude Code

Repo đã có [`.mcp.json`](../.mcp.json). Server `chat-with-docs` đọc `CWD_LOGIN` và `CWD_PASSWORD` từ môi trường của bạn:

```bash
export CWD_LOGIN=e2e.bd CWD_PASSWORD='...'     # PowerShell: $env:CWD_LOGIN='e2e.bd'; $env:CWD_PASSWORD='...'
claude                                          # chạy từ gốc repo, chấp nhận server dự án khi được hỏi
```

Kiểm tra bằng `/mcp` trong Claude Code. Thử hỏi: "Liệt kê tài liệu của tôi", "Thời hạn thanh toán trong hợp đồng A là bao lâu?".

### Claude Desktop

Thêm vào `claude_desktop_config.json` (Windows: `%APPDATA%\Claude\claude_desktop_config.json`), dùng đường dẫn tuyệt đối:

```json
{
  "mcpServers": {
    "chat-with-docs": {
      "command": "node",
      "args": ["D:/Code/VTI/chat_with_AI/mcp/dist/index.js"],
      "env": { "CWD_LOGIN": "<tên đăng nhập>", "CWD_PASSWORD": "<mật khẩu>" }
    }
  }
}
```

Tệp này nằm trên máy cá nhân và chứa mật khẩu dạng rõ, nên chỉ dùng tài khoản của chính bạn.

## Bảo mật và giới hạn

- **Quyền.** MCP có đúng quyền của tài khoản đã cấu hình, không hơn. Mỗi người dùng cấu hình bằng tài khoản của chính mình.
- **Log.**
  - Không ghi câu hỏi, câu trả lời hay mật khẩu ra log. Log chỉ ghi ra stderr, vì stdout dành cho giao thức MCP.
  - Backend vẫn ghi bản ghi kiểm toán cho mỗi câu hỏi, như khi dùng giao diện web.
- **Tải tệp lên.** `upload_documents` đọc tệp trên máy chạy MCP server, nhưng chỉ gửi tệp có đuôi `.pdf` và bắt đầu bằng `%PDF-`.
- **Xóa tài liệu.** `delete_document` có chú thích `destructiveHint`, nên client MCP sẽ hỏi bạn trước khi chạy. Tool còn bắt truyền đúng tên tệp để tránh xóa nhầm theo id.
- **OIDC.**
  - `AUTH_MODE=oidc` **chưa hỗ trợ**: đăng nhập OIDC cần trình duyệt.
  - Khi chuyển sang OIDC, cần thêm cơ chế token cho client không có trình duyệt ở backend, ví dụ token cá nhân hoặc device flow. Việc này cần bộ phận bảo mật duyệt.
- **Chức năng quản trị bảo mật** (cấp/thu hồi quyền, xem nhật ký kiểm toán) cố ý **không** đưa vào MCP.

## Kiểm thử

```bash
npm test                     # 17 kiểm thử đơn vị: MCP client ↔ server qua InMemoryTransport, backend giả lập
npm run build && CWD_IT=1 npm run test:integration
                             # 9 kiểm thử tích hợp: tiến trình MCP thật ↔ backend thật của stack E2E
                             # (docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.e2e.yml up -d)
```

Kiểm thử tích hợp:
- dùng các tài khoản mẫu `e2e.bd`, `e2e.bd2` và `e2e.manager`;
- tải lên một PDF tạm, hỏi, đối chiếu nguồn đúng tệp và đúng trang, rồi đọc trang nguồn;
- kiểm tra "không tìm thấy" khi tài liệu không có thông tin;
- kiểm tra cô lập: tài khoản BD khác không đọc được tài liệu này;
- kiểm tra phân quyền báo cáo sử dụng (BD bị từ chối, quản lý xem được);
- cuối cùng xóa tài liệu kiểm thử.
