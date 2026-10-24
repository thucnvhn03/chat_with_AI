// Tìm đoạn trích (`cited_text`) trong văn bản trang để tô sáng. Khoảng trắng được so khớp linh hoạt vì
// mô hình có thể trả đoạn trích với ngắt dòng khác văn bản trang. Không tìm thấy → không tô sáng.

export interface Highlight {
  before: string;
  match: string;
  after: string;
}

function escapeRegExp(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

export function findHighlight(pageText: string, cited: string | null | undefined): Highlight | null {
  const needle = cited?.normalize('NFC').trim();
  if (!needle) return null;
  const pattern = needle.split(/\s+/).map(escapeRegExp).join('\\s+');
  const match = new RegExp(pattern, 'u').exec(pageText.normalize('NFC'));
  if (!match) return null;
  const text = pageText.normalize('NFC');
  return {
    before: text.slice(0, match.index),
    match: match[0],
    after: text.slice(match.index + match[0].length),
  };
}
