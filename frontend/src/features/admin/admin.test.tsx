// T1-07 (S-05 quản lý quyền) và T3-04 (S-06 bản ghi kiểm toán).
import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import type { GrantOut } from '../../api/client';
import { apiError, makeMe, mockApi, renderApp, seriousViolations } from '../../test/utils';

const ADMIN = { ...makeMe('security_admin'), user: { id: 'admin-id', login: 'quan.tri', display_name: null } };

function grant(login: string, role: string, id = login): GrantOut {
  return { user_id: id, login, display_name: null, role, status: 'active', granted_at: '2026-10-01T00:00:00Z', revoked_at: null };
}

describe('S-05 Quản lý quyền', () => {
  it('s05-default: bảng người dùng, cột phạm vi [OQ-003], không vi phạm axe', async () => {
    mockApi({
      'GET /auth/me': () => ADMIN,
      'GET /admin/access': () => [grant('quan.tri', 'security_admin', 'admin-id'), grant('user01', 'bd'), grant('user03', 'manager')],
    });
    const { container } = renderApp('/admin/access');
    const table = await screen.findByRole('table');
    const rows = within(table).getAllByRole('row').slice(1);
    expect(rows).toHaveLength(3);
    expect(rows[1]).toHaveTextContent('user01Nhân sự BDOQ-003');
    expect(rows[2]).toHaveTextContent('Không áp dụng');
    // Không tự thu hồi quyền của chính mình
    expect(within(rows[0]).queryByRole('button')).toBeNull();
    expect(screen.getByRole('link', { name: 'Quản lý quyền' })).toHaveAttribute('aria-current', 'page');
    expect(await seriousViolations(container)).toEqual([]);
  });

  it('s05-empty: trạng thái trống', async () => {
    mockApi({ 'GET /auth/me': () => ADMIN, 'GET /admin/access': () => [] });
    renderApp('/admin/access');
    expect(await screen.findByRole('heading', { name: 'Chưa có người dùng nào được cấp quyền' })).toBeInTheDocument();
  });

  it('cấp quyền gọi API với tên đăng nhập và vai trò', async () => {
    const api = mockApi({ 'GET /auth/me': () => ADMIN, 'GET /admin/access': () => [] });
    api.set('POST /admin/access', (body) => grant((body as { login: string }).login, (body as { role: string }).role));
    renderApp('/admin/access');
    await userEvent.type(await screen.findByLabelText('Tên đăng nhập'), 'moi.nguoi');
    await userEvent.selectOptions(screen.getByLabelText('Vai trò'), 'manager');
    await userEvent.click(screen.getByRole('button', { name: 'Cấp quyền' }));
    expect(await screen.findByText('Đã cấp vai trò Quản lý cho "moi.nguoi".')).toBeInTheDocument();
    expect(api.calls.find((c) => c.method === 'POST')?.body).toEqual({ login: 'moi.nguoi', role: 'manager' });
  });

  it('bỏ trống tên đăng nhập: báo lỗi tại trường, không gọi API', async () => {
    const api = mockApi({ 'GET /auth/me': () => ADMIN, 'GET /admin/access': () => [] });
    renderApp('/admin/access');
    await userEvent.click(await screen.findByRole('button', { name: 'Cấp quyền' }));
    expect(screen.getByRole('alert')).toHaveTextContent('Hãy nhập tên đăng nhập.');
    expect(api.calls.some((c) => c.method === 'POST')).toBe(false);
  });

  it('s05-confirm: thu hồi phải qua bước xác nhận', async () => {
    const api = mockApi({ 'GET /auth/me': () => ADMIN, 'GET /admin/access': () => [grant('user02', 'bd')] });
    api.set('DELETE /admin/access/user02', () => undefined);
    renderApp('/admin/access');
    await userEvent.click(await screen.findByRole('button', { name: 'Thu hồi quyền của user02' }));
    const banner = screen.getByRole('alert');
    expect(banner).toHaveTextContent('Thu hồi quyền của "user02"?');
    expect(api.calls.some((c) => c.method === 'DELETE')).toBe(false);

    await userEvent.click(within(banner).getByRole('button', { name: 'Hủy' }));
    expect(screen.queryByText('Thu hồi quyền của "user02"?')).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: 'Thu hồi quyền của user02' }));
    await userEvent.click(within(screen.getByRole('alert')).getByRole('button', { name: 'Thu hồi' }));
    await waitFor(() => expect(api.calls.some((c) => c.method === 'DELETE' && c.path === '/admin/access/user02')).toBe(true));
    expect(await screen.findByText('Đã thu hồi quyền của "user02".')).toBeInTheDocument();
  });
});

describe('S-06 Bản ghi kiểm toán', () => {
  const PAGE = {
    items: [
      { id: 3, at: '2026-10-21T08:30:00Z', user: { id: 'u1', login: 'user01' }, documents: [{ id: 'd1', file_name: 'HopDong_A.pdf' }, { id: 'd2', file_name: 'BaoGia_B.pdf' }] },
      { id: 2, at: '2026-10-21T08:00:00Z', user: { id: 'u2', login: 'user02' }, documents: [{ id: 'd9', file_name: null }] },
    ],
    next_cursor: '2',
  };

  it('s06-default: bảng thời điểm, người dùng, tài liệu; xem thêm theo con trỏ; không vi phạm axe', async () => {
    const api = mockApi({ 'GET /auth/me': () => ADMIN });
    api.set('GET /admin/audit', (_b, url) =>
      url.searchParams.get('cursor') === '2'
        ? { items: [{ id: 1, at: '2026-10-20T08:00:00Z', user: { id: 'u1', login: 'user01' }, documents: [] }], next_cursor: null }
        : PAGE,
    );
    const { container } = renderApp('/admin/audit');
    const table = await screen.findByRole('table');
    const rows = within(table).getAllByRole('row').slice(1);
    expect(rows[0]).toHaveTextContent('user01');
    expect(rows[0]).toHaveTextContent('HopDong_A.pdf; BaoGia_B.pdf');
    expect(rows[1]).toHaveTextContent('Tài liệu đã xóa');
    expect(await seriousViolations(container)).toEqual([]);
    await userEvent.click(screen.getByRole('button', { name: 'Xem thêm bản ghi' }));
    await waitFor(() => expect(within(table).getAllByRole('row')).toHaveLength(4));
    expect(screen.queryByRole('button', { name: 'Xem thêm bản ghi' })).not.toBeInTheDocument();
  });

  it('bộ lọc gửi đúng tham số', async () => {
    const api = mockApi({ 'GET /auth/me': () => ADMIN, 'GET /admin/audit': () => ({ items: [], next_cursor: null }) });
    renderApp('/admin/audit');
    await screen.findByRole('heading', { name: 'Không có bản ghi trong khoảng đã chọn' });
    await userEvent.type(screen.getByLabelText('Người dùng'), 'user01');
    await userEvent.type(screen.getByLabelText('Tài liệu'), 'HopDong');
    await userEvent.click(screen.getByRole('button', { name: 'Lọc' }));
    await waitFor(() => {
      const last = api.calls.filter((c) => c.path === '/admin/audit').length;
      expect(last).toBeGreaterThanOrEqual(2);
    });
    const fetchMock = globalThis.fetch as unknown as { mock: { calls: [string][] } };
    const urls = fetchMock.mock.calls.map((c) => String(c[0])).filter((u) => u.includes('/admin/audit'));
    expect(urls[urls.length - 1]).toContain('user=user01');
    expect(urls[urls.length - 1]).toContain('document=HopDong');
  });

  it('s06-empty và s06-error (có Thử lại)', async () => {
    const api = mockApi({ 'GET /auth/me': () => ADMIN, 'GET /admin/audit': () => apiError(500, 'internal_error') });
    renderApp('/admin/audit');
    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('Không tải được bản ghi kiểm toán.');
    api.set('GET /admin/audit', () => ({ items: [], next_cursor: null }));
    await userEvent.click(within(alert).getByRole('button', { name: 'Thử lại' }));
    expect(await screen.findByRole('heading', { name: 'Không có bản ghi trong khoảng đã chọn' })).toBeInTheDocument();
  });
});
