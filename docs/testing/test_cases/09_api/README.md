# 09 — Ca kiểm thử API theo hợp đồng (API-001..API-015)

Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md) mục 6.1.10. Đặc tả: OpenAPI tại `/api/v1/openapi.json` (bản lưu: `frontend/src/api/openapi.json`); implement_plan.md mục 4. Mỗi ca trong nhóm tập hợp các kiểm tra hợp đồng của một endpoint; bước chi tiết nằm ở ca tích hợp được dẫn chiếu trong [02_integration_api/](../02_integration_api/README.md).

**Kiểm tra hợp đồng chung cho mọi endpoint**
- Phản hồi thành công khớp schema OpenAPI (tên trường, kiểu, trường bắt buộc).
- Phản hồi lỗi có dạng `{"error": {"code": <chuỗi ổn định>, "message": <tiếng Việt, không chi tiết kỹ thuật>}}`.
- Endpoint cần phiên trả 401 khi không có phiên (SEC-001); yêu cầu thay đổi dữ liệu cần `Origin` hợp lệ (SEC-006).
- Kiểu TypeScript của frontend sinh từ OpenAPI và khớp với backend (job CI `openapi-types`: xuất lại OpenAPI, sinh lại kiểu, `git diff` phải rỗng).

## Danh sách ca (15)

| Mã ca | Tên |
|---|---|
| [API-001](API-001.md) | `POST /auth/login` |
| [API-002](API-002.md) | `GET /auth/me`, `POST /auth/logout` |
| [API-003](API-003.md) | `GET /auth/oidc/login`, `GET /auth/oidc/callback` |
| [API-004](API-004.md) | `POST /documents` |
| [API-005](API-005.md) | `GET /documents`, `GET /documents/{id}` |
| [API-006](API-006.md) | `POST /documents/{id}/retry` |
| [API-007](API-007.md) | `DELETE /documents/{id}` |
| [API-008](API-008.md) | `GET /documents/{id}/pages/{page}`, `GET /documents/{id}/file` |
| [API-009](API-009.md) | `POST /events/source-opened` |
| [API-010](API-010.md) | `POST /conversations`, `POST|GET /conversations/{id}/messages` |
| [API-011](API-011.md) | `PUT /messages/{id}/feedback` |
| [API-012](API-012.md) | `GET|POST /admin/access`, `DELETE /admin/access/{user_id}` |
| [API-013](API-013.md) | `GET /admin/audit` |
| [API-014](API-014.md) | `GET /reports/usage` |
| [API-015](API-015.md) | `GET /health/live`, `GET /health/ready`, `GET /metrics` |
