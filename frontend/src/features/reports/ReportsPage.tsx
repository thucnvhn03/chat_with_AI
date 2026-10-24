// S-07 Báo cáo mức sử dụng (US-022, US-023, US-024; C-20): thẻ số liệu, biểu đồ cột có chú giải VÀ bảng
// số liệu tương ứng (không phụ thuộc màu), trạng thái trống, lỗi.
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { api, type UsageReport } from '../../api/client';
import { AppShell } from '../../app/AppShell';
import { EmptyState } from '../../components/EmptyState';
import { ErrorBanner } from '../../components/ErrorBanner';
import { TbdTag } from '../../components/TbdTag';

type Week = UsageReport['weeks'][number];

const pad = (n: number) => String(n).padStart(2, '0');
const dayMonth = { format: (d: Date) => `${pad(d.getDate())}/${pad(d.getMonth() + 1)}` };

export function weekLabel(week: string): string {
  const start = new Date(`${week}T00:00:00`);
  const end = new Date(start);
  end.setDate(start.getDate() + 6);
  return `${dayMonth.format(start)}–${dayMonth.format(end)}`;
}

function percent(ratio: number | null | undefined): string {
  return ratio === null || ratio === undefined ? '—' : `${Math.round(ratio * 100)}%`;
}

const BAR_MAX_PX = 170;

function Chart({ weeks }: { weeks: Week[] }) {
  const max = Math.max(1, ...weeks.flatMap((w) => [w.active_users, w.questions]));
  const height = (v: number) => `${Math.max(4, Math.round((v / max) * BAR_MAX_PX))}px`;
  const summary = weeks
    .map((w) => `${weekLabel(w.week)}: ${w.active_users} người dùng, ${w.questions} câu hỏi`)
    .join('; ');
  return (
    <>
      <div className="bars" role="img" aria-label={`Biểu đồ cột theo tuần. ${summary}`}>
        {weeks.map((w) => (
          <div className="bar-col" key={w.week}>
            <div style={{ display: 'flex', gap: 4, alignItems: 'flex-end', height: '100%', width: '100%', justifyContent: 'center' }}>
              <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', alignItems: 'center' }}>
                <span className="bar-val">{w.active_users}</span>
                <div className="bar" style={{ height: height(w.active_users), width: 28 }} />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', alignItems: 'center' }}>
                <span className="bar-val">{w.questions}</span>
                <div className="bar alt" style={{ height: height(w.questions), width: 28 }} />
              </div>
            </div>
            <div className="bar-lbl">{weekLabel(w.week)}</div>
          </div>
        ))}
      </div>
      <div className="legend">
        <span>
          <i style={{ background: 'var(--primary)' }} />
          Người dùng hoạt động
        </span>
        <span>
          <i style={{ background: '#0f766e' }} />
          Số câu hỏi
        </span>
      </div>
    </>
  );
}

export function ReportsPage() {
  const [weeks, setWeeks] = useState(4);
  const query = useQuery({ queryKey: ['reports', 'usage', weeks], queryFn: () => api.usage(weeks) });
  const data = query.data?.weeks ?? [];
  const latest = data[data.length - 1];
  const empty = query.isSuccess && data.every((w) => w.active_users === 0 && w.questions === 0);
  const totalFeedback = data.reduce((sum, w) => sum + w.feedback_count, 0);
  const helpful = data.reduce((sum, w) => sum + (w.helpful_ratio ?? 0) * w.feedback_count, 0);

  return (
    <AppShell>
      <main id="main" style={{ padding: '20px 24px', maxWidth: 1100 }}>
        <div className="page-title">
          <div>
            <h1>Báo cáo mức sử dụng</h1>
            <p className="muted" style={{ margin: '4px 0 0' }}>
              Số liệu hằng tuần trong giai đoạn thử nghiệm: người dùng hoạt động và số câu hỏi.
            </p>
          </div>
          <div className="field" style={{ margin: 0, width: 200 }}>
            <label htmlFor="report-range">Khoảng thời gian</label>
            <select id="report-range" value={weeks} onChange={(e) => setWeeks(Number(e.target.value))}>
              <option value={4}>4 tuần gần nhất</option>
              <option value={8}>8 tuần gần nhất</option>
            </select>
          </div>
        </div>
        {query.isError && (
          <ErrorBanner
            title="Không tải được báo cáo."
            actions={
              <button className="btn btn-sm" type="button" onClick={() => void query.refetch()}>
                Thử lại
              </button>
            }
          >
            Hãy thử lại sau ít phút.
          </ErrorBanner>
        )}
        {query.isPending && (
          <p className="muted" role="status">
            Đang tải báo cáo…
          </p>
        )}
        {empty && (
          <div className="card">
            <EmptyState icon="📊" title="Chưa có dữ liệu sử dụng">
              <p>Số liệu sẽ xuất hiện sau khi người dùng bắt đầu dùng ứng dụng trong giai đoạn thử nghiệm.</p>
            </EmptyState>
          </div>
        )}
        {query.isSuccess && !empty && latest && (
          <>
            <div className="kpis">
              <div className="card kpi">
                <div className="kpi-label">Người dùng hoạt động (tuần gần nhất)</div>
                <div className="kpi-value">{latest.active_users}</div>
                <div className="small muted">
                  Mục tiêu: <TbdTag id="OQ-002" />
                </div>
              </div>
              <div className="card kpi">
                <div className="kpi-label">Câu hỏi (tuần gần nhất)</div>
                <div className="kpi-value">{latest.questions}</div>
                <div className="small muted">
                  Mục tiêu: <TbdTag id="OQ-002" />
                </div>
              </div>
              <div className="card kpi">
                <div className="kpi-label">Câu trả lời được đánh giá hữu ích</div>
                <div className="kpi-value">{totalFeedback ? percent(helpful / totalFeedback) : '—'}</div>
                <div className="small muted">
                  Dựa trên {totalFeedback} đánh giá của người dùng trong {weeks} tuần
                </div>
              </div>
            </div>
            <section className="card card-pad" aria-labelledby="chart-title">
              <h2 id="chart-title">Theo tuần</h2>
              <Chart weeks={data} />
              <div className="table-wrap" style={{ marginTop: 16 }}>
                <table>
                  <caption>Bảng số liệu tương ứng với biểu đồ</caption>
                  <thead>
                    <tr>
                      <th scope="col">Tuần</th>
                      <th scope="col">Người dùng hoạt động</th>
                      <th scope="col">Số câu hỏi</th>
                      <th scope="col">Tỷ lệ hữu ích</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.map((w) => (
                      <tr key={w.week}>
                        <td>{weekLabel(w.week)}</td>
                        <td>{w.active_users}</td>
                        <td>{w.questions}</td>
                        <td>{percent(w.helpful_ratio)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        )}
      </main>
    </AppShell>
  );
}
