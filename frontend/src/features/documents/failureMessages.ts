// US-004 (AC-018): câu thông báo tiếng Việt theo mã `failure_reason`, nêu cách khắc phục.
// Mã không biết → câu chung; không bao giờ hiện mã kỹ thuật cho người dùng.
// Danh sách cuối cùng chờ thống nhất với BR-018 (ghi chú ở US-004).

const MESSAGES: Record<string, string> = {
  corrupted: 'Tệp bị hỏng hoặc không đọc được. Hãy mở thử tệp trên máy, lưu lại bản PDF mới rồi tải lại.',
  encrypted: 'Tài liệu bị khóa hoặc mã hóa. Hãy mở khóa rồi tải lại.',
  not_pdf: 'Tệp không phải PDF. Hãy chuyển tài liệu sang định dạng PDF rồi tải lại.',
  too_large: 'Tệp vượt quá dung lượng cho phép. Hãy tách hoặc nén tài liệu rồi tải lại.',
  no_text:
    'Tài liệu không có văn bản đọc được (có thể là bản scan dạng ảnh). Hiện chưa hỗ trợ loại tệp này; hãy dùng bản PDF có văn bản.',
  network: 'Mất kết nối khi tải lên. Tệp chưa nằm trong tập tài liệu; hãy tải lại khi có mạng.',
  internal: 'Hệ thống chưa xử lý được tệp này. Hãy thử lại sau ít phút.',
  too_many_documents:
    'Bạn đã đạt số lượng tài liệu tối đa. Hãy xóa bớt tài liệu không dùng rồi tải lại.',
};

export const GENERIC_FAILURE =
  'Không xử lý được tệp này. Hãy thử lại; nếu vẫn lỗi, hãy liên hệ bộ phận hỗ trợ.';

export const KNOWN_FAILURE_CODES = Object.keys(MESSAGES);

export function failureMessage(code: string | null | undefined): string {
  if (!code) return GENERIC_FAILURE;
  return Object.prototype.hasOwnProperty.call(MESSAGES, code) ? MESSAGES[code] : GENERIC_FAILURE;
}
