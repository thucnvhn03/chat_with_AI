// XMLHttpRequest giả lập cho kiểm thử tải lên: kiểm thử tự quyết định tiến độ, thành công hay mất mạng.
import { vi } from 'vitest';

export class FakeXhr {
  static instances: FakeXhr[] = [];
  method = '';
  url = '';
  status = 0;
  response: unknown = null;
  responseType = '';
  withCredentials = false;
  body: FormData | null = null;
  upload: { onprogress: ((e: { lengthComputable: boolean; loaded: number; total: number }) => void) | null } = {
    onprogress: null,
  };
  onload: (() => void) | null = null;
  onerror: (() => void) | null = null;
  onabort: (() => void) | null = null;

  constructor() {
    FakeXhr.instances.push(this);
  }

  open(method: string, url: string) {
    this.method = method;
    this.url = url;
  }

  send(body: FormData) {
    this.body = body;
  }

  abort() {
    this.onabort?.();
  }

  get fileName(): string {
    const file = this.body?.get('files');
    return file instanceof File ? file.name : '';
  }

  progress(fraction: number) {
    this.upload.onprogress?.({ lengthComputable: true, loaded: fraction * 100, total: 100 });
  }

  respond(status: number, body: unknown) {
    this.status = status;
    this.response = body;
    this.onload?.();
  }

  networkError() {
    this.onerror?.();
  }
}

export function installFakeXhr(): void {
  FakeXhr.instances = [];
  vi.stubGlobal('XMLHttpRequest', FakeXhr);
}
