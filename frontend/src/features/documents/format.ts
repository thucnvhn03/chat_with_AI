// Định dạng số liệu hiển thị theo kiểu Việt Nam (dấu phẩy thập phân).

export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toLocaleString('vi-VN', { maximumFractionDigits: 0 })} KB`;
  return `${(bytes / (1024 * 1024)).toLocaleString('vi-VN', { maximumFractionDigits: 1 })} MB`;
}

export function formatHours(hours: number): string {
  if (hours >= 24 && hours % 24 === 0) return `${hours / 24} ngày`;
  return `${hours.toLocaleString('vi-VN')} giờ`;
}
