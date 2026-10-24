// C-03 UploadControl: nút "Tải PDF lên", chọn nhiều tệp, kéo thả, tiến độ và kết quả TỪNG tệp.
// Không khóa vùng hội thoại khi đang tải.
import { useRef, useState, type DragEvent } from 'react';
import { StatusBadge } from '../../components/StatusBadge';
import { failureMessage } from './failureMessages';
import { formatBytes } from './format';
import type { UploadItem } from './useUploads';

interface Props {
  items: UploadItem[];
  maxFileBytes?: number;
  maxDocs?: number;
  onFiles: (files: File[]) => void;
  onRetry: (key: string) => void;
  onDismiss: (key: string) => void;
}

export function UploadControl({ items, maxFileBytes, maxDocs, onFiles, onRetry, onDismiss }: Props) {
  const input = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  function onDrop(event: DragEvent) {
    event.preventDefault();
    setDragOver(false);
    const files = Array.from(event.dataTransfer.files);
    if (files.length) onFiles(files);
  }

  return (
    <>
      <div
        className={`dropzone${dragOver ? ' is-dragover' : ''}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
      >
        <button className="btn btn-primary" type="button" onClick={() => input.current?.click()}>
          ＋ Tải PDF lên
        </button>
        <input
          ref={input}
          type="file"
          accept="application/pdf,.pdf"
          multiple
          hidden
          data-testid="file-input"
          aria-label="Chọn tệp PDF"
          onChange={(e) => {
            const files = Array.from(e.target.files ?? []);
            e.target.value = '';
            if (files.length) onFiles(files);
          }}
        />
        <p className="small muted" style={{ margin: '8px 0 0' }}>
          Chọn hoặc kéo thả một hoặc nhiều tệp PDF.
          {maxFileBytes !== undefined && maxDocs !== undefined && (
            <>
              {' '}
              Tối đa {formatBytes(maxFileBytes)} mỗi tệp, {maxDocs} tài liệu.
            </>
          )}
        </p>
      </div>

      {items.length > 0 && (
        <ul className="upload-list" aria-label="Tệp đang tải lên">
          {items.map((item) => (
            <li className="doc-item" key={item.key}>
              <div className="doc-item-top">
                <span className="doc-name" title={item.file.name}>
                  {item.file.name}
                </span>
                <StatusBadge
                  status={
                    item.status === 'uploading'
                      ? 'uploading'
                      : item.status === 'incomplete'
                        ? 'incomplete'
                        : 'failed'
                  }
                />
              </div>
              {item.status === 'uploading' && (
                <div
                  className="progress"
                  role="progressbar"
                  aria-label={`Tiến độ tải lên ${item.file.name}`}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-valuenow={Math.round(item.progress * 100)}
                >
                  <span style={{ width: `${Math.round(item.progress * 100)}%` }} />
                </div>
              )}
              {item.status !== 'uploading' && (
                <>
                  <div className="doc-meta">
                    {item.status === 'incomplete'
                      ? 'Lý do: mất kết nối. Tệp chưa nằm trong tập tài liệu.'
                      : `Lý do: ${failureMessage(item.failureReason)}`}
                  </div>
                  <div className="doc-actions">
                    {item.status === 'incomplete' && (
                      <button className="btn-link" type="button" onClick={() => onRetry(item.key)}>
                        Tải lại
                      </button>
                    )}
                    <button className="btn-link" type="button" onClick={() => onDismiss(item.key)}>
                      Bỏ qua
                    </button>
                  </div>
                </>
              )}
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
