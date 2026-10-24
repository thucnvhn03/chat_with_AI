// T2-07 (khung hội thoại, ô nhập), T2-08 (thẻ câu trả lời, nguồn, không tìm thấy), T2-10 (lỗi khi hỏi),
// T2-11 (sự kiện mở nguồn), T3-05 (lịch sử, hội thoại mới), T3-06 (chỉ báo chờ, Hủy, quá thời gian),
// T4-03 (đánh giá).
import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import type { AnswerOut } from '../../api/client';
import { apiError, makeMe, mockApi, renderApp, seriousViolations, type Handler } from '../../test/utils';
import { CONVERSATION_KEY } from './useChat';

const READY = [
  { id: 'd1', file_name: 'HopDong_A.pdf', size_bytes: 1, page_count: 12, status: 'ready', failure_reason: null, uploaded_at: '2026-10-20T00:00:00Z' },
];

const ANSWER: AnswerOut = {
  message_id: 'm1',
  answer: 'Hợp đồng A quy định thanh toán thành hai đợt.',
  not_found: false,
  citations: [
    { document_id: 'd1', document_name: 'HopDong_A.pdf', page: 5, cited_text: 'thanh toán thành hai đợt' },
    { document_id: 'd2', document_name: 'BaoGia_B.pdf', page: 2, cited_text: 'đợt hai' },
  ],
  latency_ms: 1200,
};

function setup(ask: Handler, extra: Record<string, Handler> = {}) {
  const api = mockApi({
    'GET /auth/me': () => makeMe('bd', { max_question_chars: 50 }),
    'GET /documents': () => READY,
    'POST /conversations': () => ({ id: 'c1' }),
    'POST /conversations/c1/messages': ask,
    ...extra,
  });
  const view = renderApp('/');
  return { api, ...view };
}

async function ask(question: string) {
  const input = await screen.findByLabelText('Câu hỏi của bạn');
  await waitFor(() => expect(input).toBeEnabled());
  const user = userEvent.setup();
  await user.type(input, question);
  await user.click(screen.getByRole('button', { name: 'Gửi' }));
  return input;
}

describe('Hỏi đáp', () => {
  it('câu trả lời có nguồn: chip "tên, tr.N", tiêu điểm quay về ô nhập, không vi phạm axe', async () => {
    const { container } = setup(() => ANSWER);
    const input = await ask('Điều khoản thanh toán của hợp đồng A là gì?');
    const card = await screen.findByRole('article', { name: 'Câu trả lời' });
    expect(card).toHaveTextContent('Hợp đồng A quy định thanh toán thành hai đợt.');
    const chips = within(card).getAllByRole('link');
    expect(chips.map((c) => c.textContent)).toEqual(['📄 HopDong_A.pdf, tr.5', '📄 BaoGia_B.pdf, tr.2']);
    expect(chips[0]).toHaveAttribute('href', '/sources/d1?page=5');
    await waitFor(() => expect(input).toHaveFocus());
    expect(input).toHaveValue('');
    expect(await seriousViolations(container)).toEqual([]);
  });

  it('không tìm thấy: khối cảnh báo kèm gợi ý, không có chip nguồn', async () => {
    setup(() => ({ ...ANSWER, not_found: true, citations: [], answer: 'Không tìm thấy...' }));
    await ask('Còn điều khoản phạt khi giao trễ?');
    const notice = await screen.findByRole('status');
    expect(notice).toHaveTextContent('Không tìm thấy thông tin này trong các tài liệu đã tải lên.');
    expect(notice).toHaveTextContent('bổ sung tài liệu có liên quan hoặc đổi cách đặt câu hỏi');
    expect(screen.queryByRole('link', { name: /mở trang nguồn/ })).not.toBeInTheDocument();
  });

  it('nội dung có <script> hiển thị nguyên văn, không thực thi', async () => {
    const payload = '<script>window.__xss = 1</script><img src=x onerror="window.__xss=2">';
    setup(() => ({ ...ANSWER, answer: payload }));
    await ask('Câu hỏi?');
    const card = await screen.findByRole('article', { name: 'Câu trả lời' });
    expect(card).toHaveTextContent(payload);
    expect(card.querySelector('script, img')).toBeNull();
    expect((window as unknown as { __xss?: number }).__xss).toBeUndefined();
  });

  it('chỉ báo "Đang xử lý câu hỏi…" xuất hiện ngay khi gửi; Hủy trả câu hỏi về ô nhập', async () => {
    let release: (v: unknown) => void = () => undefined;
    setup(() => new Promise((resolve) => (release = resolve)));
    const input = await ask('Câu hỏi chờ lâu');
    const thinking = await screen.findByText('Đang xử lý câu hỏi…', {}, { timeout: 300 });
    expect(thinking).toBeInTheDocument();
    expect(input).toBeDisabled();
    await userEvent.click(screen.getByRole('button', { name: 'Hủy' }));
    await waitFor(() => expect(screen.queryByText('Đang xử lý câu hỏi…')).not.toBeInTheDocument());
    expect(input).toHaveValue('Câu hỏi chờ lâu');
    release(ANSWER);
    expect(screen.queryByRole('article', { name: 'Câu trả lời' })).not.toBeInTheDocument();
  });

  it('gửi bằng Ctrl+Enter', async () => {
    const { api } = setup(() => ANSWER);
    const input = await screen.findByLabelText('Câu hỏi của bạn');
    await waitFor(() => expect(input).toBeEnabled());
    await userEvent.type(input, 'Hỏi nhanh{Control>}{Enter}{/Control}');
    await screen.findByRole('article', { name: 'Câu trả lời' });
    expect(api.calls.find((c) => c.method === 'POST' && c.path.endsWith('/messages'))?.body).toEqual({
      question: 'Hỏi nhanh',
    });
  });

  it('câu hỏi quá dài: báo số ký tự và không cho gửi', async () => {
    setup(() => ANSWER);
    const input = await screen.findByLabelText('Câu hỏi của bạn');
    await waitFor(() => expect(input).toBeEnabled());
    await userEvent.type(input, 'x'.repeat(51));
    expect(screen.getByText(/Câu hỏi dài 51\/50 ký tự/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Gửi' })).toBeDisabled();
  });

  it('chưa có tài liệu sẵn sàng: ô nhập vô hiệu kèm giải thích', async () => {
    mockApi({
      'GET /auth/me': () => makeMe(),
      'GET /documents': () => [{ ...READY[0], status: 'processing' }],
    });
    renderApp('/');
    const input = await screen.findByLabelText('Câu hỏi của bạn');
    expect(input).toBeDisabled();
    expect(screen.getByText(/Ô nhập sẽ mở khi có ít nhất một tài liệu ở trạng thái "Sẵn sàng"/)).toBeInTheDocument();
  });
});

describe('Lỗi khi hỏi (s02-offline-ask)', () => {
  it('mất mạng: giữ câu hỏi, nút "Gửi lại", không có câu trả lời dở dang; gửi lại được', async () => {
    // fetch ném TypeError như khi mất mạng
    const { api } = setup(() => {
      throw new TypeError('Failed to fetch');
    });
    const input = await ask('Điều khoản thanh toán của hợp đồng A là gì?');
    expect(await screen.findByText('Mất kết nối, chưa nhận được câu trả lời.')).toBeInTheDocument();
    expect(screen.getByText('Không gửi được câu hỏi này. Chưa có câu trả lời.')).toBeInTheDocument();
    expect(input).toHaveValue('Điều khoản thanh toán của hợp đồng A là gì?');
    expect(screen.queryByRole('article', { name: 'Câu trả lời' })).not.toBeInTheDocument();

    api.set('POST /conversations/c1/messages', () => ANSWER);
    await userEvent.click(screen.getByRole('button', { name: 'Gửi lại' }));
    expect(await screen.findByRole('article', { name: 'Câu trả lời' })).toBeInTheDocument();
    expect(screen.queryByText('Mất kết nối, chưa nhận được câu trả lời.')).not.toBeInTheDocument();
  });

  it('504: thông báo quá thời gian kèm "Thử lại"', async () => {
    const { api } = setup(() => apiError(504, 'answer_timeout', 'Hệ thống trả lời quá lâu.'));
    await ask('Câu hỏi chậm');
    expect(await screen.findByText(/Hệ thống trả lời quá lâu nên đã dừng chờ/)).toBeInTheDocument();
    api.set('POST /conversations/c1/messages', () => ANSWER);
    await userEvent.click(screen.getByRole('button', { name: 'Thử lại' }));
    expect(await screen.findByRole('article', { name: 'Câu trả lời' })).toBeInTheDocument();
  });

  it('502: thông báo chung từ máy chủ', async () => {
    setup(() => apiError(502, 'answer_unavailable', 'Chưa trả lời được lúc này. Hãy thử lại sau ít phút.'));
    await ask('Câu hỏi');
    expect(await screen.findByText('Chưa trả lời được lúc này. Hãy thử lại sau ít phút.')).toBeInTheDocument();
  });
});

describe('Nguồn, đánh giá, lịch sử', () => {
  it('chọn chip phát source_opened chỉ với id tài liệu và số trang', async () => {
    const { api } = setup(() => ANSWER, {
      'POST /events/source-opened': () => undefined,
      'GET /documents/d1/pages/5': () => ({ page: 5, page_count: 12, text: 'Văn bản', document_name: 'HopDong_A.pdf' }),
    });
    await ask('Điều khoản thanh toán?');
    await userEvent.click(await screen.findByRole('link', { name: 'HopDong_A.pdf, tr.5 – mở trang nguồn' }));
    await waitFor(() =>
      expect(api.calls.find((c) => c.path === '/events/source-opened')?.body).toEqual({ document_id: 'd1', page: 5 }),
    );
  });

  it('đánh giá: aria-pressed, đổi lại được', async () => {
    const { api } = setup(() => ANSWER, { 'PUT /messages/m1/feedback': () => undefined });
    await ask('Điều khoản thanh toán?');
    const helpful = await screen.findByRole('button', { name: /Hữu ích/ });
    const notHelpful = screen.getByRole('button', { name: /Không hữu ích/ });
    expect(helpful).toHaveAttribute('aria-pressed', 'false');
    await userEvent.click(helpful);
    expect(helpful).toHaveAttribute('aria-pressed', 'true');
    await userEvent.click(notHelpful);
    expect(notHelpful).toHaveAttribute('aria-pressed', 'true');
    expect(helpful).toHaveAttribute('aria-pressed', 'false');
    await waitFor(() =>
      expect(api.calls.filter((c) => c.path === '/messages/m1/feedback').map((c) => c.body)).toEqual([
        { value: 'helpful' },
        { value: 'not_helpful' },
      ]),
    );
  });

  it('khôi phục lịch sử trong phiên; "Hội thoại mới" xóa ngữ cảnh', async () => {
    window.sessionStorage.setItem(CONVERSATION_KEY, 'c1');
    const { api } = setup(() => ANSWER, {
      'GET /conversations/c1/messages': () => [
        { id: 'q1', role: 'user', content: 'Câu hỏi cũ', not_found: false, latency_ms: null, created_at: '', citations: [], feedback: null },
        { id: 'a1', role: 'assistant', content: 'Trả lời cũ', not_found: false, latency_ms: 10, created_at: '', citations: ANSWER.citations, feedback: 'helpful' },
      ],
    });
    expect(await screen.findByText('Câu hỏi cũ')).toBeInTheDocument();
    expect(screen.getByText('Trả lời cũ')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Hữu ích' })).toHaveAttribute('aria-pressed', 'true');

    await userEvent.click(screen.getByRole('button', { name: 'Hội thoại mới' }));
    expect(screen.queryByText('Câu hỏi cũ')).not.toBeInTheDocument();
    expect(window.sessionStorage.getItem(CONVERSATION_KEY)).toBeNull();
    api.set('POST /conversations', () => ({ id: 'c1' }));
    await ask('Câu hỏi mới');
    await screen.findByRole('article', { name: 'Câu trả lời' });
    expect(api.calls.filter((c) => c.method === 'POST' && c.path === '/conversations')).toHaveLength(1);
  });
});
