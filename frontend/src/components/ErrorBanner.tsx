// C-16 ErrorBanner: thông báo tại chỗ, có vai trò `alert` cho trình đọc màn hình.
import type { ReactNode } from 'react';

interface Props {
  title?: ReactNode;
  children?: ReactNode;
  tone?: 'err' | 'warn' | 'info';
  icon?: string;
  actions?: ReactNode;
  style?: React.CSSProperties;
}

const DEFAULT_ICON = { err: '⚠', warn: '⚠', info: 'ℹ' } as const;

export function ErrorBanner({ title, children, tone = 'err', icon, actions, style }: Props) {
  return (
    <div
      className={`banner banner-${tone}`}
      role={tone === 'info' ? 'note' : 'alert'}
      style={style}
    >
      <span aria-hidden="true">{icon ?? DEFAULT_ICON[tone]}</span>
      <div>
        {title && <strong>{title}</strong>} {children}
      </div>
      {actions && <div className="banner-actions">{actions}</div>}
    </div>
  );
}
