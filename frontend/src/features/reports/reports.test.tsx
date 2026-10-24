// T4-02: S-07 báo cáo mức sử dụng — số liệu, biểu đồ kèm bảng, trống, lỗi.
import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { apiError, makeMe, mockApi, renderApp, seriousViolations } from '../../test/utils';
import { weekLabel } from './ReportsPage';

const WEEKS = [
  { week: '2026-09-28', active_users: 3, questions: 20, helpful_ratio: null, feedback_count: 0 },
  { week: '2026-10-05', active_users: 5, questions: 38, helpful_ratio: 0.5, feedback_count: 4 },
  { week: '2026-10-12', active_users: 7, questions: 52, helpful_ratio: 1, feedback_count: 2 },
  { week: '2026-10-19', active_users: 8, questions: 64, helpful_ratio: 0.75, feedback_count: 4 },
];

describe('S-07 Báo cáo mức sử dụng', () => {
  it('s07-default: thẻ số liệu tuần gần nhất, biểu đồ có chú giải và bảng số liệu', async () => {
    mockApi({ 'GET /auth/me': () => makeMe('manager'), 'GET /reports/usage': () => ({ weeks: WEEKS }) });
    const { container } = renderApp('/reports');
    expect(await screen.findByText('Người dùng hoạt động (tuần gần nhất)')).toBeInTheDocument();
    const kpis = container.querySelectorAll('.kpi-value');
    expect(Array.from(kpis).map((k) => k.textContent)).toEqual(['8', '64', '70%']);
    const chart = screen.getByRole('img');
    expect(chart.getAttribute('aria-label')).toContain('8 người dùng, 64 câu hỏi');
    const table = screen.getByRole('table', { name: 'Bảng số liệu tương ứng với biểu đồ' });
    const rows = within(table).getAllByRole('row').slice(1);
    expect(rows).toHaveLength(4);
    expect(rows[3]).toHaveTextContent(`${weekLabel('2026-10-19')}86475%`);
    const legend = container.querySelector('.legend') as HTMLElement;
    expect(legend).toHaveTextContent('Người dùng hoạt động');
    expect(legend).toHaveTextContent('Số câu hỏi');
    expect(await seriousViolations(container)).toEqual([]);
  });

  it('đổi khoảng thời gian gọi lại API', async () => {
    const api = mockApi({ 'GET /auth/me': () => makeMe('manager'), 'GET /reports/usage': () => ({ weeks: WEEKS }) });
    renderApp('/reports');
    await screen.findByRole('table');
    await userEvent.selectOptions(screen.getByLabelText('Khoảng thời gian'), '8');
    const fetchMock = globalThis.fetch as unknown as { mock: { calls: [string][] } };
    await screen.findByRole('table');
    expect(fetchMock.mock.calls.some((c) => String(c[0]).endsWith('/reports/usage?weeks=8'))).toBe(true);
    expect(api.calls.filter((c) => c.path === '/reports/usage').length).toBeGreaterThanOrEqual(2);
  });

  it('s07-empty', async () => {
    const zero = WEEKS.map((w) => ({ ...w, active_users: 0, questions: 0, helpful_ratio: null, feedback_count: 0 }));
    mockApi({ 'GET /auth/me': () => makeMe('manager'), 'GET /reports/usage': () => ({ weeks: zero }) });
    renderApp('/reports');
    expect(await screen.findByRole('heading', { name: 'Chưa có dữ liệu sử dụng' })).toBeInTheDocument();
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
  });

  it('s07-error có Thử lại', async () => {
    mockApi({ 'GET /auth/me': () => makeMe('manager'), 'GET /reports/usage': () => apiError(500, 'internal_error') });
    renderApp('/reports');
    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('Không tải được báo cáo.');
    expect(within(alert).getByRole('button', { name: 'Thử lại' })).toBeInTheDocument();
  });
});
