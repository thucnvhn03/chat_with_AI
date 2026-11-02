---
name: test-run
description: Chạy kiểm thử tự động của dự án "Chat với tài liệu" (Vitest, pytest backend, Playwright E2E, công thức bộ đánh giá, promtool) tuần tự và an toàn cho máy ít RAM, rồi lập hồ sơ kết quả trong docs/testing/results/run-<ngày>/ — kết quả chi tiết từng ca trong 149 ca của docs/testing/test_cases, checklist kết quả mong đợi, ảnh kết quả của từng ca, ảnh giao diện thật của ca E2E. Dùng skill này khi người dùng muốn chạy test, chạy lại kiểm thử, "chạy các test case", kiểm thử hồi quy trước khi merge/phát hành, cần bằng chứng kiểm thử, ảnh kết quả test, checklist từng ca, hoặc muốn biết mã hiện tại có còn đạt không. Nếu người dùng chỉ cần báo cáo tổng kết (IEEE 829, cổng G4, LG-01..LG-11) từ kết quả đã có, dùng skill test-report; skill này tạo ra kết quả mà test-report đọc.
---

# Chạy kiểm thử và lập hồ sơ kết quả — "Chat với tài liệu"

Skill này chạy kiểm thử thật rồi biến kết quả thành hồ sơ mà QA và trưởng nhóm đọc được theo từng ca: ca nào đạt, đạt nhờ kiểm thử nào, mục kết quả mong đợi nào đã được chứng minh, ảnh chụp ra sao. Giá trị của hồ sơ nằm ở chỗ **không đánh dấu điều chưa chứng minh** — một checklist "xanh toàn bộ" mà sai còn tệ hơn checklist còn ô trống.

Skill [test-report](../test-report/SKILL.md) đọc kết quả do skill này tạo để lập Báo cáo tổng kết (IEEE 829). Skill này dùng lại script `collect_results.mjs` của test-report để khớp kiểm thử với ca, nên hai bên luôn cùng một cách đếm.

## Ranh giới

- **Không gọi Claude thật, không chạy bộ đánh giá chất lượng câu trả lời** (`evaluation/run_eval.py` với `bge-m3` + Claude) — tốn phí. Chỉ làm khi người dùng yêu cầu rõ, và khi đó theo `evaluation/README.md`.
- **Chạy tuần tự, không chạy song song các tầng Docker.** Máy phát triển có ~3,8 GB RAM cho Docker và từng bị reset khi tải nặng. `run_layers.sh` đã tuần tự sẵn; đừng mở thêm lệnh Docker nặng trong lúc nó chạy.
- **Không tự `--build` ảnh Docker** khi script báo ảnh cũ hoặc thiếu — build tốn vài phút và nhiều RAM. Báo người dùng và hỏi trước.
- **Không commit.** Hồ sơ là tệp mới trong `docs/testing/results/`; người dùng tự quyết định commit.
- Ca thủ công chỉ ghi vào `manual_results.csv` khi thực sự đã kiểm (người dùng kể lại, hoặc bạn tự kiểm được bằng lệnh đọc — ví dụ tìm khóa API trong mã). Ghi đúng người thực hiện là ai.

## Quy trình

### 1. Xác định phạm vi

Suy ra từ yêu cầu; mặc định `all`. Tầng và thời gian tham khảo (máy 2 CPU):

| Tầng | Cần | Thời gian | Ca được gắn |
|---|---|---|---|
| `frontend` | Node (không cần Docker) | ~1,5 phút | UI, ACC, một phần UT/SEC |
| `backend` | Docker: postgres, objectstore, ảnh `cwd-backend-dev` | ~6–14 phút | UT, INT-API, SEC, OPS, API (qua phụ thuộc) |
| `e2e` | Docker: stack E2E đã build, cổng 5173 | ~6 phút | E2E, ACC, UI-001, PERF-005 |
| `eval` | Ảnh `cwd-backend-dev` (máy không có Python cục bộ) | <10 giây | UT-022 |
| `alerts` | Ảnh `prom/prometheus:v3.1.0` | <5 giây | OPS-002 (bằng chứng ngoài JUnit) |

Người dùng hỏi một nhóm cụ thể ("chạy test bảo mật") → chạy tầng chứa nhóm đó (bảo mật → `backend frontend`).

### 2. Chuẩn bị Docker (nếu cần)

`docker info` lỗi → Docker Desktop chưa chạy. Trên Windows mở bằng PowerShell `Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"`, rồi chờ `docker info` thành công (vòng lặp kiểm tra tối đa ~2,5 phút). Chạy `frontend` trước trong lúc chờ Docker khởi động — tầng này không cần Docker.

### 3. Chạy

```bash
.claude/skills/test-run/scripts/run_layers.sh all
# hoặc từng phần, cùng ngày sẽ gộp vào cùng một thư mục test-results/run-<ngày>/:
.claude/skills/test-run/scripts/run_layers.sh frontend
.claude/skills/test-run/scripts/run_layers.sh backend e2e eval alerts
```

Lệnh `all` mất ~15–25 phút, vượt giới hạn 10 phút của một lệnh Bash: chạy với `run_in_background`, rồi chờ thông báo hoàn tất (Monitor với vòng `until` nếu cần). Tốt hơn: chạy `frontend` ở tiền cảnh, phần Docker ở nền.

Mã thoát: `0` mọi tầng đạt · `1` có kiểm thử lỗi (vẫn lập hồ sơ — lỗi phải hiện trong hồ sơ) · `3` môi trường chưa sẵn sàng (đọc thông báo `[test-run]`, xử lý theo [references/troubleshooting.md](references/troubleshooting.md)). Script tự dừng container khi xong (`--keep-up` để giữ).

Script ghi vào `test-results/<run>/`: JUnit XML, log từng tầng, `e2e-playwright.json` (ảnh đính kèm), `run-meta.json` (commit, nhánh, thay đổi chưa commit, Docker, thời gian, mã thoát từng tầng).

### 4. Lập hồ sơ

```bash
node .claude/skills/test-run/scripts/build_run_docs.mjs            # lần chạy mới nhất
node .claude/skills/test-run/scripts/build_run_docs.mjs --run run-2026-11-02
```

Script gọi `collect_results.mjs`, rồi ghi vào `docs/testing/results/<run>/`:

| Tệp | Nội dung |
|---|---|
| `README.md` | Phiên bản mã, môi trường, bảng tầng, bảng nhóm ca, checklist chung, ảnh từng tầng, ca còn chờ thủ công, kiểm thử chưa gắn ca, cách chạy lại |
| `<nhóm>.md` (11 tệp) | Từng ca: trạng thái, mục tiêu, truy vết, **checklist kết quả mong đợi**, kiểm thử đã chạy (✓/✗, thời gian), căn cứ, **ảnh kết quả** |
| `screenshots/ca/<Mã ca>.png` | Ảnh kết quả của từng ca (dựng từ JUnit) |
| `screenshots/ket-qua/<tầng>.png` | Danh sách kiểm thử của từng tầng |
| `screenshots/e2e/`, `screenshots/man-hinh/` | Ảnh giao diện thật của ca E2E; màn hình S-01..S-07 |
| `*.xml`, `*.log`, `tong-hop-summary.md` | Bằng chứng gốc |

README được sinh lại mỗi lần. Ghi chú viết tay (sai khác môi trường, việc đã kiểm thủ công, giải thích lỗi) đặt trong `docs/testing/results/<run>/NOTES.md` — script chèn nó vào README thành mục "Ghi chú của người chạy".

Cách đánh dấu checklist (script làm sẵn; kiểm lại khi đọc):
- `[x]` khi ca Đạt nhờ kiểm thử tự động, hoặc dòng của bảng tương tác có tệp kiểm thử chạy đạt toàn bộ, hoặc kết quả thủ công đã ghi.
- Để trống khi: ca thủ công chưa ghi nhận; mục chứa `[TBD`; ca "phần tự động đạt, phần thủ công chưa ghi nhận" (tiêu đề ca ghi rõ điều này).

### 5. Kiểm tra trước khi báo

Mở và nhìn (Read) ít nhất: một ảnh ca Đạt có nhiều kiểm thử, một ảnh ca thủ công, hai ảnh E2E bất kỳ — ảnh E2E có đúng nội dung tên ca không (ảnh trùng hoặc lệch ca là lỗi thường gặp, xem troubleshooting). Đọc README mục 1 và 3.

Nếu có kiểm thử lỗi: đọc log tầng đó, tìm nguyên nhân gần nhất (lỗi mã, lỗi môi trường, kiểm thử chập chờn). Lỗi môi trường (cổng, hết thời gian chờ, RAM) → chạy lại riêng tầng đó một lần trước khi kết luận lỗi mã. Ghi phân tích vào `NOTES.md` rồi chạy lại `build_run_docs.mjs`.

"Chưa có kết quả" ở ca có kiểm thử tự động mà tầng đã chạy → tên kiểm thử trong tệp ca đã cũ (lỗi truy vết). Báo người dùng, không tự sửa trạng thái.

### 6. Trả lời người dùng

Ngắn gọn: tổng kiểm thử đạt/lỗi/bỏ qua theo tầng; số ca theo trạng thái; ca lỗi (nếu có) và nguyên nhân; ca còn chờ thủ công; đường dẫn `docs/testing/results/<run>/README.md`; những gì đã thay đổi ngoài thư mục hồ sơ (`screenshots.spec.ts` ghi đè ảnh trong `docs/implement/evidence/screenshots/`; dòng mới trong `manual_results.csv`). Đề nghị chạy skill test-report nếu người dùng cần báo cáo cho cổng phát hành.

## Ghi kết quả thủ công

Khi người dùng kể kết quả kiểm thử thủ công, thêm dòng vào `docs/testing/results/manual_results.csv` rồi chạy lại `build_run_docs.mjs` — ca chuyển trạng thái và checklist được đánh dấu:

```csv
id,status,date,tester,note
UAT-001,Đạt,2026-11-05,Nguyễn Văn A (BD),"10 PDF thật, tất cả Sẵn sàng"
```

`status`: Đạt, Không đạt, Bị chặn, Chưa chạy.
