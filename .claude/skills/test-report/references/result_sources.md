# Nguồn kết quả kiểm thử và lệnh tạo

Skill không chạy các lệnh này. Đưa lệnh cho người dùng khi thiếu kết quả. Mọi tệp JUnit nên nằm trong `test-results/` (đã có trong `.gitignore`), trừ backend (xem dưới).

| Tầng | Ca liên quan | Tệp kết quả | Lệnh tạo (người dùng tự chạy) | Ghi chú |
|---|---|---|---|---|
| Backend: đơn vị + tích hợp + bảo mật (pytest) | UT, INT-API, SEC, một phần OPS | `backend/test-results/backend.xml` | `docker compose -f deploy/docker-compose.yml up -d postgres objectstore` rồi `scripts/backend-docker.sh pytest -q -p no:cacheprovider --junitxml=test-results/backend.xml` | Container gắn `backend/` vào `/app`, nên tệp nằm trong `backend/test-results/`. Cần Docker — máy 8 GB nên giới hạn WSL (`.wslconfig`) |
| Frontend (Vitest) | UI, ACC, một phần UT, SEC-012 | `test-results/frontend-vitest.xml` | `cd frontend && npx vitest run --reporter=default --reporter=junit --outputFile.junit=../test-results/frontend-vitest.xml` | Không cần Docker, nhẹ |
| E2E (Playwright) | E2E, ACC, UI-001 | `test-results/e2e-playwright.xml` | Dựng stack E2E (`docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.e2e.yml up -d --build`), rồi `cd e2e && PLAYWRIGHT_JUNIT_OUTPUT_NAME=../test-results/e2e-playwright.xml npx playwright test --reporter=list,junit` | Nặng nhất; chạy trên máy đủ tài nguyên hoặc lấy từ CI hằng đêm |
| Bộ đánh giá: công thức chỉ số (pytest) | Hỗ trợ QE | `test-results/evaluation.xml` | `cd evaluation && pytest --junitxml=../test-results/evaluation.xml` | Cần Python (máy hiện tại không có Python cục bộ) |
| Bộ đánh giá: chất lượng câu trả lời | QE-001..QE-008, LG-02..LG-05 | `evaluation/reports/*.json`, `*.md`, `*-review.csv` | Xem `evaluation/README.md` và [10_quality_evaluation/README.md](../../../../docs/testing/test_cases/10_quality_evaluation/README.md) | Chỉ có giá trị cho LG khi chạy với `bge-m3` + Claude và bộ câu hỏi đã duyệt. Tốn phí |
| Luật cảnh báo (promtool) | OPS-002 | Văn bản trên console | `docker run --rm -v "$PWD/deploy/monitoring:/m" --entrypoint promtool prom/prometheus:v3.1.0 test rules /m/alerts_test.yml` | Không có JUnit — ghi kết quả vào `manual_results.csv` |
| CI GitHub Actions | Mọi tầng tự động | Log trên tab Actions; artifact `playwright-report`, `evaluation-report` | — | CI hiện chưa xuất JUnit. Có thể đề xuất thêm `--junitxml` / reporter junit và `upload-artifact` (không tự sửa nếu chưa được yêu cầu) |
| Kiểm thử thủ công | UAT, PERF, ACC-002, OPS, UI-001/002 | `docs/testing/results/manual_results.csv` | — | Cột: `id,status,date,tester,note` |
| Trạng thái launch lần trước | LG-01..LG-11 | `docs/implement/launch_checklist.md` | — | Dùng để so sánh tiến triển, người chịu trách nhiệm, hạn |

## Định dạng JUnit mà script hiểu

- **pytest:** `classname="tests.integration.test_auth"`, `name="test_login_me_logout"` (tham số hóa: `name="test_x[...]"` → khớp theo `test_x`).
- **Vitest:** `classname="src/features/chat/chat.test.tsx"`, `name="<describe> > <tiêu đề>"`.
- **Playwright:** `classname` là đường dẫn tệp spec, `name` chứa tiêu đề kiểm thử; ca tham chiếu bằng `auth.spec.ts: "đăng nhập đúng"` được khớp khi tên chứa chuỗi trong ngoặc kép.

Có `<failure>` hoặc `<error>` → lỗi; có `<skipped>` → bỏ qua; còn lại → đạt.
