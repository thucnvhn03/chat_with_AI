// T2-09: S-03 trình xem nguồn — trang đúng, tô sáng đoạn trích, chuyển trang, tài liệu đã xóa.
import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { apiError, makeMe, mockApi, renderApp, seriousViolations } from '../../test/utils';
import { findHighlight } from './highlight';

const CITATIONS = [
  { document_id: 'd1', document_name: 'HopDong_A.pdf', page: 5, cited_text: 'Đợt một được thanh toán trong   30 ngày' },
  { document_id: 'd2', document_name: 'BaoGia_B.pdf', page: 2, cited_text: 'đợt hai' },
];

function page(n: number, text: string) {
  return { page: n, page_count: 12, text, document_name: 'HopDong_A.pdf' };
}

describe('findHighlight', () => {
  it('khớp linh hoạt khoảng trắng và ngắt dòng', () => {
    const h = findHighlight('5.1 Mở đầu.\nĐợt một được thanh\ntoán trong 30 ngày kể từ ngày ký.', CITATIONS[0].cited_text);
    expect(h?.match).toBe('Đợt một được thanh\ntoán trong 30 ngày');
    expect(h?.before).toBe('5.1 Mở đầu.\n');
  });

  it('không tìm thấy hoặc rỗng → không tô sáng', () => {
    expect(findHighlight('Văn bản trang', 'không có ở đây')).toBeNull();
    expect(findHighlight('Văn bản (đặc biệt) [x]', '')).toBeNull();
    expect(findHighlight('Giá (đã gồm VAT) là 12 triệu', '(đã gồm VAT)')?.match).toBe('(đã gồm VAT)');
  });
});

describe('S-03 Trình xem nguồn', () => {
  it('s03-default: "Trang N / M", tô sáng đoạn trích, cột nguồn, không vi phạm axe', async () => {
    mockApi({
      'GET /auth/me': () => makeMe(),
      'GET /documents/d1/pages/5': () => page(5, 'Điều 5. Thanh toán.\nĐợt một được thanh toán trong 30 ngày kể từ ngày ký.'),
    });
    const { container } = renderApp('/sources/d1?page=5', { citations: CITATIONS, active: CITATIONS[0] });
    expect(await screen.findByText('Trang 5 / 12')).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 1, name: 'HopDong_A.pdf' })).toBeInTheDocument();
    const mark = container.querySelector('mark.hit');
    expect(mark).toHaveTextContent('Đợt một được thanh toán trong 30 ngày');
    const sources = screen.getByRole('complementary', { name: 'Nguồn của câu trả lời' });
    const links = within(sources).getAllByRole('link');
    expect(links[0]).toHaveAttribute('aria-current', 'true');
    expect(links[1]).not.toHaveAttribute('aria-current');
    expect(await seriousViolations(container)).toEqual([]);
  });

  it('đoạn trích không có trong trang: hiển thị trang, không tô sáng, không báo lỗi', async () => {
    mockApi({ 'GET /auth/me': () => makeMe(), 'GET /documents/d1/pages/5': () => page(5, 'Nội dung khác hẳn.') });
    const { container } = renderApp('/sources/d1?page=5', { citations: CITATIONS });
    expect(await screen.findByText('Nội dung khác hẳn.')).toBeInTheDocument();
    expect(container.querySelector('mark')).toBeNull();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('chuyển trang không tải lại toàn bộ ứng dụng', async () => {
    const api = mockApi({
      'GET /auth/me': () => makeMe(),
      'GET /documents/d1/pages/5': () => page(5, 'Trang năm'),
      'GET /documents/d1/pages/6': () => page(6, 'Trang sáu'),
    });
    renderApp('/sources/d1?page=5', { citations: CITATIONS });
    await screen.findByText('Trang năm');
    await userEvent.click(screen.getByRole('button', { name: 'Trang sau' }));
    expect(await screen.findByText('Trang sáu')).toBeInTheDocument();
    expect(screen.getByText('Trang 6 / 12')).toBeInTheDocument();
    expect(api.calls.filter((c) => c.path === '/auth/me')).toHaveLength(1);
    await userEvent.click(screen.getByRole('button', { name: 'Trang trước' }));
    await waitFor(() => expect(screen.getByText('Trang 5 / 12')).toBeInTheDocument());
  });

  it('s03-deleted: tài liệu đã bị xóa khi API trả 404', async () => {
    mockApi({ 'GET /auth/me': () => makeMe(), 'GET /documents/d1/pages/5': () => apiError(404, 'document_not_found') });
    renderApp('/sources/d1?page=5', { citations: CITATIONS });
    expect(await screen.findByRole('heading', { name: 'Tài liệu này đã bị xóa' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Quay lại hội thoại' })).toHaveAttribute('href', '/');
    expect(screen.queryByText(/Trang \d+ \//)).not.toBeInTheDocument();
  });
});
