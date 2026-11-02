// Cấu hình đọc từ biến môi trường. Mật khẩu không bao giờ ghi vào log hay kết quả tool.

export interface Config {
  /** Gốc API, gồm tiền tố /api/v1 */
  apiUrl: string;
  /** Header Origin gửi kèm yêu cầu thay đổi dữ liệu; phải thuộc ALLOWED_ORIGINS của backend (CSRF) */
  origin: string;
  login: string;
  password: string;
  /** Thời gian tối đa chờ tài liệu xử lý xong khi tải lên với wait=true */
  uploadWaitSeconds: number;
}

export function loadConfig(env: NodeJS.ProcessEnv = process.env): Config {
  const login = env.CWD_LOGIN?.trim();
  const password = env.CWD_PASSWORD;
  if (!login || !password) {
    throw new Error('Thiếu CWD_LOGIN hoặc CWD_PASSWORD (tài khoản nội bộ, AUTH_MODE=local).');
  }
  return {
    apiUrl: (env.CWD_API_URL ?? 'http://localhost:8000/api/v1').replace(/\/+$/, ''),
    origin: (env.CWD_ORIGIN ?? 'http://localhost:5173').replace(/\/+$/, ''),
    login,
    password,
    uploadWaitSeconds: Number(env.CWD_UPLOAD_WAIT_SECONDS ?? 180),
  };
}
