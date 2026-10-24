// S-03 Trình xem nguồn (US-015, C-14): "Trang N / M", trang trước/sau, văn bản trang với đoạn trích được
// tô sáng, cột nguồn bên phải; trạng thái "tài liệu đã bị xóa" khi API trả 404.
// Cách hiển thị theo DQ-005; mặc định hiển thị văn bản trang trong ứng dụng.
import { useQuery } from '@tanstack/react-query';
import { useEffect, useRef } from 'react';
import { Link, useLocation, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { api, ApiError, type CitationOut } from '../../api/client';
import { AppShell } from '../../app/AppShell';
import { EmptyState } from '../../components/EmptyState';
import { ErrorBanner } from '../../components/ErrorBanner';
import { SourceChip } from '../chat/SourceChip';
import { findHighlight } from './highlight';

interface ViewerState {
  citations?: CitationOut[];
  active?: CitationOut;
}

export function SourceViewerPage() {
  const { documentId = '' } = useParams();
  const [params, setParams] = useSearchParams();
  const location = useLocation();
  const navigate = useNavigate();
  const state = (location.state ?? {}) as ViewerState;
  const page = Math.max(1, Number(params.get('page')) || 1);
  const headingRef = useRef<HTMLHeadingElement>(null);

  const query = useQuery({
    queryKey: ['page', documentId, page],
    queryFn: () => api.page(documentId, page),
  });

  useEffect(() => {
    headingRef.current?.focus();
  }, [documentId]);

  const deleted = query.error instanceof ApiError && query.error.status === 404;
  const data = query.data;
  const citations = state.citations ?? (state.active ? [state.active] : []);
  const active =
    citations.find((c) => c.document_id === documentId && c.page === page) ??
    (state.active?.document_id === documentId && state.active.page === page ? state.active : undefined);
  const highlight = data ? findHighlight(data.text, active?.cited_text) : null;
  const title = data?.document_name ?? active?.document_name ?? citations[0]?.document_name ?? 'Tài liệu';

  function goTo(next: number) {
    setParams({ page: String(next) }, { replace: true, state: location.state });
  }

  return (
    <AppShell mainId="viewer-title">
      <main className="viewer">
        <section className="card" aria-labelledby="viewer-title">
          <div className="viewer-toolbar">
            <button className="btn btn-sm" type="button" onClick={() => navigate('/')}>
              ← Quay lại hội thoại
            </button>
            <h1 id="viewer-title" ref={headingRef} tabIndex={-1} style={{ fontSize: '1.0625rem' }}>
              {title}
            </h1>
            {data && (
              <>
                <span className="badge badge-info" aria-live="polite">
                  Trang {data.page} / {data.page_count}
                </span>
                <span style={{ marginLeft: 'auto' }} className="small muted">
                  Đoạn được tô sáng là thông tin dùng trong câu trả lời
                </span>
                <div style={{ display: 'flex', gap: 6 }}>
                  <button
                    className="btn btn-sm"
                    type="button"
                    aria-label="Trang trước"
                    disabled={page <= 1}
                    onClick={() => goTo(page - 1)}
                  >
                    ‹
                  </button>
                  <button
                    className="btn btn-sm"
                    type="button"
                    aria-label="Trang sau"
                    disabled={page >= data.page_count}
                    onClick={() => goTo(page + 1)}
                  >
                    ›
                  </button>
                </div>
              </>
            )}
          </div>
          {query.isPending && (
            <p className="card-pad muted" role="status">
              Đang tải trang…
            </p>
          )}
          {data && (
            <div className="viewer-stage">
              <article className="page-paper" aria-label={`Nội dung trang ${data.page} của ${data.document_name}`}>
                <pre className="page-text">
                  {highlight ? (
                    <>
                      {highlight.before}
                      <mark className="hit">{highlight.match}</mark>
                      {highlight.after}
                    </>
                  ) : (
                    data.text || 'Trang này không có văn bản.'
                  )}
                </pre>
                <div className="page-no">— {data.page} —</div>
              </article>
            </div>
          )}
          {deleted && (
            <div className="card-pad">
              <EmptyState icon="🗑" title="Tài liệu này đã bị xóa" headingLevel={2}>
                <p>
                  Không thể mở trang nguồn vì tài liệu không còn trong tập tài liệu của bạn. Nếu cần, hãy tải lại
                  tài liệu rồi đặt lại câu hỏi.
                </p>
                <Link className="btn btn-primary" to="/">
                  Quay lại hội thoại
                </Link>
              </EmptyState>
            </div>
          )}
          {query.isError && !deleted && (
            <div className="card-pad">
              <ErrorBanner
                actions={
                  <button className="btn btn-sm" type="button" onClick={() => void query.refetch()}>
                    Thử lại
                  </button>
                }
              >
                Không tải được trang nguồn.
              </ErrorBanner>
            </div>
          )}
        </section>
        {citations.length > 0 && (
          <aside className="card card-pad" aria-labelledby="src-title" style={{ alignSelf: 'start' }}>
            <h2 id="src-title">Nguồn của câu trả lời</h2>
            <p className="small muted">Chọn một nguồn để mở đúng trang.</p>
            <ul style={{ listStyle: 'none', padding: 0, margin: '12px 0 0', display: 'flex', flexDirection: 'column', gap: 10 }}>
              {citations.map((c) => (
                <li key={`${c.document_id}-${c.page}`}>
                  <SourceChip
                    citation={c}
                    allCitations={citations}
                    current={c.document_id === documentId && c.page === page}
                  />
                </li>
              ))}
            </ul>
          </aside>
        )}
      </main>
    </AppShell>
  );
}
