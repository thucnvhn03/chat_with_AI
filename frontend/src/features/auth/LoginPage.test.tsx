// T1-06: S-01 bốn trạng thái, điều hướng theo vai trò, AuthGate (401 → /login giữ câu hỏi).
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { DRAFT_KEY } from '../../app/storage';
import { apiError, makeMe, mockApi, renderApp, seriousViolations } from '../../test/utils';

async function submit(login = 'an.nguyen', password = 'mat-khau') {
  const user = userEvent.setup();
  await user.type(screen.getByLabelText('Tên đăng nhập'), login);
  await user.type(screen.getByLabelText('Mật khẩu'), password);
  await user.click(screen.getByRole('button', { name: 'Đăng nhập' }));
}

describe('S-01 Đăng nhập', () => {
  it('mặc định: biểu mẫu, không có thông báo lỗi, không vi phạm axe', async () => {
    mockApi({});
    const { container } = renderApp('/login');
    expect(screen.getByRole('heading', { name: 'Đăng nhập' })).toBeInTheDocument();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    expect(await seriousViolations(container)).toEqual([]);
  });

  it('sai thông tin: thông báo chung, không phân biệt sai tên hay sai mật khẩu', async () => {
    mockApi({ 'POST /auth/login': () => apiError(401, 'invalid_credentials') });
    renderApp('/login');
    await submit();
    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Tên đăng nhập hoặc mật khẩu chưa đúng.',
    );
    expect(screen.getByLabelText('Mật khẩu')).toHaveValue('');
  });

  it('không có quyền (403 no_access)', async () => {
    mockApi({ 'POST /auth/login': () => apiError(403, 'no_access') });
    renderApp('/login');
    await submit();
    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Tài khoản này chưa được cấp quyền sử dụng ứng dụng.',
    );
  });

  it('hết phiên: thông báo khi bị đưa về từ một yêu cầu 401', async () => {
    mockApi({ 'GET /auth/me': () => apiError(401, 'session_expired') });
    renderApp('/login', { notice: { reason: 'expired' } });
    expect(await screen.findByRole('alert')).toHaveTextContent('Phiên làm việc đã hết hạn.');
  });

  it.each([
    ['bd', 'Tài liệu của tôi'],
    ['security_admin', 'Quản lý quyền sử dụng'],
    ['manager', 'Báo cáo mức sử dụng'],
  ] as const)('đăng nhập vai trò %s đưa tới đúng màn hình', async (role, heading) => {
    mockApi({
      'POST /auth/login': () => makeMe(role),
      'GET /auth/me': () => makeMe(role),
      'GET /documents': () => [],
      'GET /admin/access': () => [],
      'GET /reports/usage': () => ({ weeks: [] }),
    });
    renderApp('/login');
    await submit();
    expect(await screen.findByRole('heading', { name: heading })).toBeInTheDocument();
  });
});

describe('AuthGate (C-01)', () => {
  it('chưa đăng nhập → về /login', async () => {
    mockApi({ 'GET /auth/me': () => apiError(401, 'unauthenticated') });
    renderApp('/');
    expect(await screen.findByRole('heading', { name: 'Đăng nhập' })).toBeInTheDocument();
  });

  it('401 giữa phiên → về /login với thông báo hết phiên, câu hỏi đang soạn vẫn được giữ', async () => {
    const api = mockApi({
      'GET /auth/me': () => makeMe('bd'),
      'GET /documents': () => [
        { id: 'd1', file_name: 'A.pdf', size_bytes: 1, page_count: 1, status: 'ready', failure_reason: null, uploaded_at: '2026-10-20T00:00:00Z' },
      ],
    });
    renderApp('/');
    const input = await screen.findByLabelText('Câu hỏi của bạn');
    await waitFor(() => expect(input).toBeEnabled());
    const user = userEvent.setup();
    await user.type(input, 'Điều khoản thanh toán?');
    api.set('POST /conversations', () => apiError(401, 'session_expired'));
    await user.click(screen.getByRole('button', { name: 'Gửi' }));
    expect(await screen.findByText('Phiên làm việc đã hết hạn.')).toBeInTheDocument();
    expect(window.sessionStorage.getItem(DRAFT_KEY)).toBe('Điều khoản thanh toán?');
  });

  it('sai vai trò → về trang chủ của vai trò', async () => {
    mockApi({ 'GET /auth/me': () => makeMe('manager'), 'GET /reports/usage': () => ({ weeks: [] }) });
    renderApp('/admin/access');
    expect(await screen.findByRole('heading', { name: 'Báo cáo mức sử dụng' })).toBeInTheDocument();
  });
});
