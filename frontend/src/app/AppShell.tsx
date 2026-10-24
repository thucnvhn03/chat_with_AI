// C-00 AppShell: liên kết bỏ qua, header (thương hiệu, người dùng, đăng xuất), vùng nội dung.
import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { homeFor, useAuth } from './auth';

const ROLE_LABEL: Record<string, string> = {
  bd: 'Nhân sự BD',
  manager: 'Quản lý',
  security_admin: 'Quản trị bảo mật',
};

export function roleLabel(role: string): string {
  return ROLE_LABEL[role] ?? role;
}

interface Props {
  children: ReactNode;
  /** id của vùng nội dung chính mà liên kết "bỏ qua" trỏ tới */
  mainId?: string;
  skipLabel?: string;
}

export function AppShell({ children, mainId = 'main', skipLabel = 'Bỏ qua tới nội dung chính' }: Props) {
  const { me, logout } = useAuth();
  return (
    <>
      <a className="skip-link" href={`#${mainId}`}>
        {skipLabel}
      </a>
      <header className="app-header">
        <Link className="brand" to={homeFor(me?.role)}>
          <span className="brand-mark" aria-hidden="true">
            C
          </span>{' '}
          Chat với tài liệu
        </Link>
        <div className="header-right">
          {me && (
            <span className="user-chip">
              {roleLabel(me.role)} ({me.user.display_name ?? me.user.login})
            </span>
          )}
          <button className="btn btn-sm" type="button" onClick={() => void logout()}>
            Đăng xuất
          </button>
        </div>
      </header>
      {children}
    </>
  );
}
