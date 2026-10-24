// T3-08 (AC-005, AC-014, AC-023, AC-024): xóa tài liệu có xác nhận → biến khỏi danh sách → hỏi nội dung của
// nó → "không tìm thấy"; quản trị bảo mật cấp/thu hồi quyền và xem bản ghi kiểm toán.
import { expect, test } from '@playwright/test';
import { ask, docItem, login, unique, uploadPdf, waitReady } from './helpers';

test('xóa tài liệu: hộp thoại xác nhận, biến khỏi danh sách, không còn được dùng để trả lời', async ({ page }) => {
  // Từ vựng sinh ngẫu nhiên mỗi lần chạy: câu hỏi chỉ có đáp án trong tài liệu sẽ bị xóa
  const secret = unique('BIMAT').toUpperCase();
  const words = [unique('zq'), unique('vx'), unique('kj')].join(' ');
  const name = `${unique('XoaDi')}.pdf`;
  await login(page, 'e2e.bd');
  await uploadPdf(page, name, [`${words} la ${secret}.`]);
  await waitReady(page, name);
  await ask(page, `${words} la gi?`);
  await expect(page.getByRole('article', { name: 'Câu trả lời' }).last()).toContainText(secret);

  const trigger = docItem(page, name).getByRole('button', { name: `Xóa ${name}` });
  await trigger.click();
  const dialog = page.getByRole('alertdialog');
  await expect(dialog).toContainText(`Xóa tài liệu "${name}"?`);
  await expect(dialog.getByRole('button', { name: 'Hủy' })).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(dialog).toBeHidden();
  await expect(trigger).toBeFocused();

  await trigger.click();
  await page.getByRole('button', { name: 'Xóa vĩnh viễn' }).click();
  await expect(docItem(page, name)).toHaveCount(0);

  await page.getByRole('button', { name: 'Hội thoại mới' }).click();
  await ask(page, `${words} la gi?`);
  await expect(page.getByRole('status').filter({ hasText: 'Không tìm thấy thông tin này' }).last()).toBeVisible();
});

test('quản trị bảo mật: cấp, thu hồi quyền và xem bản ghi kiểm toán', async ({ page, browser }) => {
  // Tạo một câu hỏi để có bản ghi kiểm toán mới
  const bd = await browser.newPage();
  const name = `${unique('KiemToan')}.pdf`;
  await login(bd, 'e2e.bd2');
  await uploadPdf(bd, name, ['Bao cao kiem toan noi bo quy 3.']);
  await waitReady(bd, name);
  await ask(bd, 'Bao cao kiem toan noi bo la cua quy nao?');
  await expect(bd.getByRole('article', { name: 'Câu trả lời' }).last()).toBeVisible();

  await login(page, 'e2e.admin');
  await expect(page.getByRole('heading', { name: 'Quản lý quyền sử dụng' })).toBeVisible();
  const login2 = unique('nguoi.moi');
  await page.getByLabel('Tên đăng nhập').fill(login2);
  await page.getByLabel('Vai trò').selectOption('manager');
  await page.getByRole('button', { name: 'Cấp quyền' }).click();
  const row = page.getByRole('row').filter({ hasText: login2 });
  await expect(row).toContainText('Quản lý');
  await expect(row).toContainText('Đang hoạt động');
  await row.getByRole('button', { name: /Thu hồi quyền/ }).click();
  await page.getByRole('alert').getByRole('button', { name: 'Thu hồi' }).click();
  await expect(row).toContainText('Đã thu hồi');

  await page.getByRole('link', { name: 'Bản ghi kiểm toán' }).click();
  await page.getByLabel('Người dùng').fill('e2e.bd2');
  await page.getByRole('button', { name: 'Lọc' }).click();
  const first = page.getByRole('table').getByRole('row').nth(1);
  await expect(first).toContainText('e2e.bd2');
  await expect(first).toContainText(name);
  // Không hiển thị nội dung câu hỏi
  await expect(page.getByText('Bao cao kiem toan noi bo la cua quy nao?')).toHaveCount(0);
});
