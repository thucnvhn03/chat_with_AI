// Danh sách tài liệu (GET /documents), hỏi định kỳ mỗi POLL_INTERVAL_S khi còn tài liệu đang xử lý,
// dừng khi không còn (US-001, T1-18).
import { useQuery } from '@tanstack/react-query';
import { api, type DocumentOut } from '../../api/client';

export const DOCUMENTS_KEY = ['documents'] as const;

export function hasProcessing(documents: DocumentOut[] | undefined): boolean {
  return !!documents?.some((d) => d.status === 'processing' || d.status === 'uploading');
}

export function useDocuments(pollIntervalS: number) {
  return useQuery({
    queryKey: DOCUMENTS_KEY,
    queryFn: api.listDocuments,
    refetchInterval: (query) => (hasProcessing(query.state.data) ? pollIntervalS * 1000 : false),
  });
}
