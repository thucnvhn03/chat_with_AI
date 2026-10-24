// C-04 DocumentList: tên, số trang, dung lượng, trạng thái; tệp lỗi có lý do, Thử lại và Xóa.
import type { DocumentOut } from '../../api/client';
import { StatusBadge } from '../../components/StatusBadge';
import { failureMessage } from './failureMessages';
import { formatBytes } from './format';

interface Props {
  documents: DocumentOut[];
  onRetry: (id: string) => void;
  onDelete: (doc: DocumentOut, trigger: HTMLElement) => void;
  retryingId?: string | null;
}

export function DocumentList({ documents, onRetry, onDelete, retryingId }: Props) {
  return (
    <ul className="doc-list" aria-label="Danh sách tài liệu">
      {documents.map((doc) => (
        <li className="doc-item" key={doc.id}>
          <div className="doc-item-top">
            <span className="doc-name" title={doc.file_name}>
              {doc.file_name}
            </span>
            <StatusBadge
              status={doc.status === 'ready' ? 'ready' : doc.status === 'failed' ? 'failed' : 'processing'}
            />
          </div>
          {doc.status === 'ready' && (
            <div className="doc-meta">
              {doc.page_count ?? '?'} trang · {formatBytes(doc.size_bytes)}
            </div>
          )}
          {doc.status === 'processing' && (
            <>
              <div className="doc-meta">Chưa dùng được để trả lời cho tới khi xử lý xong</div>
              <div
                className="progress"
                role="progressbar"
                aria-label={`Đang xử lý ${doc.file_name}`}
                aria-valuetext="Đang xử lý"
              >
                <span style={{ width: '60%' }} />
              </div>
            </>
          )}
          {doc.status === 'failed' && (
            <div className="doc-meta">Lý do: {failureMessage(doc.failure_reason)}</div>
          )}
          {doc.status !== 'processing' && (
            <div className="doc-actions">
              {doc.status === 'failed' && (
                <button
                  className="btn-link"
                  type="button"
                  disabled={retryingId === doc.id}
                  onClick={() => onRetry(doc.id)}
                  aria-label={`Thử lại ${doc.file_name}`}
                >
                  Thử lại
                </button>
              )}
              <button
                className="btn-link"
                type="button"
                onClick={(e) => onDelete(doc, e.currentTarget)}
                aria-label={`Xóa ${doc.file_name}`}
              >
                Xóa
              </button>
            </div>
          )}
        </li>
      ))}
    </ul>
  );
}
