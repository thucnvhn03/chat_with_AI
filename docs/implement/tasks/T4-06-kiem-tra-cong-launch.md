# T4-06 · Kiểm tra cổng launch

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 4 — Chất lượng, đo lường, sẵn sàng phát hành |
| Story | Nền tảng / nghiệm thu (không gắn riêng một story) |
| Loại việc | QA |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T4-01..T4-05 |
| Trạng thái | Done (đã chạy; kết luận: chưa đủ điều kiện phát hành — xem launch_checklist.md) |

- **Làm gì:** chạy từng mục LG-01..LG-11 (`PRD.md` mục 5.1) và ghi kết quả, bằng chứng (đường dẫn báo cáo, ảnh chụp) vào `docs/implement/launch_checklist.md`. Chạy toàn bộ E2E, kiểm thử bảo mật, bộ đánh giá, kiểm tra axe trên mọi màn hình S-01..S-07, kiểm tra các ảnh màn hình chuẩn trong `html_design/screenshots/` so với giao diện thật.
- **Xong khi:** mỗi mục LG có trạng thái Đạt/Không đạt kèm bằng chứng; mục không đạt có người chịu trách nhiệm và hạn.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G3 (trước Sprint 4): OQ-002 (ngưỡng), bộ câu hỏi chuẩn đầy đủ. | Cổng G4 (cuối Sprint 4): tiêu chí launch LG-01..LG-11 đạt, hoặc có quyết định ngoại lệ bằng văn bản của sponsor.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
