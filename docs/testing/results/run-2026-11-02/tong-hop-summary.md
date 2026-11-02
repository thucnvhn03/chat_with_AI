# Tổng hợp kết quả kiểm thử

Sinh lúc 2026-11-02T13:25:16.292Z bởi `collect_results.mjs`.

## Nguồn kết quả

| Tệp | Tầng | Tổng | Đạt | Lỗi | Bỏ qua | Thời gian (s) | Sửa lần cuối |
|---|---|---|---|---|---|---|---|
| `test-results\run-2026-11-02\backend-pytest.xml` | backend | 186 | 185 | 0 | 1 | 321.1 | 2026-11-02T13:10 |
| `test-results\run-2026-11-02\frontend-vitest.xml` | frontend | 79 | 79 | 0 | 0 | 65.9 | 2026-11-02T13:01 |
| `test-results\run-2026-11-02\e2e-playwright.xml` | e2e | 20 | 20 | 0 | 0 | 342.7 | 2026-11-02T13:19 |
| `test-results\run-2026-11-02\evaluation-pytest.xml` | evaluation | 12 | 12 | 0 | 0 | 0.3 | 2026-11-02T13:22 |

## Trạng thái ca theo nhóm

| Nhóm | Tổng | Đạt | Không đạt | Bỏ qua | Chưa có kết quả | Thủ công — chưa ghi nhận | Bị chặn |
|---|---|---|---|---|---|---|---|
| 01_unit | 22 | 22 | 0 | 0 | 0 | 0 | 0 |
| 02_integration_api | 40 | 40 | 0 | 0 | 0 | 0 | 0 |
| 03_e2e_system | 13 | 13 | 0 | 0 | 0 | 0 | 0 |
| 04_acceptance | 11 | 0 | 0 | 0 | 0 | 11 | 0 |
| 05_performance | 6 | 2 | 0 | 0 | 0 | 4 | 0 |
| 06_security | 13 | 11 | 0 | 0 | 0 | 2 | 0 |
| 07_accessibility | 8 | 6 | 0 | 0 | 0 | 2 | 0 |
| 08_ui | 8 | 5 | 0 | 0 | 0 | 3 | 0 |
| 09_api | 15 | 15 | 0 | 0 | 0 | 0 | 0 |
| 10_quality_evaluation | 8 | 0 | 0 | 0 | 0 | 8 | 0 |
| 11_operations | 5 | 3 | 0 | 0 | 0 | 2 | 0 |
| **Tổng** | **149** | **117** | **0** | **0** | **0** | **32** | **0** |

## Từng ca

| Mã | Tên | Ưu tiên | Trạng thái | Ghi chú |
|---|---|---|---|---|
| UT-001 | Trích xuất PDF giữ số trang | Cao | Đạt |  |
| UT-002 | Chuẩn hóa tiếng Việt về NFC | Cao | Đạt |  |
| UT-003 | Phân loại lỗi PDF | Cao | Đạt |  |
| UT-004 | Chunk không vượt ranh giới trang | Cao | Đạt |  |
| UT-005 | Trang ngắn và trang rỗng | Trung bình | Đạt |  |
| UT-006 | Giới hạn token, chồng lấp và ghép lại văn bản | Cao | Đạt |  |
| UT-007 | Lớp từ chối 1: dưới ngưỡng không gọi mô hình | Cao | Đạt |  |
| UT-008 | Lớp từ chối 2: câu từ chối cố định | Cao | Đạt |  |
| UT-009 | Lớp từ chối 3: có nội dung nhưng không có nguồn hợp lệ | Cao | Đạt |  |
| UT-010 | Ánh xạ và gộp citation | Cao | Đạt |  |
| UT-011 | Ghép câu hỏi trước vào truy vấn | Trung bình | Đạt |  |
| UT-012 | Adapter Claude: ánh xạ citation | Cao | Đạt |  |
| UT-013 | Adapter Claude: từ chối và cắt cụt | Cao | Đạt |  |
| UT-014 | Adapter Claude: hình dạng yêu cầu | Cao | Đạt |  |
| UT-015 | Adapter OIDC: kiểm tra ID token | Cao | Đạt |  |
| UT-016 | Định dạng lỗi chung, không lộ chi tiết kỹ thuật | Cao | Đạt |  |
| UT-017 | Log không chứa nội dung câu hỏi | Cao | Đạt |  |
| UT-018 | Tiến trình API nạp đủ model | Cao | Đạt |  |
| UT-019 | Mọi ngưỡng là trường cấu hình | Cao | Đạt |  |
| UT-020 | Bảng thông báo lỗi tải lên | Trung bình | Đạt |  |
| UT-021 | Tô sáng đoạn trích trong trang nguồn | Trung bình | Đạt |  |
| UT-022 | Công thức chỉ số của bộ đánh giá | Cao | Đạt |  |
| INT-API-001 | Đăng nhập thành công | Cao | Đạt |  |
| INT-API-002 | Sai thông tin đăng nhập không tiết lộ tài khoản | Cao | Đạt |  |
| INT-API-003 | Đăng nhập đúng nhưng chưa được cấp quyền | Cao | Đạt |  |
| INT-API-004 | Bảo vệ CSRF theo Origin | Cao | Đạt |  |
| INT-API-005 | Phiên hết hạn | Cao | Đạt |  |
| INT-API-006 | Người bị thu hồi mất truy cập ngay | Cao | Đạt |  |
| INT-API-007 | Tải nhiều tệp, mỗi tệp xét độc lập | Cao | Đạt |  |
| INT-API-008 | Giới hạn số tài liệu mỗi người | Trung bình | Đạt |  |
| INT-API-009 | Nạp PDF hợp lệ tới trạng thái sẵn sàng | Cao | Đạt |  |
| INT-API-010 | Lý do lỗi do worker xác định | Cao | Đạt |  |
| INT-API-011 | Lỗi tạm thời được thử lại rồi chuyển failed | Cao | Đạt |  |
| INT-API-012 | Tài liệu bị xóa trong lúc đang nạp | Cao | Đạt |  |
| INT-API-013 | Nhiều worker không lấy trùng việc | Cao | Đạt |  |
| INT-API-014 | Thử lại tài liệu lỗi | Trung bình | Đạt |  |
| INT-API-015 | Truy xuất không bao giờ trả tài liệu ngoài phạm vi | Cao | Đạt |  |
| INT-API-016 | Chỉ truy xuất tài liệu sẵn sàng | Cao | Đạt |  |
| INT-API-017 | Đủ TOP_K khi danh sách được phép nhỏ trong kho lớn | Trung bình | Đạt |  |
| INT-API-018 | Giới hạn số chunk mỗi tài liệu | Trung bình | Đạt |  |
| INT-API-019 | Câu trả lời có nguồn đúng tài liệu và trang | Cao | Đạt |  |
| INT-API-020 | Câu ngoài phạm vi không gọi mô hình | Cao | Đạt |  |
| INT-API-021 | Kiểm tra độ dài câu hỏi | Trung bình | Đạt |  |
| INT-API-022 | Dịch vụ AI từ chối hoặc quá thời gian | Cao | Đạt |  |
| INT-API-023 | Mỗi câu hỏi đúng một bản ghi kiểm toán, không nội dung | Cao | Đạt |  |
| INT-API-024 | Lỗi commit không bị nuốt | Cao | Đạt |  |
| INT-API-025 | Lịch sử hội thoại và câu hỏi tiếp theo | Trung bình | Đạt |  |
| INT-API-026 | Trang nguồn: trang không hợp lệ và quyền | Cao | Đạt |  |
| INT-API-027 | Tải tệp gốc qua backend | Trung bình | Đạt |  |
| INT-API-028 | Xóa loại tài liệu khỏi truy vấn ngay lập tức | Cao | Đạt |  |
| INT-API-029 | Xóa vĩnh viễn | Cao | Đạt |  |
| INT-API-030 | Xóa vĩnh viễn chịu lỗi và làm lại được | Cao | Đạt |  |
| INT-API-031 | Quyền xóa tài liệu | Cao | Đạt |  |
| INT-API-032 | Đánh giá câu trả lời | Thấp | Đạt |  |
| INT-API-033 | Bản ghi kiểm toán: lọc và phân trang | Trung bình | Đạt |  |
| INT-API-034 | Báo cáo sử dụng theo tuần | Trung bình | Đạt |  |
| INT-API-035 | Quản lý quyền truy cập | Cao | Đạt |  |
| INT-API-036 | Health báo lỗi khi thành phần dừng | Trung bình | Đạt |  |
| INT-API-037 | Đăng nhập OIDC | Cao | Đạt |  |
| INT-API-038 | Lệnh tạo quản trị viên đầu tiên | Trung bình | Đạt |  |
| INT-API-039 | Migration và ràng buộc lược đồ | Cao | Đạt |  |
| INT-API-040 | Dọn dữ liệu định kỳ theo thời hạn lưu | Trung bình | Đạt |  |
| E2E-001 | Đăng nhập đúng và sai | Cao | Đạt |  |
| E2E-002 | Người bị thu hồi quyền không vào được | Cao | Đạt |  |
| E2E-003 | Hết phiên giữ câu hỏi đang soạn | Cao | Đạt |  |
| E2E-004 | Trạng thái trống | Trung bình | Đạt |  |
| E2E-005 | Tải PDF hợp lệ tới "Sẵn sàng" | Cao | Đạt |  |
| E2E-006 | Tệp hỏng và tệp không phải PDF | Cao | Đạt |  |
| E2E-007 | Mất mạng khi tải lên | Cao | Đạt |  |
| E2E-008 | Hỏi đáp có nguồn và trình xem nguồn | Cao | Đạt |  |
| E2E-009 | Mất mạng khi hỏi | Cao | Đạt |  |
| E2E-010 | Xóa tài liệu | Cao | Đạt |  |
| E2E-011 | Quản trị quyền và bản ghi kiểm toán | Trung bình | Đạt |  |
| E2E-012 | Khả năng tiếp cận trên mọi màn hình | Cao | Đạt |  |
| E2E-013 | Ảnh màn hình đối chiếu với thiết kế | Trung bình | Đạt |  |
| UAT-001 | Tải nhiều PDF thật |  | Thủ công — chưa ghi nhận |  |
| UAT-002 | Tệp lỗi có lý do dễ hiểu |  | Thủ công — chưa ghi nhận |  |
| UAT-003 | Trả lời câu hỏi thường gặp có nguồn |  | Thủ công — chưa ghi nhận |  |
| UAT-004 | Không bịa khi tài liệu không có thông tin |  | Thủ công — chưa ghi nhận |  |
| UAT-005 | Hỏi tiếp bằng đại từ |  | Thủ công — chưa ghi nhận |  |
| UAT-006 | Xóa tài liệu và xác nhận xóa vĩnh viễn |  | Thủ công — chưa ghi nhận |  |
| UAT-007 | Cấp/thu hồi quyền và cô lập tài liệu |  | Thủ công — chưa ghi nhận |  |
| UAT-008 | Tra cứu bản ghi kiểm toán |  | Thủ công — chưa ghi nhận |  |
| UAT-009 | Báo cáo mức sử dụng |  | Thủ công — chưa ghi nhận |  |
| UAT-010 | Nghiệm thu chất lượng theo ngôn ngữ |  | Thủ công — chưa ghi nhận |  |
| UAT-011 | Rà soát chính sách dữ liệu |  | Thủ công — chưa ghi nhận |  |
| PERF-001 | Độ trễ hỏi đáp trên bộ câu hỏi chuẩn | Cao | Thủ công — chưa ghi nhận |  |
| PERF-002 | Tải nhẹ hỏi đáp đồng thời | Trung bình | Thủ công — chưa ghi nhận |  |
| PERF-003 | Thời gian nạp tài liệu | Trung bình | Thủ công — chưa ghi nhận |  |
| PERF-004 | Truy xuất trong kho lớn có lọc quyền | Trung bình | Thủ công — chưa ghi nhận |  |
| PERF-005 | Phản hồi giao diện | Trung bình | Đạt |  |
| PERF-006 | Hết thời gian chờ đúng hạn | Cao | Đạt |  |
| SEC-001 | Mọi route yêu cầu phiên | Cao | Đạt |  |
| SEC-002 | Phân quyền theo vai trò | Cao | Đạt |  |
| SEC-003 | Cô lập dữ liệu giữa người dùng | Cao | Đạt |  |
| SEC-004 | Chính sách mật khẩu và khóa tạm | Cao | Đạt |  |
| SEC-005 | Quản lý phiên | Cao | Đạt |  |
| SEC-006 | Chống CSRF | Cao | Đạt |  |
| SEC-007 | Chống XSS từ nội dung câu trả lời | Cao | Đạt |  |
| SEC-008 | Tiêu đề bảo mật của frontend production | Trung bình | Thủ công — chưa ghi nhận |  |
| SEC-009 | Không lộ thông tin qua lỗi | Cao | Đạt |  |
| SEC-010 | Log và sự kiện không chứa nội dung (canary) | Cao | Đạt |  |
| SEC-011 | Kiểm tra tệp tải lên theo nội dung | Cao | Đạt |  |
| SEC-012 | Quét lỗ hổng phụ thuộc | Trung bình | Thủ công — chưa ghi nhận |  |
| SEC-013 | Dữ liệu gửi ra dịch vụ AI | Cao | Đạt | Thủ công: 2026-11-02 · Claude Code (hỗ trợ QA) · Phần thủ công bước 3: git grep sk-ant-… trên mã đã theo dõi: 0 kết quả; deploy/.env bị .gitignore bỏ qua. Phần tự động (test_request_shape, test_out_of_scope…) đạt trong run-2026-11-02 |
| ACC-001 | Dùng được chỉ bằng bàn phím | Cao | Đạt | Phần tự động đạt; phần thủ công chưa ghi nhận |
| ACC-002 | Trình đọc màn hình | Cao | Thủ công — chưa ghi nhận |  |
| ACC-003 | Tương phản màu | Cao | Đạt |  |
| ACC-004 | Thuộc tính ARIA | Cao | Thủ công — chưa ghi nhận |  |
| ACC-005 | Quản lý tiêu điểm | Cao | Đạt |  |
| ACC-006 | Thông báo lỗi được trình đọc màn hình nhận | Trung bình | Đạt |  |
| ACC-007 | Thu phóng 200% | Trung bình | Đạt | Phần tự động đạt; phần thủ công chưa ghi nhận |
| ACC-008 | Không chỉ dùng màu để truyền thông tin | Trung bình | Đạt |  |
| UI-001 | Đối chiếu ảnh mẫu theo từng trạng thái | Cao | Đạt | Phần tự động đạt; phần thủ công chưa ghi nhận |
| UI-002 | Độ rộng màn hình | Thấp | Thủ công — chưa ghi nhận |  |
| UI-003 | Trạng thái của thành phần | Trung bình | Đạt |  |
| UI-004 | Tương tác | Trung bình | Thủ công — chưa ghi nhận |  |
| UI-005 | Trạng thái lỗi | Cao | Thủ công — chưa ghi nhận |  |
| UI-006 | Trạng thái chờ | Trung bình | Đạt |  |
| UI-007 | Thông báo | Thấp | Đạt |  |
| UI-008 | Điều hướng | Cao | Đạt |  |
| API-001 | `POST /auth/login` |  | Đạt | Theo INT-API-001: Đạt, INT-API-002: Đạt, INT-API-003: Đạt, INT-API-004: Đạt, SEC-004: Đạt, INT-API-037: Đạt |
| API-002 | `GET /auth/me`, `POST /auth/logout` |  | Đạt | Theo INT-API-001: Đạt, INT-API-005: Đạt, INT-API-006: Đạt, SEC-005: Đạt |
| API-003 | `GET /auth/oidc/login`, `GET /auth/oidc/callback` |  | Đạt | Theo INT-API-037: Đạt, UT-015: Đạt |
| API-004 | `POST /documents` |  | Đạt | Theo INT-API-007: Đạt, INT-API-008: Đạt, INT-API-009: Đạt, SEC-011: Đạt |
| API-005 | `GET /documents`, `GET /documents/{id}` |  | Đạt | Theo INT-API-009: Đạt, INT-API-028: Đạt, SEC-003: Đạt |
| API-006 | `POST /documents/{id}/retry` |  | Đạt | Theo INT-API-014: Đạt |
| API-007 | `DELETE /documents/{id}` |  | Đạt | Theo INT-API-028: Đạt, INT-API-029: Đạt, INT-API-030: Đạt, INT-API-031: Đạt |
| API-008 | `GET /documents/{id}/pages/{page}`, `GET /documents/{id}/file` |  | Đạt | Theo INT-API-019: Đạt, INT-API-026: Đạt, INT-API-027: Đạt |
| API-009 | `POST /events/source-opened` |  | Đạt | Theo SEC-003: Đạt |
| API-010 | `POST /conversations`, `POST\|GET /conversations/{id}/messages` |  | Đạt | Theo INT-API-019: Đạt, INT-API-020: Đạt, INT-API-021: Đạt, INT-API-022: Đạt, INT-API-023: Đạt, INT-API-024: Đạt, INT-API-025: Đạt |
| API-011 | `PUT /messages/{id}/feedback` |  | Đạt | Theo INT-API-032: Đạt |
| API-012 | `GET\|POST /admin/access`, `DELETE /admin/access/{user_id}` |  | Đạt | Theo INT-API-035: Đạt, SEC-002: Đạt |
| API-013 | `GET /admin/audit` |  | Đạt | Theo INT-API-033: Đạt |
| API-014 | `GET /reports/usage` |  | Đạt | Theo INT-API-034: Đạt |
| API-015 | `GET /health/live`, `GET /health/ready`, `GET /metrics` |  | Đạt | Theo INT-API-036: Đạt, OPS-001: Đạt |
| QE-001 | Đúng và có nguồn (MET-002) |  | Thủ công — chưa ghi nhận |  |
| QE-002 | Tỷ lệ bịa |  | Thủ công — chưa ghi nhận |  |
| QE-003 | Ngoài phạm vi hỏi tiếp trong cùng hội thoại |  | Thủ công — chưa ghi nhận |  |
| QE-004 | Độ phủ nguồn khi hỏi nhiều tài liệu |  | Thủ công — chưa ghi nhận |  |
| QE-005 | Câu hỏi tiếp theo |  | Thủ công — chưa ghi nhận |  |
| QE-006 | Đúng trang và câu trả lời có nội dung có nguồn |  | Thủ công — chưa ghi nhận |  |
| QE-007 | Kết quả theo ngôn ngữ |  | Thủ công — chưa ghi nhận |  |
| QE-008 | Đối chiếu chấm tự động với chấm tay |  | Thủ công — chưa ghi nhận |  |
| OPS-001 | Health báo lỗi khi một thành phần dừng | Trung bình | Đạt | Theo INT-API-036: Đạt |
| OPS-002 | Luật cảnh báo phát đúng | Trung bình | Đạt |  |
| OPS-003 | Theo dõi tài liệu xóa quá hạn | Trung bình | Đạt |  |
| OPS-004 | Triển khai theo tài liệu vận hành | Trung bình | Thủ công — chưa ghi nhận |  |
| OPS-005 | Khôi phục sao lưu không "hồi sinh" tài liệu đã xóa | Trung bình | Thủ công — chưa ghi nhận |  |

## Bộ đánh giá

- Tệp: `evaluation\reports\v1-20261023T130536Z.json` (2026-10-23T13:05:35+00:00)
- Cấu hình: KIEM CHUNG LUONG: EMBEDDING_PROVIDER=hash, ANSWER_PROVIDER=fake - khong phai so lieu chat luong
- Chi phí: không ghi

| Chỉ số | Giá trị |
|---|---|
| correct_with_source | 70.8% |
| hallucination_rate | 75.0% |
| source_coverage | 0.0% |
| follow_up_correct | 58.3% |
| correct_page | 100.0% |
| answers_with_content_having_source | 100.0% |
| latency p50/p90/p95 (ms) | 197 / 319 / 356 |

## Kiểm thử chưa gắn với ca nào (26)

- test_auth.py › test_session_started_once_per_day
- test_ingestion_flow.py › test_user_cannot_see_or_touch_other_users_documents
- test_qa_flow.py › test_source_opened_event
- test_storage_and_queue.py › test_file_store_put_get_delete_twice
- test_claude_adapter.py › test_real_api_cites_correct_chunk
- test_extract.py › test_extract_single_page_and_out_of_range
- test_extract.py › test_normalize_whitespace
- test_framework.py › test_health_live_and_ready
- test_framework.py › test_health_ready_reports_failed_component
- test_framework.py › test_response_carries_request_id
- test_qa_service.py › test_refused_is_not_not_found
- test_smoke.py › test_package_is_importable[app.api]
- test_smoke.py › test_package_is_importable[app.modules.access]
- test_smoke.py › test_package_is_importable[app.modules.documents]
- test_smoke.py › test_package_is_importable[app.modules.ingestion]
- test_smoke.py › test_package_is_importable[app.modules.retrieval]
- test_smoke.py › test_package_is_importable[app.modules.qa]
- test_smoke.py › test_package_is_importable[app.modules.conversation]
- test_smoke.py › test_package_is_importable[app.modules.sources]
- test_smoke.py › test_package_is_importable[app.modules.usage]
- test_smoke.py › test_package_is_importable[app.modules.audit]
- test_smoke.py › test_package_is_importable[app.modules.jobs]
- test_smoke.py › test_package_is_importable[app.ports]
- test_smoke.py › test_package_is_importable[app.adapters]
- test_smoke.py › test_package_is_importable[app.worker]
- test_smoke.py › test_package_is_importable[app.observability]
