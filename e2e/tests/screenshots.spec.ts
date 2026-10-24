// T4-06: chụp màn hình giao diện thật để đối chiếu với docs/design/html_design/screenshots/.
// Ảnh ghi vào docs/implement/evidence/screenshots/ (bằng chứng cổng launch).
import { expect, test } from '@playwright/test';
import path from 'node:path';
import { login } from './helpers';

const OUT = path.resolve(process.cwd(), '../docs/implement/evidence/screenshots');
const shot = (name: string) => ({ path: path.join(OUT, `${name}.png`), fullPage: false });

test('ảnh màn hình S-01..S-07', async ({ page }) => {
  await page.goto('/login');
  await page.screenshot(shot('s01-default'));
  await login(page, 'e2e.bd', 'sai');
  await expect(page.getByRole('alert')).toBeVisible();
  await page.screenshot(shot('s01-wrong'));

  await login(page, 'e2e.empty');
  await expect(page.getByRole('heading', { name: 'Chưa có tài liệu nào' })).toBeVisible();
  await page.screenshot(shot('s02-empty'));

  await login(page, 'e2e.bd');
  await expect(page.getByRole('list', { name: 'Danh sách tài liệu' })).toBeVisible();
  await page.screenshot(shot('s02-default'));
  const chip = page.getByRole('link', { name: /mở trang nguồn/ }).first();
  if (await chip.count()) {
    await chip.click();
    await expect(page.getByText(/Trang \d+ \//)).toBeVisible();
    await page.screenshot(shot('s03-default'));
    await page.getByRole('button', { name: '← Quay lại hội thoại' }).click();
  }
  await page.getByRole('button', { name: /^Xóa / }).first().click();
  await page.screenshot(shot('s04-default'));
  await page.keyboard.press('Escape');

  await login(page, 'e2e.admin');
  await expect(page.getByRole('table')).toBeVisible();
  await page.screenshot(shot('s05-default'));
  await page.getByRole('link', { name: 'Bản ghi kiểm toán' }).click();
  await expect(page.getByRole('table')).toBeVisible();
  await page.screenshot(shot('s06-default'));

  await login(page, 'e2e.manager');
  await expect(page.getByRole('heading', { name: 'Báo cáo mức sử dụng' })).toBeVisible();
  await page.waitForTimeout(500);
  await page.screenshot(shot('s07-default'));
});
