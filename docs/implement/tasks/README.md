# THƯ MỤC TASK TRIỂN KHAI

Mỗi file là một task độc lập, tách từ [implement_tasks.md](../implement_tasks.md) (61 task). Đọc kèm [implement_plan.md](../implement_plan.md).

Quy ước tên file: `T<sprint>-<số>-<tên-rút-gọn>.md`. Đổi giá trị dòng "Trạng thái" trong bảng đầu mỗi file (To do / In progress / Review / Done) khi làm.

## Sprint 0 — Nền tảng và spike

- Cổng G0 (cuối Sprint 0): chốt bộ công nghệ, DQ-003, kết quả ba spike.

| Task | Tên | Loại | Cỡ | Story | Phụ thuộc |
|---|---|---|---|---|---|
| [T0-01](T0-01-khoi-tao-kho-ma-va-cong-cu.md) | Khởi tạo kho mã và công cụ | OPS | M | — | — |
| [T0-02](T0-02-docker-compose-moi-truong-cuc-bo.md) | Docker Compose môi trường cục bộ | OPS | M | — | T0-01 |
| [T0-03](T0-03-pipeline-ci.md) | Pipeline CI | OPS | M | — | T0-01 |
| [T0-04](T0-04-khung-backend-cau-hinh-log-loi-health.md) | Khung backend: cấu hình, log, lỗi, health | BE | M | — | T0-01 |
| [T0-05](T0-05-khung-frontend-va-token-giao-dien.md) | Khung frontend và token giao diện | FE | M | — | T0-01 |
| [T0-06](T0-06-spike-trich-xuat-pdf.md) | Spike trích xuất PDF | SPK | M | — | T0-01; tập PDF mẫu từ business owner (DEP-001; nếu chưa có, dùng PDF công khai không nhạy cảm) |
| [T0-07](T0-07-spike-embedding-va-truy-xuat-tieng-viet.md) | Spike embedding và truy xuất tiếng Việt | SPK | M | US-012 | T0-06 |
| [T0-08](T0-08-spike-sinh-cau-tra-loi-co-trich-dan.md) | Spike sinh câu trả lời có trích dẫn | SPK | S | — | T0-07; dữ liệu **không nhạy cảm**; khóa API (không commit) |
| [T0-09](T0-09-khung-bo-danh-gia.md) | Khung bộ đánh giá | QA | S | US-016 | T0-01 |
| [T0-10](T0-10-nen-co-so-du-lieu-va-kiem-thu-tich-hop.md) | Nền cơ sở dữ liệu và kiểm thử tích hợp | BE | S | — | T0-04 |

## Sprint 1 — Truy cập và nạp tài liệu

| Task | Tên | Loại | Cỡ | Story | Phụ thuộc |
|---|---|---|---|---|---|
| [T1-01](T1-01-migration-users-access-grants.md) | Migration `users`, `access_grants` | BE | S | US-017 | T0-10 |
| [T1-02](T1-02-cong-xac-thuc-va-adapter-tai-khoan-noi-bo.md) | Cổng xác thực và adapter tài khoản nội bộ | BE | M | US-017 | T1-01 |
| [T1-03](T1-03-adapter-oidc-chi-lam-neu-dq-003-chon-oidc.md) | Adapter OIDC (chỉ làm nếu DQ-003 chọn OIDC) | BE | M | US-017 | T1-02, G0 |
| [T1-04](T1-04-phien-endpoint-xac-thuc-va-require-role.md) | Phiên, endpoint xác thực và `require_role` | BE | M | US-017 | T1-02 |
| [T1-05](T1-05-endpoint-quan-ly-quyen-va-tai-khoan-dau-tien.md) | Endpoint quản lý quyền và tài khoản đầu tiên | BE | M | US-017 | T1-04 |
| [T1-06](T1-06-man-hinh-s-01-dang-nhap-va-authgate.md) | Màn hình S-01 Đăng nhập và AuthGate | FE | M | US-017 | T0-05, T1-04 |
| [T1-07](T1-07-man-hinh-s-05-quan-ly-quyen.md) | Màn hình S-05 Quản lý quyền | FE | M | US-017 | T1-05, T1-06 |
| [T1-08](T1-08-kiem-thu-bao-mat-xac-thuc.md) | Kiểm thử bảo mật xác thực | QA | S | US-017 | T1-04, T1-05 |
| [T1-09](T1-09-migration-documents-jobs-chunks.md) | Migration `documents`, `jobs`, `chunks` | BE | S | US-001 | T0-10 |
| [T1-10](T1-10-cong-luu-tep-va-adapter-kho-doi-tuong.md) | Cổng lưu tệp và adapter kho đối tượng | BE | S | US-001 | T0-02 |
| [T1-11](T1-11-endpoint-post-documents-kiem-tra-tep.md) | Endpoint `POST /documents` (kiểm tra tệp) | BE | M | US-001, US-002, US-003 | T1-04, T1-09, T1-10 |
| [T1-12](T1-12-hang-doi-viec-va-vong-lap-worker.md) | Hàng đợi việc và vòng lặp worker | BE | M | US-001 | T1-09 |
| [T1-13](T1-13-mo-dun-trich-xuat-pdf-theo-trang.md) | Mô-đun trích xuất PDF theo trang | BE | M | US-001, US-003, US-004 | T0-06 |
| [T1-14](T1-14-mo-dun-cat-chunk-theo-trang.md) | Mô-đun cắt chunk theo trang | BE | S | US-001 | T1-13 |
| [T1-15](T1-15-embedding-va-hoan-tat-viec-nap.md) | Embedding và hoàn tất việc nạp | BE | L | US-001, US-003 | T1-12, T1-13, T1-14, T0-07 |
| [T1-16](T1-16-endpoint-danh-sach-chi-tiet-thu-lai-tai-lieu.md) | Endpoint danh sách, chi tiết, thử lại tài liệu | BE | S | US-003, US-005 | T1-11, T1-15 |
| [T1-17](T1-17-fe-nut-tai-len-va-tien-do.md) | FE: nút tải lên và tiến độ | FE | M | US-001, US-002, US-003 | T0-05, T1-11 |
| [T1-18](T1-18-fe-danh-sach-tai-lieu-trang-thai-loi-trang-thai-trong.md) | FE: danh sách tài liệu, trạng thái, lỗi, trạng thái trống | FE | M | US-001, US-003, US-005 | T1-16, T1-17 |
| [T1-19](T1-19-bang-thong-bao-loi-tai-len-us-004.md) | Bảng thông báo lỗi tải lên (US-004) | FE | S | US-004 | T1-18 |
| [T1-20](T1-20-kiem-thu-tich-hop-luong-nap.md) | Kiểm thử tích hợp luồng nạp | QA | M | US-001, US-002, US-003, US-004, US-005 | T1-15, T1-16 |
| [T1-21](T1-21-kiem-thu-e2e-tai-tai-lieu.md) | Kiểm thử E2E tải tài liệu | QA | S | US-001 | T1-18, T1-19, T1-20 |

## Sprint 2 — Hỏi đáp có nguồn

- Cổng G1 (trước Sprint 2): OQ-006 (kịch bản A/B), OQ-005 sơ bộ, OQ-007. Chưa có thì dùng Kịch bản A với dữ liệu mẫu không nhạy cảm.

| Task | Tên | Loại | Cỡ | Story | Phụ thuộc |
|---|---|---|---|---|---|
| [T2-01](T2-01-migration-hoi-thoai-trich-dan-kiem-toan-su-kien.md) | Migration hội thoại, trích dẫn, kiểm toán, sự kiện | BE | S | US-008 | T1-09 |
| [T2-02](T2-02-mo-dun-truy-xuat.md) | Mô-đun truy xuất | BE | M | US-008, US-009 | T1-15, T2-01 |
| [T2-03](T2-03-cong-sinh-cau-tra-loi-va-adapter-claude.md) | Cổng sinh câu trả lời và adapter Claude | BE | L | US-008 | T0-08, T1-15 |
| [T2-04](T2-04-dieu-phoi-hoi-dap-ba-lop-tu-choi-va-anh-xa-nguon.md) | Điều phối hỏi đáp: ba lớp từ chối và ánh xạ nguồn | BE | L | US-008, US-009, US-011, US-014 | T2-02, T2-03 |
| [T2-05](T2-05-endpoint-hoi-thoai-va-ghi-kiem-toan.md) | Endpoint hội thoại và ghi kiểm toán | BE | M | US-008, US-014 | T2-04, T1-04 |
| [T2-06](T2-06-endpoint-trang-nguon-va-tep-goc.md) | Endpoint trang nguồn và tệp gốc | BE | M | US-015 | T1-16 |
| [T2-07](T2-07-fe-khung-hoi-thoai-va-o-nhap.md) | FE: khung hội thoại và ô nhập | FE | M | US-008 | T1-18, T2-05 |
| [T2-08](T2-08-fe-the-cau-tra-loi-nguon-khong-tim-thay.md) | FE: thẻ câu trả lời, nguồn, "không tìm thấy" | FE | M | US-011, US-014 | T2-07 |
| [T2-09](T2-09-fe-man-hinh-s-03-trinh-xem-nguon.md) | FE: màn hình S-03 Trình xem nguồn | FE | M | US-015 | T2-06, T2-08 |
| [T2-10](T2-10-fe-trang-thai-loi-khi-hoi.md) | FE: trạng thái lỗi khi hỏi | FE | S | US-008 | T2-07 |
| [T2-11](T2-11-su-kien-phan-tich-phia-fe.md) | Sự kiện phân tích phía FE | FE | S | US-014 | T2-08 |
| [T2-12](T2-12-kiem-thu-tich-hop-hoi-dap.md) | Kiểm thử tích hợp hỏi đáp | QA | M | US-008, US-011, US-015 | T2-05, T2-06 |
| [T2-13](T2-13-bo-cau-hoi-chuan-phien-ban-1-va-duong-co-so.md) | Bộ câu hỏi chuẩn phiên bản 1 và đường cơ sở | QA | M | US-008, US-009, US-011, US-012, US-016 | T0-09, T2-05; tập PDF và câu hỏi từ business owner (DEP-001, ASM-005) |
| [T2-14](T2-14-kiem-thu-e2e-hoi-dap.md) | Kiểm thử E2E hỏi đáp | QA | S | US-008 | T2-09, T2-10, T2-12 |

## Sprint 3 — Xóa, phạm vi quyền, kiểm toán, hội thoại

- Cổng G2 (trước Sprint 3): OQ-003, OQ-012. Chưa có thì dùng giá trị tạm: chỉ tài liệu của chính mình; xóa ngay khi worker chạy; lưu bản ghi 365 ngày.

| Task | Tên | Loại | Cỡ | Story | Phụ thuộc |
|---|---|---|---|---|---|
| [T3-01](T3-01-xoa-tai-lieu-endpoint-va-hop-thoai.md) | Xóa tài liệu: endpoint và hộp thoại | BE+FE | M | US-006, US-007 | T1-16, T2-02 |
| [T3-02](T3-02-worker-xoa-vinh-vien.md) | Worker xóa vĩnh viễn | BE | M | US-007 | T3-01, T1-12 |
| [T3-03](T3-03-allowed-document-ids-va-acl.md) | `allowed_document_ids` và ACL | BE | M | US-018 | T1-16, T2-06; G2 |
| [T3-04](T3-04-ban-ghi-kiem-toan-endpoint-va-man-hinh-s-06.md) | Bản ghi kiểm toán: endpoint và màn hình S-06 | BE+FE | M | US-020 | T2-05, T1-07 |
| [T3-05](T3-05-hoi-thoai-lich-su-va-cau-hoi-tiep-theo.md) | Hội thoại: lịch sử và câu hỏi tiếp theo | BE+FE | M | US-010 | T2-05, T2-08 |
| [T3-06](T3-06-do-thoi-gian-han-thoi-gian-cho-va-trang-thai-cho.md) | Đo thời gian, hạn thời gian chờ và trạng thái chờ | BE+FE | M | US-013 | T2-05, T2-07 |
| [T3-07](T3-07-kiem-thu-co-lap-quyen.md) | Kiểm thử cô lập quyền | QA | M | US-018 | T3-03 |
| [T3-08](T3-08-kiem-thu-e2e-xoa-va-kiem-toan.md) | Kiểm thử E2E xóa và kiểm toán | QA | S | US-007, US-020 | T3-01, T3-02, T3-04 |

## Sprint 4 — Chất lượng, đo lường, sẵn sàng phát hành

- Cổng G3 (trước Sprint 4): OQ-002 (ngưỡng), bộ câu hỏi chuẩn đầy đủ.
- Cổng G4 (cuối Sprint 4): tiêu chí launch LG-01..LG-11 đạt, hoặc có quyết định ngoại lệ bằng văn bản của sponsor.

| Task | Tên | Loại | Cỡ | Story | Phụ thuộc |
|---|---|---|---|---|---|
| [T4-01](T4-01-hieu-chinh-va-nghiem-thu-chat-luong.md) | Hiệu chỉnh và nghiệm thu chất lượng | QA+BE | L | US-012, US-016 | T2-13, T3-05; G3 |
| [T4-02](T4-02-bao-cao-muc-su-dung-endpoint-va-s-07.md) | Báo cáo mức sử dụng: endpoint và S-07 | BE+FE | M | US-022, US-023 | T2-05, T1-06 |
| [T4-03](T4-03-danh-gia-cau-tra-loi.md) | Đánh giá câu trả lời | BE+FE | S | US-024 | T2-08 |
| [T4-04](T4-04-health-giam-sat-va-canh-bao.md) | Health, giám sát và cảnh báo | OPS | M | US-021 | T0-04, T3-02 |
| [T4-05](T4-05-ho-so-xu-ly-du-lieu-va-kiem-thu-log-khong-chua-noi-dung.md) | Hồ sơ xử lý dữ liệu và kiểm thử "log không chứa nội dung" | QA+OPS | M | US-019 | T3-02, T3-04; G1 (OQ-005, OQ-006) |
| [T4-06](T4-06-kiem-tra-cong-launch.md) | Kiểm tra cổng launch | QA | M | — | T4-01..T4-05 |
| [T4-07](T4-07-tai-lieu-van-hanh.md) | Tài liệu vận hành | OPS | S | — | T4-04 |
| [T4-08](T4-08-ra-soat-kha-nang-tiep-can-toan-bo.md) | Rà soát khả năng tiếp cận toàn bộ | QA | S | — | T4-02, T4-03 |
