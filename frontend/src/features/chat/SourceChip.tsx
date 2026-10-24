// C-12 SourceChip: "tên tài liệu, tr.N"; chọn chip mở S-03 đúng trang và phát sự kiện `source_opened`.
import { Link } from 'react-router-dom';
import { api, type CitationOut } from '../../api/client';

interface Props {
  citation: CitationOut;
  /** Toàn bộ nguồn của câu trả lời, để S-03 hiển thị cột nguồn */
  allCitations: CitationOut[];
  current?: boolean;
}

export function sourceHref(citation: CitationOut): string {
  return `/sources/${citation.document_id}?page=${citation.page}`;
}

export function SourceChip({ citation, allCitations, current }: Props) {
  return (
    <Link
      className="chip"
      to={sourceHref(citation)}
      state={{ citations: allCitations, active: citation }}
      aria-current={current ? 'true' : undefined}
      // Tên truy cập bắt đầu bằng đúng chữ hiển thị (WCAG 2.5.3), thêm mô tả hành động
      aria-label={`${citation.document_name}, tr.${citation.page} – mở trang nguồn`}
      onClick={() => {
        // Chỉ gửi id tài liệu và số trang, không gửi nội dung (T2-11)
        api.sourceOpened(citation.document_id, citation.page).catch(() => undefined);
      }}
    >
      <span aria-hidden="true">📄</span> {citation.document_name}, tr.{citation.page}
    </Link>
  );
}
