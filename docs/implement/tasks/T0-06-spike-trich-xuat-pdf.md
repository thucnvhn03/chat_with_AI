# T0-06 · Spike trích xuất PDF

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 0 — Nền tảng và spike |
| Story | Nền tảng / nghiệm thu (không gắn riêng một story) |
| Loại việc | SPK |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T0-01; tập PDF mẫu từ business owner (DEP-001; nếu chưa có, dùng PDF công khai không nhạy cảm) |
| Trạng thái | Review (đã chạy trên bộ PDF tổng hợp; chạy lại trên PDF thật DEP-001 trước G0) |

- **Làm gì:** viết script `evaluation/spikes/extract.py` thử `pypdf` và `pdfplumber` trên ít nhất 20 PDF. Đo: tỷ lệ trang có văn bản, lỗi với tiếng Việt (dấu), chất lượng với bảng và nhiều cột, thời gian mỗi trang.
- **Sản phẩm:** `evaluation/spikes/extract.py` và báo cáo `docs/implement/spike_pdf.md` (một đến hai trang): kết luận chọn thư viện, các loại PDF kém, đề xuất giới hạn MVP.
- **Xong khi:** báo cáo nêu rõ chọn thư viện nào và vì sao; nêu tỷ lệ PDF thuộc loại "không có văn bản" để xác nhận ADR-010.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G0 (cuối Sprint 0): chốt bộ công nghệ, DQ-003, kết quả ba spike.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
