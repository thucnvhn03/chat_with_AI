// S-01 Đăng nhập (US-017): bốn trạng thái — mặc định, sai thông tin, không có quyền, hết phiên.
// Trạng thái lấy từ mã lỗi của API (401 invalid_credentials, 403 no_access, 401 session_expired).
import { useState, type FormEvent } from 'react';
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { api, ApiError, NetworkError } from '../../api/client';
import { homeFor, useAuth, type LoginNotice } from '../../app/auth';
import { ErrorBanner } from '../../components/ErrorBanner';

type LoginState = 'default' | 'wrong' | 'noaccess' | 'expired' | 'locked' | 'network';

const OIDC_MODE = import.meta.env.VITE_AUTH_MODE === 'oidc';

function initialState(notice: LoginNotice | undefined, error: string | null): LoginState {
  if (error === 'no_access' || notice?.reason === 'noaccess') return 'noaccess';
  if (notice?.reason === 'expired') return 'expired';
  return 'default';
}

export function LoginPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const { setMe } = useAuth();
  const routeState = location.state as { notice?: LoginNotice; from?: string } | null;
  const [state, setState] = useState<LoginState>(() =>
    initialState(routeState?.notice, params.get('error')),
  );
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!login.trim() || !password) {
      setState('wrong');
      return;
    }
    setSubmitting(true);
    try {
      const me = await api.login(login.trim(), password);
      setMe(me);
      const home = homeFor(me.role);
      // Quay lại trang trước khi hết phiên nếu cùng khu vực của vai trò
      const from = routeState?.from;
      navigate(from && from !== '/login' && from.startsWith(home) ? from : home, { replace: true });
    } catch (err) {
      if (err instanceof ApiError && err.code === 'no_access') setState('noaccess');
      else if (err instanceof ApiError && err.status === 429) setState('locked');
      else if (err instanceof NetworkError) setState('network');
      else setState('wrong');
      setPassword('');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <a className="skip-link" href="#main">
        Bỏ qua tới nội dung chính
      </a>
      <main id="main" className="login-wrap">
      <div className="card login-card">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">
            C
          </span>{' '}
          Chat với tài liệu
        </div>
        <h1>Đăng nhập</h1>
        <p className="muted">Dùng tài khoản được cấp để hỏi đáp trên tài liệu PDF của bạn.</p>

        {state === 'expired' && (
          <ErrorBanner tone="warn" icon="⏱" title="Phiên làm việc đã hết hạn.">
            Hãy đăng nhập lại. Câu hỏi bạn đang soạn sẽ được giữ lại nếu có thể.
          </ErrorBanner>
        )}
        {state === 'wrong' && (
          <ErrorBanner title="Tên đăng nhập hoặc mật khẩu chưa đúng.">
            Hãy kiểm tra lại và thử một lần nữa.
          </ErrorBanner>
        )}
        {state === 'locked' && (
          <ErrorBanner title="Đăng nhập sai quá nhiều lần.">
            Tài khoản tạm thời bị khóa. Hãy thử lại sau ít phút.
          </ErrorBanner>
        )}
        {state === 'network' && (
          <ErrorBanner icon="📡" title="Không kết nối được tới máy chủ.">
            Hãy kiểm tra mạng rồi thử lại.
          </ErrorBanner>
        )}
        {state === 'noaccess' && (
          <ErrorBanner icon="⛔" title="Tài khoản này chưa được cấp quyền sử dụng ứng dụng.">
            Hãy liên hệ quản trị bảo mật để được cấp quyền.
          </ErrorBanner>
        )}

        {OIDC_MODE ? (
          <a className="btn btn-primary" style={{ width: '100%' }} href="/api/v1/auth/oidc/login">
            Đăng nhập bằng tài khoản tổ chức
          </a>
        ) : (
          <form onSubmit={onSubmit} noValidate>
            <div className="field">
              <label htmlFor="login-user">Tên đăng nhập</label>
              <input
                id="login-user"
                type="text"
                autoComplete="username"
                placeholder="ví dụ: ten.ho@congty.vn"
                value={login}
                onChange={(e) => setLogin(e.target.value)}
                aria-invalid={state === 'wrong' || undefined}
              />
            </div>
            <div className="field">
              <label htmlFor="login-password">Mật khẩu</label>
              <input
                id="login-password"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                aria-invalid={state === 'wrong' || undefined}
              />
            </div>
            <button
              className="btn btn-primary"
              style={{ width: '100%' }}
              type="submit"
              disabled={submitting}
            >
              {submitting ? 'Đang đăng nhập…' : 'Đăng nhập'}
            </button>
          </form>
        )}
      </div>
      </main>
    </>
  );
}
