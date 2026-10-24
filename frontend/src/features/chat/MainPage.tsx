// S-02 Màn hình chính (vai trò BD): vùng tài liệu và vùng hội thoại cạnh nhau.
import { useAuth } from '../../app/auth';
import { AppShell } from '../../app/AppShell';
import { ErrorBanner } from '../../components/ErrorBanner';
import { DocumentPanel } from '../documents/DocumentPanel';
import { useDocuments } from '../documents/useDocuments';
import { useUploads } from '../documents/useUploads';
import { ChatPanel } from './ChatPanel';
import { useChat } from './useChat';

export function MainPage() {
  const { me } = useAuth();
  const config = me?.config;
  const documents = useDocuments(config?.poll_interval_s ?? 3);
  const uploads = useUploads(config?.max_file_bytes);
  const chat = useChat();

  const list = documents.data;
  const hasDocuments = (list?.length ?? 0) > 0;
  const hasReady = !!list?.some((d) => d.status === 'ready');
  const incomplete = uploads.items.filter((i) => i.status === 'incomplete');

  return (
    <AppShell mainId="chat" skipLabel="Bỏ qua tới hội thoại">
      {(chat.error?.kind === 'network' || incomplete.length > 0) && (
        <div style={{ padding: '12px 24px 0', display: 'grid', gap: 8 }}>
          {chat.error?.kind === 'network' && (
            <ErrorBanner icon="📡" title="Mất kết nối, chưa nhận được câu trả lời." style={{ margin: 0 }}>
              Câu hỏi của bạn vẫn được giữ lại bên dưới. Hãy kiểm tra mạng rồi gửi lại.
            </ErrorBanner>
          )}
          {incomplete.length > 0 && (
            <ErrorBanner icon="📡" title="Mất kết nối khi tải lên." style={{ margin: 0 }}>
              {incomplete.length === 1
                ? `Tệp "${incomplete[0].file.name}" chưa tải xong và chưa được đưa vào tập tài liệu.`
                : `${incomplete.length} tệp chưa tải xong và chưa được đưa vào tập tài liệu.`}{' '}
              Hãy tải lại khi có mạng.
            </ErrorBanner>
          )}
        </div>
      )}
      <main className="workspace">
        <DocumentPanel
          documents={list}
          loading={documents.isPending}
          loadError={documents.isError}
          onReload={() => void documents.refetch()}
          uploads={uploads}
          maxFileBytes={config?.max_file_bytes}
          maxDocs={config?.max_docs_per_user}
          purgeSlaHours={config?.purge_sla_hours}
        />
        <ChatPanel
          chat={chat}
          hasDocuments={hasDocuments}
          hasReady={hasReady}
          maxQuestionChars={config?.max_question_chars}
        />
      </main>
    </AppShell>
  );
}
