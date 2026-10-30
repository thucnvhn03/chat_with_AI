---
name: test-report
description: Lập Báo cáo tổng kết kiểm thử (Test Summary Report, IEEE 829) cho dự án "Chat với tài liệu" từ kết quả kiểm thử có sẵn — JUnit XML của pytest/Vitest/Playwright, báo cáo bộ đánh giá trong evaluation/reports, kết quả kiểm thử thủ công — gắn vào 149 ca trong docs/testing/test_cases và đối chiếu tiêu chí launch LG-01..LG-11 của Master Test Plan. Dùng skill này mỗi khi người dùng muốn báo cáo kiểm thử, test report, tổng kết kết quả test, báo cáo QA, báo cáo cho cổng G4 / sprint / phát hành, hỏi "đã đạt bao nhiêu ca", "dự án đủ điều kiện phát hành chưa", hoặc muốn cập nhật docs/testing/Test_Summary_Report.md — kể cả khi họ không nói chữ "report".
---

# Báo cáo tổng kết kiểm thử — "Chat với tài liệu"

Skill này biến kết quả kiểm thử **đã có** thành báo cáo tổng kết theo IEEE 829-2008, có truy vết tới từng ca kiểm thử và tiêu chí launch. Người đọc báo cáo (sponsor, business owner, trưởng nhóm, QA) dùng nó để quyết định phát hành, nên giá trị của báo cáo nằm ở chỗ **mỗi kết luận đều có bằng chứng** và những gì chưa biết được nói rõ là chưa biết.

## Ranh giới: chỉ đọc kết quả, không chạy kiểm thử

Không tự chạy pytest, Vitest, Playwright, Docker hay bộ đánh giá. Máy phát triển của dự án từng bị reset khi chạy tải Docker nặng, và bộ đánh giá với Claude tốn phí. Nếu thiếu kết quả, đưa người dùng lệnh trong [references/result_sources.md](references/result_sources.md) để họ tự chạy, rồi lập báo cáo với phần còn thiếu được đánh dấu "Chưa có kết quả". Được phép chạy `node` cho script tổng hợp bên dưới vì nó chỉ đọc tệp.

## Quy trình

### 1. Xác định phạm vi báo cáo

Hỏi ngắn (hoặc suy ra từ yêu cầu): báo cáo cho mốc nào — sprint N, cổng G4/phát hành, hay một đợt kiểm thử cụ thể (ví dụ chỉ bảo mật). Mặc định: báo cáo toàn bộ cho cổng phát hành. Ghi lại phiên bản mã: `git rev-parse --short HEAD` và `git status --short` (có thay đổi chưa commit thì ghi rõ).

### 2. Tìm kết quả có sẵn

Tìm ở các vị trí trong [references/result_sources.md](references/result_sources.md): `test-results/`, `backend/test-results/`, `evaluation/reports/`, `docs/testing/results/manual_results.csv`, `e2e/playwright-report/`, `docs/implement/launch_checklist.md`, kết quả CI do người dùng dán vào.

Với mỗi nguồn, ghi thời điểm tạo. Kết quả cũ hơn commit gần nhất có thay đổi mã liên quan thì vẫn dùng được nhưng phải ghi "kết quả trước commit X" — người ra quyết định cần biết số liệu có còn phản ánh mã hiện tại không.

Nếu không có JUnit XML nào: dừng lại, nói với người dùng còn thiếu gì và đưa lệnh tạo. Chỉ lập báo cáo từ nguồn văn bản (launch_checklist, Phụ lục 2 của Master Test Plan) khi người dùng đồng ý, và ghi rõ trong báo cáo rằng số liệu lấy từ tài liệu, không từ tệp kết quả.

### 3. Chạy script tổng hợp

```bash
node .claude/skills/test-report/scripts/collect_results.mjs \
  --results test-results,backend/test-results \
  --eval evaluation/reports \
  --manual docs/testing/results/manual_results.csv \
  --out test-results/summary
```

Script đọc cột "Tự động hóa" / "Ca chi tiết" của từng ca, khớp với tên kiểm thử trong JUnit, và ghi `summary.md` + `summary.json` gồm: nguồn kết quả, trạng thái ca theo nhóm, kiểm thử lỗi, trạng thái từng ca, chỉ số bộ đánh giá, và **kiểm thử chưa gắn với ca nào** (lỗ hổng truy vết). Đọc `summary.json` thay vì tự đếm — đếm tay 149 ca dễ sai.

Trạng thái script gán:

| Trạng thái | Nghĩa |
|---|---|
| Đạt | Mọi kiểm thử tự động được tham chiếu có kết quả và đạt (hoặc mọi ca phụ thuộc đạt, với nhóm 09_api) |
| Không đạt | Có ít nhất một kiểm thử tham chiếu lỗi, hoặc ca phụ thuộc không đạt |
| Bỏ qua | Có kiểm thử tham chiếu bị skip toàn bộ — chưa đủ để kết luận Đạt |
| Chưa có kết quả | Ca có kiểm thử tự động nhưng không tìm thấy trong tệp kết quả (tầng đó chưa chạy, hoặc tên kiểm thử đã đổi) |
| Thủ công — chưa ghi nhận | Ca thủ công chưa có dòng trong `manual_results.csv` |

Script khớp theo tên, nên nó có thể sai ở hai chỗ; kiểm tra lại trước khi viết:
- "Chưa có kết quả" mà tầng đó đã chạy → có thể tên kiểm thử trong tệp ca đã cũ. Báo đây là lỗi truy vết cần sửa trong tệp ca, đừng tự đổi thành Đạt.
- Ca có ghi chú "phần thủ công chưa ghi nhận" → phần tự động đạt nhưng ca chưa hoàn tất; ghi đúng như vậy.

### 4. Đánh giá theo tiêu chí

Đọc Master Test Plan mục 7 (tiêu chí đạt/không đạt, LG-01..LG-11), mục 6.2 (mức độ lỗi), mục 8 (tạm dừng), Phụ lục 1 (truy vết), và `docs/implement/launch_checklist.md` (trạng thái LG lần trước, người chịu trách nhiệm).

Với từng LG, kết luận một trong: **Đạt**, **Không đạt**, **Chưa kết luận** (thiếu dữ liệu hoặc ngưỡng còn [TBD]), **Ngoại lệ** (có quyết định bằng văn bản của sponsor). Những điểm dễ kết luận sai:

- Ngưỡng còn `[TBD: OQ-002]` → chỉ báo số đo được, kết luận "Chưa kết luận". Không tự đặt ngưỡng.
- Báo cáo bộ đánh giá có `config_note` chứa `hash`/`fake` (embedding hoặc adapter giả lập) → đó là kiểm chứng luồng, **không phải số liệu chất lượng**; không dùng cho LG-02..LG-05.
- LG-06 (bảo mật xác nhận bằng văn bản), LG-10 (bộ câu hỏi và PDF thật), LG-11 (OQ đã chốt) cần bằng chứng từ con người — không suy ra từ kiểm thử tự động.
- Kiểm thử lỗi: phân loại mức độ theo bảng ở Master Test Plan mục 6.2, dựa vào ca bị ảnh hưởng (ca Cao về xóa/cô lập/nguồn → thường Nghiêm trọng hoặc Cao). Nêu căn cứ phân loại.

Kết luận chung là một trong: **Đủ điều kiện phát hành**, **Đủ điều kiện có điều kiện** (liệt kê điều kiện), **Chưa đủ điều kiện**. Khi còn bất kỳ LG nào "Không đạt" hoặc "Chưa kết luận" mà không có ngoại lệ, kết luận không thể là "Đủ điều kiện".

### 5. Viết báo cáo

Dùng mẫu trong [references/report_template.md](references/report_template.md). Lưu vào `docs/testing/Test_Summary_Report.md` (vị trí đã định trong Master Test Plan mục 9). Nếu tệp đã tồn tại: đọc trước, giữ bảng lịch sử phiên bản và thêm dòng mới; nội dung chính thay bằng kết quả mới. Báo cáo cho một sprint/đợt riêng thì lưu `docs/testing/reports/TSR-<mốc>-<YYYYMMDD>.md`.

Viết bằng tiếng Việt, câu ngắn, có số cụ thể. Người đọc chính là sponsor và business owner — mục "Tóm tắt" phải đọc hiểu được mà không cần đọc phần còn lại. Danh sách 149 ca đầy đủ đặt ở phụ lục (lấy từ `summary.md`), không đặt ở thân báo cáo.

### 6. Trả lời người dùng

Một dòng nêu người đọc báo cáo, đường dẫn tệp, kết luận chung, số ca theo trạng thái, các LG chưa đạt, và những nguồn kết quả còn thiếu cùng lệnh để tạo. Không commit trừ khi được yêu cầu.

## Kết quả thủ công

Ca thủ công (UAT, ACC với trình đọc màn hình, OPS, PERF…) được ghi vào `docs/testing/results/manual_results.csv`:

```csv
id,status,date,tester,note
UAT-001,Đạt,2026-11-02,Nguyễn Văn A (BD),"20 PDF thật, 0 lỗi"
ACC-002,Không đạt,2026-11-03,QA,"VoiceOver không đọc tiến độ tải lên — BUG-012"
```

`status` dùng: Đạt, Không đạt, Bị chặn, Chưa chạy. Nếu người dùng kể kết quả thủ công trong hội thoại, đề nghị ghi vào tệp này (có người thực hiện và ngày) thay vì chỉ đưa vào báo cáo — để lần báo cáo sau còn bằng chứng.
