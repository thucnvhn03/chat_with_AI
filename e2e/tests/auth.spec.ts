// T1-06 (E2E): đăng nhập đúng, sai, không có quyền, hết phiên; axe trên S-01.
import { expect, test } from '@playwright/test';
import { expectNoSeriousA11yViolations, login } from './helpers';

test('đăng nhập đúng: BD vào màn hình chính', async ({ page }) => {
  await login(page, 'e2e.bd');
  await expect(page.getByRole('heading', { name: 'Tài liệu của tôi' })).toBeVisible();
  await expect(page.getByText(/Nhân sự BD/)).toBeVisible();
});

test('đăng nhập sai: thông báo chung, axe không vi phạm nghiêm trọng', async ({ page }) => {
  await login(page, 'e2e.bd', 'sai-mat-khau');
  await expect(page.getByRole('alert')).toContainText('Tên đăng nhập hoặc mật khẩu chưa đúng.');
  await expectNoSeriousA11yViolations(page);
});

test('không có quyền: tài khoản bị thu hồi nhận trạng thái "không có quyền"', async ({ browser }) => {
  // Quản trị bảo mật thu hồi quyền của e2e.revoke rồi cấp lại ở cuối để chạy lại được
  const admin = await browser.newPage();
  await login(admin, 'e2e.admin');
  const row = admin.getByRole('row').filter({ hasText: 'e2e.revoke' });
  await row.getByRole('button', { name: /Thu hồi quyền/ }).click();
  await admin.getByRole('alert').getByRole('button', { name: 'Thu hồi' }).click();
  await expect(row).toContainText('Đã thu hồi');

  const user = await browser.newPage();
  await login(user, 'e2e.revoke');
  await expect(user.getByRole('alert')).toContainText('chưa được cấp quyền sử dụng ứng dụng');

  await admin.getByLabel('Tên đăng nhập').fill('e2e.revoke');
  await admin.getByLabel('Vai trò').selectOption('bd');
  await admin.getByRole('button', { name: 'Cấp quyền' }).click();
  await expect(row).toContainText('Đang hoạt động');
});

test('hết phiên: yêu cầu kế tiếp đưa về S-01 với thông báo hết phiên, giữ câu hỏi đang soạn', async ({ page, context }) => {
  await login(page, 'e2e.bd');
  await expect(page.getByRole('heading', { name: 'Tài liệu của tôi' })).toBeVisible();
  const input = page.getByLabel('Câu hỏi của bạn');
  // Giả lập phiên hết hạn phía máy chủ: cookie phiên không còn hợp lệ
  const cookies = await context.cookies();
  await context.clearCookies();
  await context.addCookies(cookies.map((c) => (c.name === 'cwd_session' ? { ...c, value: 'phien-het-han' } : c)));
  if (await input.isEnabled()) {
    await input.fill('Câu hỏi đang soạn dở');
    await page.getByRole('button', { name: 'Gửi' }).click();
  } else {
    await page.reload();
  }
  await expect(page.getByRole('heading', { name: 'Đăng nhập' })).toBeVisible();
  await expect(page.getByRole('alert')).toContainText('Phiên làm việc đã hết hạn.');
});
