// C-10 EmptyState: trạng thái trống có biểu tượng, tiêu đề và hướng dẫn bước tiếp theo.
import type { ReactNode } from 'react';

interface Props {
  icon: string;
  title: string;
  children?: ReactNode;
  headingLevel?: 2 | 3;
}

export function EmptyState({ icon, title, children, headingLevel = 3 }: Props) {
  const Heading = headingLevel === 2 ? 'h2' : 'h3';
  return (
    <div className="empty">
      <div className="empty-icon" aria-hidden="true">
        {icon}
      </div>
      <Heading>{title}</Heading>
      {children}
    </div>
  );
}
