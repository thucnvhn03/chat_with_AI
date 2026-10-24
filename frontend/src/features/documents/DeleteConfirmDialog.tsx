// C-05 DeleteConfirmDialog (S-04, US-006/007): tiêu điểm mặc định ở "Hủy", nêu tên tài liệu, thời hạn xóa
// vĩnh viễn và "không thể hoàn tác"; lỗi hiển thị ngay trong hộp thoại; Esc đóng và trả focus về nút gọi.
import { useEffect, useRef, type KeyboardEvent } from 'react';
import { TbdTag } from '../../components/TbdTag';
import { ErrorBanner } from '../../components/ErrorBanner';
import { formatHours } from './format';

interface Props {
  fileName: string;
  purgeSlaHours?: number;
  deleting: boolean;
  failed: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}

export function DeleteConfirmDialog({ fileName, purgeSlaHours, deleting, failed, onCancel, onConfirm }: Props) {
  const cancelRef = useRef<HTMLButtonElement>(null);
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    cancelRef.current?.focus();
  }, []);

  function onKeyDown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      event.stopPropagation();
      onCancel();
      return;
    }
    if (event.key !== 'Tab' || !dialogRef.current) return;
    // Giữ tiêu điểm trong hộp thoại
    const focusable = Array.from(
      dialogRef.current.querySelectorAll<HTMLElement>('button:not([disabled])'),
    );
    if (focusable.length === 0) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  return (
    <div className="overlay" onKeyDown={onKeyDown}>
      <div
        ref={dialogRef}
        className="dialog"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="delete-title"
        aria-describedby="delete-desc"
      >
        <h2 id="delete-title">Xóa tài liệu "{fileName}"?</h2>
        <p id="delete-desc">
          Tài liệu sẽ bị gỡ khỏi tập tài liệu của bạn và không còn được dùng để trả lời. Nội dung sẽ bị
          xóa vĩnh viễn trong vòng{' '}
          {purgeSlaHours !== undefined ? formatHours(purgeSlaHours) : <TbdTag id="OQ-012" />}.{' '}
          <strong>Thao tác này không thể hoàn tác.</strong>
        </p>
        {failed && (
          <ErrorBanner style={{ marginTop: 12 }}>Chưa xóa được tài liệu. Hãy thử lại sau ít phút.</ErrorBanner>
        )}
        <div className="dialog-actions">
          <button ref={cancelRef} className="btn" type="button" onClick={onCancel}>
            Hủy
          </button>
          <button className="btn btn-danger" type="button" onClick={onConfirm} disabled={deleting}>
            {deleting ? 'Đang xóa…' : 'Xóa vĩnh viễn'}
          </button>
        </div>
      </div>
    </div>
  );
}
