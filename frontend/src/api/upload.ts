// Tải một tệp lên bằng XMLHttpRequest để có tiến độ theo byte (fetch chưa báo tiến độ tải lên).
// Mỗi tệp một yêu cầu: tệp lỗi hoặc mất mạng không ảnh hưởng tệp khác (US-002).
import { API_BASE, ApiError, NetworkError, notifyUnauthorized, type UploadResult } from './client';

export interface UploadHandle {
  promise: Promise<UploadResult>;
  abort: () => void;
}

export function uploadFile(file: File, onProgress: (fraction: number) => void): UploadHandle {
  const xhr = new XMLHttpRequest();
  const promise = new Promise<UploadResult>((resolve, reject) => {
    xhr.open('POST', `${API_BASE}/documents`);
    xhr.withCredentials = true;
    xhr.responseType = 'json';
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) onProgress(event.loaded / event.total);
    };
    xhr.onerror = () => reject(new NetworkError());
    xhr.onabort = () => reject(new DOMException('Đã hủy', 'AbortError'));
    xhr.onload = () => {
      const body = xhr.response as unknown;
      if (xhr.status >= 200 && xhr.status < 300 && Array.isArray(body) && body.length === 1) {
        resolve(body[0] as UploadResult);
        return;
      }
      const err = (body as { error?: { code?: string; message?: string } } | null)?.error;
      const error = new ApiError(
        xhr.status,
        err?.code ?? 'error',
        err?.message ?? 'Đã có lỗi xảy ra. Hãy thử lại sau.',
      );
      notifyUnauthorized(error, '/documents');
      reject(error);
    };
    const form = new FormData();
    form.append('files', file, file.name);
    xhr.send(form);
  });
  return { promise, abort: () => xhr.abort() };
}
