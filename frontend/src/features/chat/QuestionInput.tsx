// C-09 QuestionInput: gửi bằng nút hoặc Ctrl/Cmd+Enter; vô hiệu kèm giải thích khi chưa có tài liệu sẵn
// sàng; kiểm tra độ dài theo MAX_QUESTION_CHARS [PQ-002]; câu hỏi đang soạn được giữ trong sessionStorage.
import { forwardRef, type FormEvent, type KeyboardEvent } from 'react';

interface Props {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled: boolean;
  placeholder: string;
  submitLabel: string;
  maxChars?: number;
  hint?: string;
}

export const QuestionInput = forwardRef<HTMLTextAreaElement, Props>(function QuestionInput(
  { value, onChange, onSubmit, disabled, placeholder, submitLabel, maxChars, hint },
  ref,
) {
  const length = value.trim().length;
  const tooLong = maxChars !== undefined && length > maxChars;
  const canSend = !disabled && length > 0 && !tooLong;

  function submit(event?: FormEvent) {
    event?.preventDefault();
    if (canSend) onSubmit();
  }

  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      submit();
    }
  }

  return (
    <div className="composer-wrap">
      <form className="composer" onSubmit={submit}>
        <label htmlFor="question" className="sr-only">
          Câu hỏi của bạn
        </label>
        <textarea
          ref={ref}
          id="question"
          rows={1}
          value={value}
          disabled={disabled}
          placeholder={placeholder}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={onKeyDown}
          aria-describedby="question-hint"
          aria-invalid={tooLong || undefined}
        />
        <button className="btn btn-primary" type="submit" disabled={!canSend}>
          {submitLabel}
        </button>
      </form>
      <p className="field-hint" id="question-hint">
        {hint ?? 'Gửi bằng nút "Gửi" hoặc Ctrl+Enter.'}
        {maxChars !== undefined && (
          <>
            {' '}
            <span className={`char-count${tooLong ? ' over' : ''}`} aria-live="polite">
              {tooLong
                ? `Câu hỏi dài ${length}/${maxChars} ký tự — hãy rút gọn.`
                : `${length}/${maxChars} ký tự`}
            </span>
          </>
        )}
      </p>
    </div>
  );
});
