// Nhãn cho giá trị chưa được chốt (ví dụ OQ-003), giống `.tbd` của giao diện mẫu.
export function TbdTag({ id }: { id: string }) {
  return (
    <span className="tbd" title="Chưa có quyết định">
      {id}
    </span>
  );
}
