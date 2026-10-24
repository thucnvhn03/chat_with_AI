// C-01 AuthGate: biết ai đang đăng nhập (GET /auth/me), xử lý 401 → về /login, điều hướng theo vai trò.
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { createContext, useCallback, useContext, useEffect, useMemo, type ReactNode } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { api, ApiError, setUnauthorizedHandler, type Me, type Role } from '../api/client';

export const ME_KEY = ['me'] as const;

/** Trang chủ theo vai trò: BD → S-02, quản trị bảo mật → S-05, quản lý → S-07. */
export function homeFor(role: string | undefined): string {
  if (role === 'security_admin') return '/admin/access';
  if (role === 'manager') return '/reports';
  return '/';
}

export interface LoginNotice {
  reason: 'expired' | 'noaccess';
}

interface AuthValue {
  me: Me | null;
  loading: boolean;
  setMe: (me: Me | null) => void;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const location = useLocation();
  const onLoginPage = location.pathname === '/login';

  const query = useQuery({
    queryKey: ME_KEY,
    queryFn: api.me,
    retry: false,
    staleTime: Infinity,
    enabled: !onLoginPage,
  });

  const setMe = useCallback(
    (me: Me | null) => queryClient.setQueryData(ME_KEY, me),
    [queryClient],
  );

  useEffect(() => {
    // 401 ở bất kỳ yêu cầu nào: quay về đăng nhập; câu hỏi đang soạn đã nằm trong sessionStorage
    setUnauthorizedHandler((code) => {
      const hadSession = queryClient.getQueryData(ME_KEY) != null;
      queryClient.clear();
      const notice: LoginNotice | undefined =
        code === 'session_expired' || hadSession ? { reason: 'expired' } : undefined;
      navigate('/login', { replace: true, state: { notice, from: window.location.pathname } });
    });
    return () => setUnauthorizedHandler(null);
  }, [navigate, queryClient]);

  const logout = useCallback(async () => {
    try {
      await api.logout();
    } finally {
      queryClient.clear();
      navigate('/login', { replace: true });
    }
  }, [navigate, queryClient]);

  const error = query.error;
  const noAccess = error instanceof ApiError && error.status === 403 && error.code === 'no_access';
  const value = useMemo<AuthValue>(
    () => ({ me: query.data ?? null, loading: query.isPending && !onLoginPage, setMe, logout }),
    [query.data, query.isPending, onLoginPage, setMe, logout],
  );

  if (noAccess && !onLoginPage) {
    return <Navigate to="/login" replace state={{ notice: { reason: 'noaccess' } }} />;
  }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth phải nằm trong AuthProvider');
  return value;
}

/** Chặn tuyến theo vai trò; sai vai trò thì đưa về trang chủ của vai trò đó. */
export function RequireRole({ roles, children }: { roles: Role[]; children: ReactNode }) {
  const { me, loading } = useAuth();
  if (loading) {
    return (
      <p className="app-main-loading" role="status">
        Đang tải…
      </p>
    );
  }
  if (!me) return <Navigate to="/login" replace />;
  if (!roles.includes(me.role as Role)) return <Navigate to={homeFor(me.role)} replace />;
  return <>{children}</>;
}
