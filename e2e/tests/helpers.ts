// Tiện ích dùng chung cho kịch bản E2E: đăng nhập, tạo PDF, tải lên, hỏi, kiểm tra axe.
import AxeBuilder from '@axe-core/playwright';
import { expect, type Page } from '@playwright/test';
import { makePdf } from './pdf';

export const PASSWORD = 'e2e-mat-khau-123';

export async function login(page: Page, user: string, password = PASSWORD): Promise<void> {
  await page.goto('/login');
  await page.getByLabel('Tên đăng nhập').fill(user);
  await page.getByLabel('Mật khẩu').fill(password);
  await page.getByRole('button', { name: 'Đăng nhập' }).click();
}

export function unique(prefix: string): string {
  return `${prefix}_${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`;
}

export async function uploadPdf(page: Page, fileName: string, pages: string[]): Promise<void> {
  await page.getByTestId('file-input').setInputFiles({
    name: fileName,
    mimeType: 'application/pdf',
    buffer: makePdf(pages),
  });
}

export function docItem(page: Page, fileName: string) {
  return page.getByRole('list', { name: 'Danh sách tài liệu' }).getByRole('listitem').filter({ hasText: fileName });
}

export async function waitReady(page: Page, fileName: string): Promise<void> {
  await expect(docItem(page, fileName)).toContainText('Sẵn sàng', { timeout: 30_000 });
}

export async function ask(page: Page, question: string): Promise<void> {
  const input = page.getByLabel('Câu hỏi của bạn');
  await expect(input).toBeEnabled();
  await input.fill(question);
  await page.getByRole('button', { name: 'Gửi' }).click();
}

/** Không có vi phạm WCAG 2.1 AA mức nghiêm trọng hoặc cao. */
export async function expectNoSeriousA11yViolations(page: Page): Promise<void> {
  const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze();
  const serious = results.violations
    .filter((v) => v.impact === 'serious' || v.impact === 'critical')
    .map((v) => `${v.id}: ${v.help} (${v.nodes.length})`);
  expect(serious).toEqual([]);
}
