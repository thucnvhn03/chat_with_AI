// T4-08: axe tự động trên S-01..S-07 và các trạng thái chính; kiểm tra dùng được chỉ bằng bàn phím.
import { expect, test } from '@playwright/test';
import { expectNoSeriousA11yViolations, login } from './helpers';

test('S-01 Đăng nhập', async ({ page }) => {
  await page.goto('/login');
  await expectNoSeriousA11yViolations(page);
});

test('S-05 và S-06 (quản trị bảo mật)', async ({ page }) => {
  await login(page, 'e2e.admin');
  await expect(page.getByRole('heading', { name: 'Quản lý quyền sử dụng' })).toBeVisible();
  await expectNoSeriousA11yViolations(page);
  await page.getByRole('link', { name: 'Bản ghi kiểm toán' }).click();
  await expect(page.getByRole('heading', { name: 'Bản ghi kiểm toán truy vấn' })).toBeVisible();
  await expectNoSeriousA11yViolations(page);
});

test('S-07 Báo cáo mức sử dụng', async ({ page }) => {
  await login(page, 'e2e.manager');
  await expect(page.getByRole('heading', { name: 'Báo cáo mức sử dụng' })).toBeVisible();
  await expect(page.getByRole('status')).toHaveCount(0);
  await expectNoSeriousA11yViolations(page);
});

test('S-04 hộp thoại xóa', async ({ page }) => {
  await login(page, 'e2e.bd');
  await page.getByRole('list', { name: 'Danh sách tài liệu' }).waitFor({ timeout: 10_000 }).catch(() => undefined);
  const deleteButton = page.getByRole('button', { name: /^Xóa / }).first();
  test.skip((await deleteButton.count()) === 0, 'cần ít nhất một tài liệu (chạy documents.spec trước)');
  await deleteButton.click();
  await expect(page.getByRole('alertdialog')).toBeVisible();
  await expectNoSeriousA11yViolations(page);
  await page.keyboard.press('Escape');
});

test('chỉ dùng bàn phím: liên kết bỏ qua và đăng nhập', async ({ page }) => {
  await page.goto('/login');
  await page.keyboard.press('Tab');
  await expect(page.getByText('Bỏ qua tới nội dung chính')).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(page.getByLabel('Tên đăng nhập')).toBeFocused();
  await page.keyboard.type('e2e.bd');
  await page.keyboard.press('Tab');
  await page.keyboard.type('e2e-mat-khau-123');
  await page.keyboard.press('Enter');
  await expect(page.getByRole('heading', { name: 'Tài liệu của tôi' })).toBeVisible();
});

test('thu phóng 200%: màn hình chính không mất chức năng', async ({ page }) => {
  await page.setViewportSize({ width: 720, height: 450 });
  await login(page, 'e2e.bd');
  await page.evaluate(() => {
    document.body.style.zoom = '2';
  });
  await expect(page.getByRole('button', { name: '＋ Tải PDF lên' })).toBeVisible();
  await expect(page.getByLabel('Câu hỏi của bạn')).toBeVisible();
});
