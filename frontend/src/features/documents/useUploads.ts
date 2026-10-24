// Trạng thái tải lên từng tệp (US-001..003). Kiểm tra phía trình duyệt (đuôi, dung lượng) chỉ để phản
// hồi sớm; quyết định cuối ở backend. Mất mạng giữa chừng → "Chưa tải xong", không bao giờ "Sẵn sàng".
import { useQueryClient } from '@tanstack/react-query';
import { useCallback, useRef, useState } from 'react';
import { ApiError, NetworkError } from '../../api/client';
import { uploadFile } from '../../api/upload';
import { DOCUMENTS_KEY } from './useDocuments';

export type UploadStatus = 'uploading' | 'rejected' | 'incomplete';

export interface UploadItem {
  key: string;
  file: File;
  status: UploadStatus;
  progress: number;
  failureReason?: string;
}

let nextKey = 0;

export function useUploads(maxFileBytes: number | undefined) {
  const queryClient = useQueryClient();
  const [items, setItems] = useState<UploadItem[]>([]);
  const aborts = useRef(new Map<string, () => void>());

  const update = useCallback((key: string, patch: Partial<UploadItem>) => {
    setItems((current) => current.map((i) => (i.key === key ? { ...i, ...patch } : i)));
  }, []);

  const remove = useCallback((key: string) => {
    aborts.current.get(key)?.();
    aborts.current.delete(key);
    setItems((current) => current.filter((i) => i.key !== key));
  }, []);

  const start = useCallback(
    (item: UploadItem) => {
      const handle = uploadFile(item.file, (fraction) => update(item.key, { progress: fraction }));
      aborts.current.set(item.key, handle.abort);
      handle.promise
        .then((result) => {
          if (result.status === 'failed') {
            update(item.key, { status: 'rejected', failureReason: result.failure_reason ?? undefined });
          } else {
            // Đã vào danh sách tài liệu (trạng thái "Đang xử lý"); bỏ khỏi danh sách tải lên
            setItems((current) => current.filter((i) => i.key !== item.key));
          }
          void queryClient.invalidateQueries({ queryKey: DOCUMENTS_KEY });
        })
        .catch((err: unknown) => {
          if (err instanceof DOMException && err.name === 'AbortError') return;
          if (err instanceof NetworkError) {
            update(item.key, { status: 'incomplete', failureReason: 'network' });
          } else if (err instanceof ApiError && err.status === 401) {
            // AuthGate đã điều hướng về đăng nhập
          } else {
            update(item.key, { status: 'rejected', failureReason: 'internal' });
          }
        })
        .finally(() => aborts.current.delete(item.key));
    },
    [queryClient, update],
  );

  const addFiles = useCallback(
    (files: File[]) => {
      const created: UploadItem[] = files.map((file) => {
        const key = `u${nextKey++}`;
        if (!file.name.toLowerCase().endsWith('.pdf')) {
          return { key, file, status: 'rejected', progress: 0, failureReason: 'not_pdf' };
        }
        if (maxFileBytes !== undefined && file.size > maxFileBytes) {
          return { key, file, status: 'rejected', progress: 0, failureReason: 'too_large' };
        }
        return { key, file, status: 'uploading', progress: 0 };
      });
      setItems((current) => [...current, ...created]);
      created.filter((i) => i.status === 'uploading').forEach(start);
    },
    [maxFileBytes, start],
  );

  const retry = useCallback(
    (key: string) => {
      const item = items.find((i) => i.key === key);
      if (!item) return;
      const fresh: UploadItem = { ...item, status: 'uploading', progress: 0, failureReason: undefined };
      update(key, fresh);
      start(fresh);
    },
    [items, start, update],
  );

  return { items, addFiles, retry, dismiss: remove };
}
