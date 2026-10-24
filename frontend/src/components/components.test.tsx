// T0-05: thành phần dùng chung và AppShell (kèm kiểm tra axe).
import { screen, waitFor } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { makeMe, mockApi, renderApp, renderWithProviders, seriousViolations } from '../test/utils';
import { EmptyState } from './EmptyState';
import { ErrorBanner } from './ErrorBanner';
import { StatusBadge } from './StatusBadge';

describe('ErrorBanner (C-16)', () => {
  it('có vai trò alert, tiêu đề và hành động', () => {
    renderWithProviders(
      <ErrorBanner title="Không tải được." actions={<button type="button">Thử lại</button>}>
        Hãy thử lại sau.
      </ErrorBanner>,
    );
    const alert = screen.getByRole('alert');
    expect(alert).toHaveTextContent('Không tải được. Hãy thử lại sau.');
    expect(alert).toHaveClass('banner-err');
    expect(screen.getByRole('button', { name: 'Thử lại' })).toBeInTheDocument();
  });

  it('dạng thông tin dùng vai trò note', () => {
    renderWithProviders(<ErrorBanner tone="info">Ghi chú</ErrorBanner>);
    expect(screen.getByRole('note')).toHaveClass('banner-info');
  });
});

describe('EmptyState (C-10)', () => {
  it('hiển thị tiêu đề và hướng dẫn, biểu tượng ẩn với trình đọc màn hình', () => {
    const { container } = renderWithProviders(
      <EmptyState icon="📄" title="Chưa có tài liệu nào">
        <p>Hãy tải PDF lên.</p>
      </EmptyState>,
    );
    expect(screen.getByRole('heading', { name: 'Chưa có tài liệu nào' })).toBeInTheDocument();
    expect(container.querySelector('.empty-icon')).toHaveAttribute('aria-hidden', 'true');
  });
});

describe('StatusBadge (C-06)', () => {
  it.each([
    ['ready', 'Sẵn sàng', 'badge-ok'],
    ['processing', 'Đang xử lý', 'badge-warn'],
    ['failed', 'Lỗi', 'badge-err'],
    ['incomplete', 'Chưa tải xong', 'badge-err'],
  ] as const)('%s luôn có chữ "%s", không chỉ dùng màu', (status, label, cls) => {
    const { container } = renderWithProviders(<StatusBadge status={status} />);
    const badge = container.querySelector('.badge');
    expect(badge).toHaveTextContent(label);
    expect(badge).toHaveClass(cls);
  });
});

describe('AppShell (C-00)', () => {
  it('có liên kết bỏ qua, tên người dùng, không có vi phạm axe nghiêm trọng', async () => {
    mockApi({
      'GET /auth/me': () => makeMe('manager'),
      'GET /reports/usage': () => ({ weeks: [] }),
    });
    const { container } = renderApp('/reports');
    await screen.findByText(/Quản lý \(Nguyễn An\)/);
    expect(screen.getByText('Bỏ qua tới nội dung chính')).toHaveAttribute('href', '#main');
    expect(screen.getByRole('button', { name: 'Đăng xuất' })).toBeInTheDocument();
    await waitFor(async () => expect(await seriousViolations(container)).toEqual([]));
  });
});
