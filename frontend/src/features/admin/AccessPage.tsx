// S-05 Quản lý quyền (US-017, C-18): cấp quyền, bảng người dùng, thu hồi có xác nhận, trạng thái trống.
// Cột "Phạm vi tài liệu" hiển thị [TBD: OQ-003] cho tới khi có quyết định.
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, type FormEvent } from 'react';
import { api, ApiError, type GrantOut, type Role } from '../../api/client';
import { roleLabel } from '../../app/AppShell';
import { EmptyState } from '../../components/EmptyState';
import { ErrorBanner } from '../../components/ErrorBanner';
import { StatusBadge } from '../../components/StatusBadge';
import { TbdTag } from '../../components/TbdTag';
import { useAuth } from '../../app/auth';
import { AdminLayout } from './AdminLayout';

const ACCESS_KEY = ['admin', 'access'] as const;

export function AccessPage() {
  const queryClient = useQueryClient();
  const { me } = useAuth();
  const [login, setLogin] = useState('');
  const [role, setRole] = useState<Role>('bd');
  const [formError, setFormError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [confirm, setConfirm] = useState<GrantOut | null>(null);

  const list = useQuery({ queryKey: ACCESS_KEY, queryFn: api.listAccess });
  const grant = useMutation({
    mutationFn: () => api.grantAccess(login.trim(), role),
    onSuccess: (g) => {
      setNotice(`Đã cấp vai trò ${roleLabel(g.role)} cho "${g.login}".`);
      setLogin('');
      void queryClient.invalidateQueries({ queryKey: ACCESS_KEY });
    },
    onError: (err) => setFormError(err instanceof ApiError ? err.message : 'Chưa cấp được quyền.'),
  });
  const revoke = useMutation({
    mutationFn: (g: GrantOut) => api.revokeAccess(g.user_id),
    onSuccess: (_data, g) => {
      setNotice(`Đã thu hồi quyền của "${g.login}".`);
      setConfirm(null);
      void queryClient.invalidateQueries({ queryKey: ACCESS_KEY });
    },
  });

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    setNotice(null);
    setFormError(null);
    if (!login.trim()) {
      setFormError('Hãy nhập tên đăng nhập.');
      return;
    }
    grant.mutate();
  }

  const grants = list.data ?? [];

  return (
    <AdminLayout>
      <div className="page-title">
        <div>
          <h1>Quản lý quyền sử dụng</h1>
          <p className="muted" style={{ margin: '4px 0 0' }}>
            Chỉ người được cấp quyền mới dùng được ứng dụng. Phạm vi chia sẻ tài liệu: <TbdTag id="OQ-003" />
          </p>
        </div>
      </div>

      {confirm && (
        <ErrorBanner
          tone="warn"
          title={`Thu hồi quyền của "${confirm.login}"?`}
          actions={
            <>
              <button className="btn btn-sm" type="button" onClick={() => setConfirm(null)} autoFocus>
                Hủy
              </button>
              <button
                className="btn btn-sm btn-danger"
                type="button"
                disabled={revoke.isPending}
                onClick={() => revoke.mutate(confirm)}
              >
                Thu hồi
              </button>
            </>
          }
        >
          Người này sẽ không đăng nhập được và không truy vấn được tài liệu nữa.
          {revoke.isError && ' Chưa thu hồi được, hãy thử lại.'}
        </ErrorBanner>
      )}
      {notice && (
        <div className="banner banner-info" role="status">
          <span aria-hidden="true">ℹ</span>
          <div>{notice}</div>
        </div>
      )}

      <section className="card" aria-labelledby="add-title" style={{ marginBottom: 16 }}>
        <form className="toolbar" onSubmit={onSubmit} noValidate>
          <h2 id="add-title" style={{ width: '100%' }}>
            Cấp quyền cho người dùng
          </h2>
          <div className="field">
            <label htmlFor="grant-login">Tên đăng nhập</label>
            <input
              id="grant-login"
              type="text"
              placeholder="ví dụ: ten.ho@congty.vn"
              value={login}
              onChange={(e) => setLogin(e.target.value)}
              aria-invalid={formError ? true : undefined}
              aria-describedby={formError ? 'grant-error' : undefined}
            />
            {formError && (
              <div className="field-error" id="grant-error" role="alert">
                {formError}
              </div>
            )}
          </div>
          <div className="field">
            <label htmlFor="grant-role">Vai trò</label>
            <select id="grant-role" value={role} onChange={(e) => setRole(e.target.value as Role)}>
              <option value="bd">Nhân sự BD</option>
              <option value="manager">Quản lý</option>
              <option value="security_admin">Quản trị bảo mật</option>
            </select>
          </div>
          <button className="btn btn-primary" type="submit" disabled={grant.isPending}>
            Cấp quyền
          </button>
        </form>
      </section>

      <section className="card" aria-labelledby="list-title">
        <div className="toolbar">
          <h2 id="list-title">Người dùng đã được cấp quyền</h2>
        </div>
        {list.isError && (
          <div className="card-pad">
            <ErrorBanner
              actions={
                <button className="btn btn-sm" type="button" onClick={() => void list.refetch()}>
                  Thử lại
                </button>
              }
            >
              Không tải được danh sách người dùng.
            </ErrorBanner>
          </div>
        )}
        {list.isSuccess && grants.length === 0 && (
          <EmptyState icon="👤" title="Chưa có người dùng nào được cấp quyền">
            <p>Hãy nhập tên đăng nhập ở phần trên rồi chọn "Cấp quyền".</p>
          </EmptyState>
        )}
        {grants.length > 0 && (
          <div className="table-wrap">
            <table>
              <caption className="sr-only">Danh sách người dùng và vai trò</caption>
              <thead>
                <tr>
                  <th scope="col">Người dùng</th>
                  <th scope="col">Vai trò</th>
                  <th scope="col">Phạm vi tài liệu</th>
                  <th scope="col">Trạng thái</th>
                  <th scope="col">Thao tác</th>
                </tr>
              </thead>
              <tbody>
                {grants.map((g) => (
                  <tr key={g.user_id}>
                    <td>{g.login}</td>
                    <td>{roleLabel(g.role)}</td>
                    <td>{g.role === 'bd' ? <TbdTag id="OQ-003" /> : 'Không áp dụng'}</td>
                    <td>
                      <StatusBadge status={g.status === 'active' ? 'active' : 'revoked'} />
                    </td>
                    <td>
                      {g.status === 'active' && g.user_id !== me?.user.id && (
                        <button
                          className="btn-link"
                          type="button"
                          onClick={() => {
                            setNotice(null);
                            setConfirm(g);
                          }}
                          aria-label={`Thu hồi quyền của ${g.login}`}
                        >
                          Thu hồi quyền
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </AdminLayout>
  );
}
