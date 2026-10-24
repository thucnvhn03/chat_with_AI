// C-07 ChatPanel, C-08 MessageList: chuỗi hỏi đáp, chỉ báo chờ có nút Hủy, lỗi khi hỏi, ô nhập.
import { useEffect, useRef, useState } from 'react';
import { DRAFT_KEY, storage } from '../../app/storage';
import { EmptyState } from '../../components/EmptyState';
import { ErrorBanner } from '../../components/ErrorBanner';
import { AnswerCard } from './AnswerCard';
import { QuestionInput } from './QuestionInput';
import type { useChat } from './useChat';

interface Props {
  chat: ReturnType<typeof useChat>;
  hasDocuments: boolean;
  hasReady: boolean;
  maxQuestionChars?: number;
}

export function ChatPanel({ chat, hasDocuments, hasReady, maxQuestionChars }: Props) {
  const [draft, setDraft] = useState(() => storage.get(DRAFT_KEY) ?? '');
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const { turns, pending, error } = chat;

  useEffect(() => {
    endRef.current?.scrollIntoView?.({ block: 'end' });
  }, [turns.length, pending, error]);

  async function submitQuestion(question: string) {
    if (!question) return;
    setDraft('');
    const ok = await chat.send(question);
    // Bản nháp trong sessionStorage chỉ xóa khi đã có câu trả lời: gặp 401 giữa chừng thì câu hỏi vẫn còn
    // sau khi đăng nhập lại. Lỗi hoặc hủy: trả câu hỏi về ô nhập để gửi lại.
    if (ok) storage.remove(DRAFT_KEY);
    else setDraft((current) => current || question);
    setTimeout(() => inputRef.current?.focus(), 0);
  }

  const waiting = pending !== null;
  const disabled = !hasReady || waiting;
  const placeholder = waiting
    ? 'Đang chờ câu trả lời…'
    : !hasDocuments
      ? 'Hãy tải tài liệu lên trước khi đặt câu hỏi'
      : !hasReady
        ? 'Tài liệu đang được xử lý, hãy chờ trong giây lát…'
        : 'Nhập câu hỏi về nội dung tài liệu…';
  const showEmpty = !hasDocuments && turns.length === 0 && !waiting;

  return (
    <section id="chat" className="card panel" aria-labelledby="chat-title" tabIndex={-1}>
      <div className="panel-head">
        <h2 id="chat-title">Hội thoại</h2>
        <div className="panel-head-actions">
          <span className="small muted">Câu trả lời chỉ dựa trên các tài liệu bạn đã tải lên</span>
          {turns.length > 0 && (
            <button className="btn btn-sm" type="button" onClick={chat.newConversation} disabled={waiting}>
              Hội thoại mới
            </button>
          )}
        </div>
      </div>
      <div className="panel-body" aria-live="polite">
        {showEmpty && (
          <EmptyState icon="💬" title="Bắt đầu bằng việc tải tài liệu lên">
            <p>
              Khi có tài liệu sẵn sàng, bạn có thể hỏi bằng câu tự nhiên, ví dụ: "Điều khoản thanh toán của
              hợp đồng A là gì?"
            </p>
          </EmptyState>
        )}
        <div className="messages">
          {turns.map((turn) => (
            <div key={turn.key} style={{ display: 'contents' }}>
              <div className="msg msg-user">{turn.question}</div>
              <AnswerCard
                answer={turn.answer}
                onFeedback={(value) => chat.setFeedback(turn.answer.messageId, value)}
              />
            </div>
          ))}
          {waiting && (
            <>
              <div className="msg msg-user">{pending}</div>
              <div className="thinking" role="status">
                <span className="dots" aria-hidden="true">
                  <i />
                  <i />
                  <i />
                </span>
                <span>Đang xử lý câu hỏi…</span>
                <button className="btn btn-sm" type="button" onClick={chat.cancel}>
                  Hủy
                </button>
              </div>
            </>
          )}
          {error && (
            <>
              <div className="msg msg-user">{error.question}</div>
              <ErrorBanner
                style={{ maxWidth: '86%', margin: 0 }}
                actions={
                  error.kind === 'timeout' ? (
                    <button
                      className="btn btn-sm"
                      type="button"
                      onClick={() => {
                        chat.clearError();
                        void submitQuestion(error.question);
                      }}
                    >
                      Thử lại
                    </button>
                  ) : undefined
                }
              >
                {error.kind === 'network' && 'Không gửi được câu hỏi này. Chưa có câu trả lời.'}
                {error.kind === 'timeout' &&
                  'Hệ thống trả lời quá lâu nên đã dừng chờ. Câu hỏi vẫn được giữ trong ô nhập.'}
                {error.kind === 'unavailable' &&
                  (error.message ?? 'Chưa trả lời được lúc này. Hãy thử lại sau ít phút.')}
                {error.kind === 'error' && (error.message ?? 'Đã có lỗi xảy ra. Hãy thử lại sau.')}
              </ErrorBanner>
            </>
          )}
          <div ref={endRef} />
        </div>
      </div>
      <QuestionInput
        ref={inputRef}
        value={draft}
        onChange={(value) => {
          setDraft(value);
          storage.set(DRAFT_KEY, value);
        }}
        onSubmit={() => void submitQuestion(draft.trim())}
        disabled={disabled}
        placeholder={placeholder}
        submitLabel={error?.kind === 'network' ? 'Gửi lại' : 'Gửi'}
        maxChars={maxQuestionChars}
        hint={!hasReady && !waiting ? 'Ô nhập sẽ mở khi có ít nhất một tài liệu ở trạng thái "Sẵn sàng".' : undefined}
      />
    </section>
  );
}
