// C-02 DocumentPanel: vùng "Tài liệu của tôi" gồm UploadControl, DocumentList, EmptyState, hộp thoại xóa.
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRef, useState } from 'react';
import { api, type DocumentOut } from '../../api/client';
import { EmptyState } from '../../components/EmptyState';
import { ErrorBanner } from '../../components/ErrorBanner';
import { DeleteConfirmDialog } from './DeleteConfirmDialog';
import { DocumentList } from './DocumentList';
import { UploadControl } from './UploadControl';
import { DOCUMENTS_KEY } from './useDocuments';
import type { useUploads } from './useUploads';

interface Props {
  documents: DocumentOut[] | undefined;
  loading: boolean;
  loadError: boolean;
  onReload: () => void;
  uploads: ReturnType<typeof useUploads>;
  maxFileBytes?: number;
  maxDocs?: number;
  purgeSlaHours?: number;
}

export function DocumentPanel(props: Props) {
  const { documents, loading, loadError, onReload, uploads } = props;
  const queryClient = useQueryClient();
  const [toDelete, setToDelete] = useState<DocumentOut | null>(null);
  const trigger = useRef<HTMLElement | null>(null);

  const retry = useMutation({
    mutationFn: api.retryDocument,
    onSettled: () => queryClient.invalidateQueries({ queryKey: DOCUMENTS_KEY }),
  });
  const remove = useMutation({
    mutationFn: api.deleteDocument,
    onSuccess: (_data, id) => {
      // Tài liệu biến khỏi danh sách ngay
      queryClient.setQueryData<DocumentOut[]>(DOCUMENTS_KEY, (current) =>
        current?.filter((d) => d.id !== id),
      );
      closeDialog();
      void queryClient.invalidateQueries({ queryKey: DOCUMENTS_KEY });
    },
  });

  function closeDialog() {
    setToDelete(null);
    remove.reset();
    // Trả tiêu điểm về nút đã mở hộp thoại (nếu nút còn trên trang), nếu không thì về tiêu đề vùng
    const target = trigger.current?.isConnected ? trigger.current : document.getElementById('docs-title');
    target?.focus();
  }

  const count = documents?.length ?? 0;
  const empty = !loading && !loadError && count === 0 && uploads.items.length === 0;

  return (
    <aside className="card panel" aria-labelledby="docs-title">
      <div className="panel-head">
        <h2 id="docs-title" tabIndex={-1}>
          Tài liệu của tôi
        </h2>
        {count > 0 && <span className="small muted">{count} tệp</span>}
      </div>
      <div className="panel-body">
        <UploadControl
          items={uploads.items}
          maxFileBytes={props.maxFileBytes}
          maxDocs={props.maxDocs}
          onFiles={uploads.addFiles}
          onRetry={uploads.retry}
          onDismiss={uploads.dismiss}
        />
        {loadError && (
          <ErrorBanner
            style={{ marginTop: 12 }}
            actions={
              <button className="btn btn-sm" type="button" onClick={onReload}>
                Thử lại
              </button>
            }
          >
            Không tải được danh sách tài liệu.
          </ErrorBanner>
        )}
        {loading && (
          <p className="small muted" role="status">
            Đang tải danh sách tài liệu…
          </p>
        )}
        {empty && (
          <EmptyState icon="📄" title="Chưa có tài liệu nào">
            <p>Hãy tải ít nhất một tệp PDF lên. Sau đó bạn có thể hỏi về nội dung của tất cả các tài liệu.</p>
          </EmptyState>
        )}
        {count > 0 && documents && (
          <DocumentList
            documents={documents}
            retryingId={retry.isPending ? retry.variables : null}
            onRetry={(id) => retry.mutate(id)}
            onDelete={(doc, el) => {
              trigger.current = el;
              setToDelete(doc);
            }}
          />
        )}
      </div>
      {toDelete && (
        <DeleteConfirmDialog
          fileName={toDelete.file_name}
          purgeSlaHours={props.purgeSlaHours}
          deleting={remove.isPending}
          failed={remove.isError}
          onCancel={closeDialog}
          onConfirm={() => remove.mutate(toDelete.id)}
        />
      )}
    </aside>
  );
}
