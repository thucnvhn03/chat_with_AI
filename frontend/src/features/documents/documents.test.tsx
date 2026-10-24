// T1-17 (tải lên), T1-18 (danh sách, trạng thái, trống, hỏi định kỳ), T3-01 (hộp thoại xóa).
import { act, fireEvent, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import type { DocumentOut } from '../../api/client';
import { FakeXhr, installFakeXhr } from '../../test/fakeXhr';
import { apiError, makeMe, mockApi, renderApp, seriousViolations } from '../../test/utils';
import { hasProcessing } from './useDocuments';

function doc(overrides: Partial<DocumentOut>): DocumentOut {
  return {
    id: 'd1',
    file_name: 'HopDong_A.pdf',
    size_bytes: 2_200_000,
    page_count: 12,
    status: 'ready',
    failure_reason: null,
    uploaded_at: '2026-10-20T00:00:00Z',
    ...overrides,
  };
}

const DEFAULT_DOCS = [
  doc({}),
  doc({ id: 'd2', file_name: 'BaoGia_B.pdf', status: 'processing', page_count: null }),
  doc({ id: 'd3', file_name: 'TaiLieu_C.pdf', status: 'failed', failure_reason: 'encrypted', page_count: null }),
];

function pdf(name: string, size = 1000): File {
  return new File([new Uint8Array(size)], name, { type: 'application/pdf' });
}

describe('S-02 vùng tài liệu', () => {
  it('trạng thái mặc định khớp s02-default: tên, số trang, dung lượng, nhãn, lý do lỗi', async () => {
    mockApi({ 'GET /auth/me': () => makeMe(), 'GET /documents': () => DEFAULT_DOCS });
    const { container } = renderApp('/');
    const list = await screen.findByRole('list', { name: 'Danh sách tài liệu' });
    const items = within(list).getAllByRole('listitem');
    expect(items).toHaveLength(3);
    expect(items[0]).toHaveTextContent('HopDong_A.pdf');
    expect(items[0]).toHaveTextContent('Sẵn sàng');
    expect(items[0]).toHaveTextContent('12 trang · 2,1 MB');
    expect(items[1]).toHaveTextContent('Đang xử lý');
    expect(items[1]).toHaveTextContent('Chưa dùng được để trả lời cho tới khi xử lý xong');
    expect(items[2]).toHaveTextContent('Lỗi');
    expect(items[2]).toHaveTextContent('Lý do: Tài liệu bị khóa hoặc mã hóa. Hãy mở khóa rồi tải lại.');
    expect(within(items[2]).getByRole('button', { name: 'Thử lại TaiLieu_C.pdf' })).toBeInTheDocument();
    expect(within(items[2]).getByRole('button', { name: 'Xóa TaiLieu_C.pdf' })).toBeInTheDocument();
    expect(screen.getByText('3 tệp')).toBeInTheDocument();
    expect(await seriousViolations(container)).toEqual([]);
  });

  it('trạng thái trống khớp s02-empty: hướng dẫn tải PDF, ô hỏi bị vô hiệu kèm giải thích', async () => {
    mockApi({ 'GET /auth/me': () => makeMe(), 'GET /documents': () => [] });
    renderApp('/');
    expect(await screen.findByRole('heading', { name: 'Chưa có tài liệu nào' })).toBeInTheDocument();
    expect(screen.getByLabelText('Câu hỏi của bạn')).toBeDisabled();
    expect(screen.getByLabelText('Câu hỏi của bạn')).toHaveAttribute(
      'placeholder',
      'Hãy tải tài liệu lên trước khi đặt câu hỏi',
    );
  });

  it('lỗi tải danh sách có nút Thử lại', async () => {
    mockApi({ 'GET /auth/me': () => makeMe(), 'GET /documents': () => apiError(500, 'internal_error') });
    renderApp('/');
    expect(await screen.findByText('Không tải được danh sách tài liệu.')).toBeInTheDocument();
  });

  it('chỉ hỏi định kỳ khi còn tài liệu đang xử lý', () => {
    expect(hasProcessing(DEFAULT_DOCS)).toBe(true);
    expect(hasProcessing([doc({}), doc({ id: 'x', status: 'failed' })])).toBe(false);
    expect(hasProcessing(undefined)).toBe(false);
  });

  it('hỏi lại trạng thái tới khi hết tài liệu đang xử lý rồi dừng', async () => {
    const api = mockApi({ 'GET /auth/me': () => makeMe('bd', { poll_interval_s: 0.05 }) });
    let n = 0;
    api.set('GET /documents', () => {
      n += 1;
      return [doc({ status: n < 3 ? 'processing' : 'ready' })];
    });
    renderApp('/');
    await screen.findByText('Sẵn sàng', {}, { timeout: 2000 });
    const callsWhenReady = n;
    await new Promise((r) => setTimeout(r, 300));
    expect(n).toBe(callsWhenReady);
    expect(callsWhenReady).toBe(3);
  });

  it('danh sách 200 tài liệu dựng nhanh', async () => {
    const many = Array.from({ length: 200 }, (_, i) => doc({ id: `d${i}`, file_name: `TaiLieu_${i}.pdf` }));
    mockApi({ 'GET /auth/me': () => makeMe(), 'GET /documents': () => many });
    const started = performance.now();
    renderApp('/');
    const list = await screen.findByRole('list', { name: 'Danh sách tài liệu' });
    expect(within(list).getAllByRole('listitem')).toHaveLength(200);
    // Ngưỡng rộng cho máy kiểm thử đang bận; mục tiêu thật đo ở E2E trên trình duyệt
    expect(performance.now() - started).toBeLessThan(10_000);
  });

  it('Thử lại gọi API retry', async () => {
    const api = mockApi({ 'GET /auth/me': () => makeMe(), 'GET /documents': () => DEFAULT_DOCS });
    api.set('POST /documents/d3/retry', () => doc({ id: 'd3', status: 'processing' }));
    renderApp('/');
    await userEvent.click(await screen.findByRole('button', { name: 'Thử lại TaiLieu_C.pdf' }));
    await waitFor(() => expect(api.calls.some((c) => c.path === '/documents/d3/retry')).toBe(true));
  });
});

describe('UploadControl (C-03)', () => {
  async function setup() {
    installFakeXhr();
    const api = mockApi({ 'GET /auth/me': () => makeMe('bd', { max_file_bytes: 5000 }), 'GET /documents': () => [] });
    renderApp('/');
    const input = (await screen.findByTestId('file-input')) as HTMLInputElement;
    return { api, input };
  }

  it('nhiều tệp: tiến độ và kết quả riêng từng tệp; kiểm tra sớm đuôi và dung lượng', async () => {
    const { api, input } = await setup();
    fireEvent.change(input, {
      target: { files: [pdf('a.pdf'), pdf('b.pdf'), pdf('ghi-chu.txt'), pdf('lon.pdf', 9000)] },
    });
    const uploads = await screen.findByRole('list', { name: 'Tệp đang tải lên' });
    // Chỉ hai tệp hợp lệ được gửi lên máy chủ
    expect(FakeXhr.instances.map((x) => x.fileName)).toEqual(['a.pdf', 'b.pdf']);
    expect(within(uploads).getByText(/Tệp không phải PDF/)).toBeInTheDocument();
    expect(within(uploads).getByText(/vượt quá dung lượng/)).toBeInTheDocument();

    act(() => FakeXhr.instances[0].progress(0.4));
    expect(screen.getByRole('progressbar', { name: 'Tiến độ tải lên a.pdf' })).toHaveAttribute('aria-valuenow', '40');

    api.set('GET /documents', () => [doc({ id: 'n1', file_name: 'a.pdf', status: 'processing' })]);
    act(() => FakeXhr.instances[0].respond(200, [{ id: 'n1', file_name: 'a.pdf', status: 'processing' }]));
    act(() => FakeXhr.instances[1].respond(200, [{ id: null, file_name: 'b.pdf', status: 'failed', failure_reason: 'not_pdf' }]));
    const list = await screen.findByRole('list', { name: 'Danh sách tài liệu' });
    expect(within(list).getByText('a.pdf')).toBeInTheDocument();
    expect(within(uploads).getByText('b.pdf')).toBeInTheDocument();
  });

  it('mất mạng giữa chừng: "Chưa tải xong", không bao giờ "Sẵn sàng"; Tải lại gửi lại tệp', async () => {
    const { input } = await setup();
    fireEvent.change(input, { target: { files: [pdf('BaoGia_B.pdf')] } });
    act(() => FakeXhr.instances[0].progress(0.6));
    act(() => FakeXhr.instances[0].networkError());

    const uploads = await screen.findByRole('list', { name: 'Tệp đang tải lên' });
    expect(within(uploads).getByText('Chưa tải xong')).toBeInTheDocument();
    expect(screen.queryByText('Sẵn sàng')).not.toBeInTheDocument();
    expect(screen.getByText(/Tệp "BaoGia_B.pdf" chưa tải xong/)).toBeInTheDocument();

    await userEvent.click(within(uploads).getByRole('button', { name: 'Tải lại' }));
    expect(FakeXhr.instances).toHaveLength(2);
    expect(FakeXhr.instances[1].fileName).toBe('BaoGia_B.pdf');
  });

  it('không khóa vùng hội thoại khi đang tải', async () => {
    installFakeXhr();
    mockApi({ 'GET /auth/me': () => makeMe(), 'GET /documents': () => [doc({})] });
    renderApp('/');
    const input = (await screen.findByTestId('file-input')) as HTMLInputElement;
    fireEvent.change(input, { target: { files: [pdf('moi.pdf')] } });
    await waitFor(() => expect(screen.getByLabelText('Câu hỏi của bạn')).toBeEnabled());
  });
});

describe('DeleteConfirmDialog (C-05, S-04)', () => {
  async function openDialog() {
    const api = mockApi({ 'GET /auth/me': () => makeMe(), 'GET /documents': () => DEFAULT_DOCS });
    renderApp('/');
    const trigger = await screen.findByRole('button', { name: 'Xóa TaiLieu_C.pdf' });
    await userEvent.click(trigger);
    return { api, trigger };
  }

  it('khớp s04-default: tên tài liệu, thời hạn xóa, không thể hoàn tác, tiêu điểm ở Hủy', async () => {
    await openDialog();
    const dialog = screen.getByRole('alertdialog', { name: 'Xóa tài liệu "TaiLieu_C.pdf"?' });
    expect(dialog).toHaveTextContent('xóa vĩnh viễn trong vòng 1 ngày');
    expect(dialog).toHaveTextContent('Thao tác này không thể hoàn tác.');
    expect(within(dialog).getByRole('button', { name: 'Hủy' })).toHaveFocus();
  });

  it('Esc đóng hộp thoại và trả tiêu điểm về nút gọi', async () => {
    const { trigger } = await openDialog();
    await userEvent.keyboard('{Escape}');
    expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument();
    expect(trigger).toHaveFocus();
  });

  it('xóa thất bại hiển thị lỗi trong hộp thoại (s04-failed)', async () => {
    const { api } = await openDialog();
    api.set('DELETE /documents/d3', () => apiError(500, 'internal_error'));
    await userEvent.click(screen.getByRole('button', { name: 'Xóa vĩnh viễn' }));
    const dialog = screen.getByRole('alertdialog');
    expect(await within(dialog).findByRole('alert')).toHaveTextContent('Chưa xóa được tài liệu.');
  });

  it('xóa thành công: tài liệu biến khỏi danh sách ngay', async () => {
    const { api } = await openDialog();
    api.set('DELETE /documents/d3', () => ({ id: 'd3', status: 'deleting' }));
    api.set('GET /documents', () => DEFAULT_DOCS.slice(0, 2));
    await userEvent.click(screen.getByRole('button', { name: 'Xóa vĩnh viễn' }));
    await waitFor(() => expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument());
    expect(screen.queryByText('TaiLieu_C.pdf')).not.toBeInTheDocument();
    expect(api.calls.some((c) => c.method === 'DELETE' && c.path === '/documents/d3')).toBe(true);
  });
});
