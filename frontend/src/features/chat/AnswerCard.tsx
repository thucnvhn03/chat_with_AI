// C-11 AnswerCard và C-15 NotFoundNotice (US-008, US-011, US-014).
// Nội dung câu trả lời hiển thị dưới dạng VĂN BẢN đã thoát ký tự (React), không render HTML từ mô hình.
import { FeedbackControl } from './FeedbackControl';
import { SourceChip } from './SourceChip';
import type { AnswerView } from './useChat';

export function NotFoundNotice() {
  return (
    <div className="notfound" role="status">
      <strong>Không tìm thấy thông tin này trong các tài liệu đã tải lên.</strong>
      <p style={{ margin: '6px 0 0' }}>Bạn có thể bổ sung tài liệu có liên quan hoặc đổi cách đặt câu hỏi.</p>
    </div>
  );
}

interface Props {
  answer: AnswerView;
  onFeedback: (value: string | null) => void;
}

export function AnswerCard({ answer, onFeedback }: Props) {
  if (answer.notFound) return <NotFoundNotice />;
  const paragraphs = answer.text.split(/\n{2,}/).filter((p) => p.trim());
  return (
    <article className="msg msg-ai" aria-label="Câu trả lời">
      {paragraphs.map((p, i) => (
        <p key={i} style={{ whiteSpace: 'pre-line' }}>
          {p}
        </p>
      ))}
      {answer.citations.length > 0 && (
        <div className="sources">
          <span className="label">Nguồn:</span>
          {answer.citations.map((c) => (
            <SourceChip
              key={`${c.document_id}-${c.page}`}
              citation={c}
              allCitations={answer.citations}
            />
          ))}
        </div>
      )}
      <FeedbackControl messageId={answer.messageId} value={answer.feedback} onChange={onFeedback} />
    </article>
  );
}
