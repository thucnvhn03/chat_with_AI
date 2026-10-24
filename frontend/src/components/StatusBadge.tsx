// C-06 StatusBadge: huy hiệu trạng thái luôn có chữ, không chỉ dùng màu.

export type BadgeStatus =
  | 'ready'
  | 'processing'
  | 'uploading'
  | 'failed'
  | 'incomplete'
  | 'active'
  | 'revoked';

const BADGES: Record<BadgeStatus, { className: string; icon: string; label: string }> = {
  ready: { className: 'badge-ok', icon: '✔', label: 'Sẵn sàng' },
  processing: { className: 'badge-warn', icon: '⏳', label: 'Đang xử lý' },
  uploading: { className: 'badge-info', icon: '⬆', label: 'Đang tải lên' },
  failed: { className: 'badge-err', icon: '✖', label: 'Lỗi' },
  incomplete: { className: 'badge-err', icon: '✖', label: 'Chưa tải xong' },
  active: { className: 'badge-ok', icon: '✔', label: 'Đang hoạt động' },
  revoked: { className: 'badge-err', icon: '✖', label: 'Đã thu hồi' },
};

export function StatusBadge({ status }: { status: BadgeStatus }) {
  const badge = BADGES[status];
  return (
    <span className={`badge ${badge.className}`}>
      <span aria-hidden="true">{badge.icon}</span> {badge.label}
    </span>
  );
}
