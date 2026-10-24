// S-06 Bản ghi kiểm toán (US-020, C-19): bộ lọc, bảng (thời điểm, người dùng, tài liệu liên quan),
// trạng thái trống và lỗi (kèm "Thử lại"). Không hiển thị nội dung câu hỏi.
import { useInfiniteQuery } from '@tanstack/react-query';
import { useState, type FormEvent } from 'react';
import { api } from '../../api/client';
import { EmptyState } from '../../components/EmptyState';
import { ErrorBanner } from '../../components/ErrorBanner';
import { TbdTag } from '../../components/TbdTag';
import { AdminLayout } from './AdminLayout';

interface Filters {
  from: string;
  to: string;
  user: string;
  document: string;
}

const EMPTY: Filters = { from: '', to: '', user: '', document: '' };

function toParams(filters: Filters, cursor?: string): URLSearchParams {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) if (value.trim()) params.set(key, value.trim());
  if (cursor) params.set('cursor', cursor);
  return params;
}

const dateTime = new Intl.DateTimeFormat('vi-VN', { dateStyle: 'short', timeStyle: 'medium' });

export function AuditPage() {
  const [draft, setDraft] = useState<Filters>(EMPTY);
  const [filters, setFilters] = useState<Filters>(EMPTY);

  const query = useInfiniteQuery({
    queryKey: ['admin', 'audit', filters],
    queryFn: ({ pageParam }) => api.audit(toParams(filters, pageParam)),
    initialPageParam: undefined as string | undefined,
    getNextPageParam: (last) => last.next_cursor ?? undefined,
  });

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    setFilters(draft);
  }

  const items = query.data?.pages.flatMap((p) => p.items) ?? [];
  const field = (key: keyof Filters) => ({
    value: draft[key],
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => setDraft({ ...draft, [key]: e.target.value }),
  });

  return (
    <AdminLayout>
      <div className="page-title">
        <div>
          <h1>Bản ghi kiểm toán truy vấn</h1>
          <p className="muted" style={{ margin: '4px 0 0' }}>
            Cho biết người dùng nào đã hỏi về tài liệu nào và vào thời điểm nào. Bản ghi được lưu tối thiểu{' '}
            <TbdTag id="OQ-012" /> ngày.
          </p>
        </div>
      </div>
      {query.isError && (
        <ErrorBanner
          title="Không tải được bản ghi kiểm toán."
          actions={
            <button className="btn btn-sm" type="button" onClick={() => void query.refetch()}>
              Thử lại
            </button>
          }
        >
          Hãy thử lại sau ít phút.
        </ErrorBanner>
      )}
      <section className="card" aria-labelledby="res-title">
        <form className="toolbar" onSubmit={onSubmit}>
          <h2 id="res-title" style={{ width: '100%' }}>
            Lọc bản ghi
          </h2>
          <div className="field">
            <label htmlFor="audit-from">Từ ngày</label>
            <input id="audit-from" type="date" {...field('from')} />
          </div>
          <div className="field">
            <label htmlFor="audit-to">Đến ngày</label>
            <input id="audit-to" type="date" {...field('to')} />
          </div>
          <div className="field">
            <label htmlFor="audit-user">Người dùng</label>
            <input id="audit-user" type="text" placeholder="Tất cả" {...field('user')} />
          </div>
          <div className="field">
            <label htmlFor="audit-doc">Tài liệu</label>
            <input id="audit-doc" type="text" placeholder="Tất cả" {...field('document')} />
          </div>
          <button className="btn btn-primary" type="submit">
            Lọc
          </button>
        </form>
        {query.isPending && (
          <p className="card-pad muted" role="status">
            Đang tải bản ghi…
          </p>
        )}
        {query.isSuccess && items.length === 0 && (
          <EmptyState icon="🔍" title="Không có bản ghi trong khoảng đã chọn">
            <p>Hãy mở rộng khoảng thời gian hoặc bỏ bớt điều kiện lọc.</p>
          </EmptyState>
        )}
        {items.length > 0 && (
          <div className="table-wrap">
            <table>
              <caption className="sr-only">Bản ghi truy vấn, mới nhất trước</caption>
              <thead>
                <tr>
                  <th scope="col">Thời điểm</th>
                  <th scope="col">Người dùng</th>
                  <th scope="col">Tài liệu liên quan</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td>{dateTime.format(new Date(item.at))}</td>
                    <td>{item.user.login ?? item.user.id}</td>
                    <td>
                      {item.documents.length === 0
                        ? 'Không có tài liệu'
                        : item.documents.map((d) => d.file_name ?? 'Tài liệu đã xóa').join('; ')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {query.hasNextPage && (
          <div className="load-more">
            <button
              className="btn"
              type="button"
              onClick={() => void query.fetchNextPage()}
              disabled={query.isFetchingNextPage}
            >
              {query.isFetchingNextPage ? 'Đang tải…' : 'Xem thêm bản ghi'}
            </button>
          </div>
        )}
      </section>
      <p className="small muted">
        Không hiển thị nội dung câu hỏi hay nội dung tài liệu: chỉ hiển thị người dùng, tài liệu liên quan và thời
        điểm (BR-023).
      </p>
    </AdminLayout>
  );
}
