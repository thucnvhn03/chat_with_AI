// Khung khu vực quản trị bảo mật: điều hướng bên (S-05, S-06).
import type { ReactNode } from 'react';
import { NavLink } from 'react-router-dom';
import { AppShell } from '../../app/AppShell';

export function AdminLayout({ children }: { children: ReactNode }) {
  return (
    <AppShell>
      <div className="admin">
        <nav className="side-nav" aria-label="Khu vực quản trị">
          <NavLink to="/admin/access">Quản lý quyền</NavLink>
          <NavLink to="/admin/audit">Bản ghi kiểm toán</NavLink>
        </nav>
        <main id="main" tabIndex={-1}>
          {children}
        </main>
      </div>
    </AppShell>
  );
}
