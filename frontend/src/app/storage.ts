// sessionStorage có thể bị chặn (chế độ riêng tư, chính sách trình duyệt): mọi truy cập đều bọc try/catch.
export const DRAFT_KEY = 'cwd.draft';

export const storage = {
  get(key: string): string | null {
    try {
      return window.sessionStorage.getItem(key);
    } catch {
      return null;
    }
  },
  set(key: string, value: string): void {
    try {
      window.sessionStorage.setItem(key, value);
    } catch {
      // bỏ qua: chỉ mất tiện ích giữ câu hỏi/hội thoại
    }
  },
  remove(key: string): void {
    try {
      window.sessionStorage.removeItem(key);
    } catch {
      // bỏ qua
    }
  },
};
