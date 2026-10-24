// T1-19 (AC-018): mỗi mã lỗi trả đúng một câu không rỗng; mã lạ trả câu chung, không lộ mã kỹ thuật.
import { describe, expect, it } from 'vitest';
import { failureMessage, GENERIC_FAILURE, KNOWN_FAILURE_CODES } from './failureMessages';

describe('failureMessage', () => {
  const required = ['corrupted', 'encrypted', 'not_pdf', 'too_large', 'no_text', 'network', 'internal'];

  it('có câu cho mọi mã bắt buộc', () => {
    for (const code of required) expect(KNOWN_FAILURE_CODES).toContain(code);
  });

  it.each(required)('%s → một câu tiếng Việt không rỗng, khác câu chung, không chứa mã', (code) => {
    const message = failureMessage(code);
    expect(message.trim().length).toBeGreaterThan(10);
    expect(message).not.toBe(GENERIC_FAILURE);
    expect(message).not.toContain(code);
  });

  it('câu mẫu cho tài liệu mã hóa', () => {
    expect(failureMessage('encrypted')).toBe('Tài liệu bị khóa hoặc mã hóa. Hãy mở khóa rồi tải lại.');
  });

  it('các mã khác nhau cho câu khác nhau', () => {
    const messages = new Set(KNOWN_FAILURE_CODES.map(failureMessage));
    expect(messages.size).toBe(KNOWN_FAILURE_CODES.length);
  });

  it.each(['virus_detected', '', null, undefined, '__proto__', 'toString'])(
    'mã lạ %s → câu chung',
    (code) => {
      expect(failureMessage(code as string | null | undefined)).toBe(GENERIC_FAILURE);
    },
  );
});
