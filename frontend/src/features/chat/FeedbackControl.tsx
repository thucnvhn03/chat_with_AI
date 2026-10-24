// C-13 FeedbackControl (US-024): hai nút "Hữu ích"/"Không hữu ích" với aria-pressed; đổi lại được.
import { useState } from 'react';
import { api } from '../../api/client';

type Value = 'helpful' | 'not_helpful';

interface Props {
  messageId: string;
  value: string | null;
  onChange: (value: string | null) => void;
}

export function FeedbackControl({ messageId, value, onChange }: Props) {
  const [saving, setSaving] = useState(false);
  const [failed, setFailed] = useState(false);

  async function choose(next: Value) {
    if (next === value || saving) return;
    const previous = value;
    onChange(next);
    setSaving(true);
    setFailed(false);
    try {
      await api.feedback(messageId, next);
    } catch {
      onChange(previous);
      setFailed(true);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="feedback" role="group" aria-label="Đánh giá câu trả lời">
      Câu trả lời này
      <button
        className="btn btn-sm"
        type="button"
        aria-pressed={value === 'helpful'}
        onClick={() => void choose('helpful')}
      >
        <span aria-hidden="true">👍</span> Hữu ích
      </button>
      <button
        className="btn btn-sm"
        type="button"
        aria-pressed={value === 'not_helpful'}
        onClick={() => void choose('not_helpful')}
      >
        <span aria-hidden="true">👎</span> Không hữu ích
      </button>
      {failed && (
        <span role="alert" className="small">
          Chưa lưu được đánh giá.
        </span>
      )}
    </div>
  );
}
