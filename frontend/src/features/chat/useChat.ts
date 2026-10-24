// Trạng thái hội thoại (US-008, US-010, US-013). Hội thoại chỉ giữ trong phiên trình duyệt (PQ-004):
// id hội thoại nằm trong sessionStorage, lịch sử đọc lại từ GET /conversations/{id}/messages.
import { useCallback, useEffect, useRef, useState } from 'react';
import { api, ApiError, NetworkError, type CitationOut } from '../../api/client';
import { storage } from '../../app/storage';

export interface AnswerView {
  messageId: string;
  text: string;
  notFound: boolean;
  citations: CitationOut[];
  feedback: string | null;
}

export interface Turn {
  key: string;
  question: string;
  answer: AnswerView;
}

export type AskErrorKind = 'network' | 'timeout' | 'unavailable' | 'error';

export interface AskError {
  kind: AskErrorKind;
  question: string;
  message?: string;
}

export const CONVERSATION_KEY = 'cwd.conversation';

function classify(err: unknown): AskErrorKind {
  if (err instanceof NetworkError) return 'network';
  if (err instanceof ApiError && err.status === 504) return 'timeout';
  if (err instanceof ApiError && err.status === 502) return 'unavailable';
  return 'error';
}

export function useChat() {
  const [conversationId, setConversationId] = useState<string | null>(() => storage.get(CONVERSATION_KEY));
  const [turns, setTurns] = useState<Turn[]>([]);
  const [pending, setPending] = useState<string | null>(null);
  const [error, setError] = useState<AskError | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const controller = useRef<AbortController | null>(null);

  // Đọc lại lịch sử khi quay về từ trình xem nguồn hoặc tải lại trang — CHỈ cho hội thoại có sẵn lúc mở
  // trang. Hội thoại vừa tạo khi gửi câu hỏi đầu tiên không cần đọc lại (và nếu đọc, kết quả rỗng về muộn
  // có thể ghi đè câu trả lời vừa nhận).
  const initialConversation = useRef(conversationId);
  useEffect(() => {
    const conversationId = initialConversation.current;
    if (!conversationId) return;
    let cancelled = false;
    setHistoryLoading(true);
    api
      .messages(conversationId)
      .then((messages) => {
        if (cancelled) return;
        const restored: Turn[] = [];
        for (let i = 0; i + 1 < messages.length; i += 2) {
          const q = messages[i];
          const a = messages[i + 1];
          if (q.role !== 'user' || a.role !== 'assistant') continue;
          restored.push({
            key: a.id,
            question: q.content,
            answer: {
              messageId: a.id,
              text: a.content,
              notFound: a.not_found,
              citations: a.citations,
              feedback: a.feedback ?? null,
            },
          });
        }
        // Không ghi đè nếu người dùng đã kịp hỏi thêm trong lúc chờ
        setTurns((current) => (current.length > 0 ? current : restored));
      })
      .catch((err: unknown) => {
        // Hội thoại không còn (hoặc của phiên khác): bắt đầu hội thoại mới
        if (!cancelled && err instanceof ApiError && err.status === 404) {
          storage.remove(CONVERSATION_KEY);
          setConversationId(null);
        }
      })
      .finally(() => !cancelled && setHistoryLoading(false));
    return () => {
      cancelled = true;
    };
  }, []);

  const send = useCallback(
    async (question: string): Promise<boolean> => {
      setError(null);
      setPending(question);
      const abort = new AbortController();
      controller.current = abort;
      try {
        let id = conversationId;
        if (!id) {
          id = (await api.createConversation()).id;
          storage.set(CONVERSATION_KEY, id);
          setConversationId(id);
        }
        const result = await api.ask(id, question, abort.signal);
        setTurns((current) => [
          ...current,
          {
            key: result.message_id,
            question,
            answer: {
              messageId: result.message_id,
              text: result.answer,
              notFound: result.not_found,
              citations: result.citations,
              feedback: null,
            },
          },
        ]);
        return true;
      } catch (err) {
        if (err instanceof DOMException && err.name === 'AbortError') return false;
        if (err instanceof ApiError && err.status === 401) return false;
        setError({
          kind: classify(err),
          question,
          message: err instanceof ApiError ? err.message : undefined,
        });
        return false;
      } finally {
        if (controller.current === abort) controller.current = null;
        setPending(null);
      }
    },
    [conversationId],
  );

  /** Hủy yêu cầu phía trình duyệt (US-013). Câu hỏi được trả lại ô nhập. */
  const cancel = useCallback(() => {
    controller.current?.abort();
  }, []);

  const newConversation = useCallback(() => {
    controller.current?.abort();
    storage.remove(CONVERSATION_KEY);
    setConversationId(null);
    setTurns([]);
    setError(null);
  }, []);

  const setFeedback = useCallback((messageId: string, value: string | null) => {
    setTurns((current) =>
      current.map((t) =>
        t.answer.messageId === messageId ? { ...t, answer: { ...t.answer, feedback: value } } : t,
      ),
    );
  }, []);

  return {
    turns,
    pending,
    error,
    historyLoading,
    send,
    cancel,
    newConversation,
    setFeedback,
    clearError: () => setError(null),
  };
}
