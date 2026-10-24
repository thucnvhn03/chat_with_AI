// T1-21 (AC-001, AC-003), T1-17 (mất mạng khi tải lên): tải PDF → Đang xử lý → Sẵn sàng; tệp hỏng → Lỗi
// kèm lý do; trạng thái trống; axe trên màn hình chính.
import { expect, test } from '@playwright/test';
import { docItem, expectNoSeriousA11yViolations, login, unique, uploadPdf, waitReady } from './helpers';
import { makeCorruptedPdf } from './pdf';

test('trạng thái trống khi chưa có tài liệu', async ({ page }) => {
  await login(page, 'e2e.empty');
  await expect(page.getByRole('heading', { name: 'Chưa có tài liệu nào' })).toBeVisible();
  await expect(page.getByLabel('Câu hỏi của bạn')).toBeDisabled();
  await expectNoSeriousA11yViolations(page);
});

test('tải PDF hợp lệ: Đang xử lý rồi Sẵn sàng, hỏi được (AC-001)', async ({ page }) => {
  const name = `${unique('HopDong')}.pdf`;
  await login(page, 'e2e.bd');
  await uploadPdf(page, name, [
    'Hop dong dich vu van chuyen giua Cong ty Alpha va Cong ty Beta.',
    'Dieu 4. Thoi han thanh toan la 21 ngay ke tu ngay nhan hoa don.',
  ]);
  await expect(docItem(page, name)).toBeVisible();
  await waitReady(page, name);
  await expect(docItem(page, name)).toContainText('2 trang');
  await expect(page.getByLabel('Câu hỏi của bạn')).toBeEnabled();
  await expectNoSeriousA11yViolations(page);
});

test('tải tệp hỏng: nhãn Lỗi cùng lý do, có Thử lại và Xóa (AC-003, AC-018)', async ({ page }) => {
  const name = `${unique('Hong')}.pdf`;
  await login(page, 'e2e.bd');
  await page.getByTestId('file-input').setInputFiles({ name, mimeType: 'application/pdf', buffer: makeCorruptedPdf() });
  const item = docItem(page, name);
  await expect(item).toContainText('Lỗi', { timeout: 30_000 });
  await expect(item).toContainText('Tệp bị hỏng hoặc không đọc được');
  await expect(item.getByRole('button', { name: `Thử lại ${name}` })).toBeVisible();
  await expect(item.getByRole('button', { name: `Xóa ${name}` })).toBeVisible();
});

test('tệp không phải PDF bị từ chối ngay với lý do', async ({ page }) => {
  await login(page, 'e2e.bd');
  await page.getByTestId('file-input').setInputFiles({
    name: 'ghi-chu.pdf',
    mimeType: 'application/pdf',
    buffer: Buffer.from('day khong phai PDF'),
  });
  const uploads = page.getByRole('list', { name: 'Tệp đang tải lên' });
  await expect(uploads).toContainText('Tệp không phải PDF');
});

test('mất mạng giữa chừng khi tải lên: "Chưa tải xong", không bao giờ "Sẵn sàng"', async ({ page }) => {
  const name = `${unique('BaoGia')}.pdf`;
  await login(page, 'e2e.bd');
  await page.route('**/api/v1/documents', (route) =>
    route.request().method() === 'POST' ? route.abort('internetdisconnected') : route.continue(),
  );
  await uploadPdf(page, name, ['Bao gia dich vu luu kho nam 2026.']);
  const uploads = page.getByRole('list', { name: 'Tệp đang tải lên' });
  await expect(uploads.getByRole('listitem').filter({ hasText: name })).toContainText('Chưa tải xong');
  await expect(page.getByText(`Tệp "${name}" chưa tải xong`)).toBeVisible();
  await expect(docItem(page, name)).toHaveCount(0);

  await page.unroute('**/api/v1/documents');
  await uploads.getByRole('button', { name: 'Tải lại' }).click();
  await waitReady(page, name);
});
