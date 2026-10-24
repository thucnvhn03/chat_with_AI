// T2-14 (AC-006, AC-009, AC-012, AC-019), T2-10: tải PDF → hỏi → câu trả lời kèm nguồn → mở S-03 đúng trang
// → câu hỏi ngoài phạm vi "không tìm thấy" → mất mạng khi hỏi. axe trên S-02 và S-03.
import { expect, test } from '@playwright/test';
import { ask, expectNoSeriousA11yViolations, login, unique, uploadPdf, waitReady } from './helpers';

test('hỏi đáp có nguồn và trình xem nguồn', async ({ page }) => {
  const code = unique('MA').toUpperCase();
  const name = `${unique('HopDong')}.pdf`;
  await login(page, 'e2e.bd');
  await page.getByRole('button', { name: 'Hội thoại mới' }).click({ timeout: 2000 }).catch(() => undefined);
  await uploadPdf(page, name, [
    'Hop dong phan phoi giua Cong ty Gamma va Cong ty Delta nam 2026.',
    `Dieu 9. Ma du an cua hop dong la ${code} va duoc bao mat.`,
    'Dieu 10. Cac ben giai quyet tranh chap bang thuong luong.',
  ]);
  await waitReady(page, name);

  await ask(page, `Ma du an ${code} cua hop dong la gi?`);
  const answer = page.getByRole('article', { name: 'Câu trả lời' }).last();
  await expect(answer).toContainText(code);
  const chip = answer.getByRole('link', { name: `${name}, tr.2 – mở trang nguồn` });
  await expect(chip).toBeVisible();
  await expect(page.getByLabel('Câu hỏi của bạn')).toBeFocused();
  await expectNoSeriousA11yViolations(page);

  await chip.click();
  await expect(page.getByText('Trang 2 / 3')).toBeVisible();
  await expect(page.locator('mark.hit')).toContainText(code);
  await expectNoSeriousA11yViolations(page);
  await page.getByRole('button', { name: 'Trang sau' }).click();
  await expect(page.getByText('Trang 3 / 3')).toBeVisible();

  await page.getByRole('button', { name: '← Quay lại hội thoại' }).click();
  await expect(page.getByRole('article', { name: 'Câu trả lời' }).last()).toContainText(code);

  // AC-009: câu hỏi ngoài phạm vi trong hội thoại mới (trong cùng hội thoại, truy vấn được ghép với câu trước)
  await page.getByRole('button', { name: 'Hội thoại mới' }).click();
  // Không có từ nào trùng với dữ liệu kiểm thử (embedding giả lập so khớp theo từ)
  await ask(page, 'Capital city of Australia?');
  await expect(page.getByRole('status').filter({ hasText: 'Không tìm thấy thông tin này' }).last()).toBeVisible();
});

test('mất mạng khi hỏi: giữ câu hỏi, "Gửi lại" được sau khi có mạng', async ({ page }) => {
  const name = `${unique('TaiLieu')}.pdf`;
  await login(page, 'e2e.bd2');
  await uploadPdf(page, name, ['Chinh sach doi tra: khach hang duoc doi tra trong 14 ngay.']);
  await waitReady(page, name);

  await page.route('**/api/v1/conversations/*/messages', (route) => route.abort('internetdisconnected'));
  await ask(page, 'Khach hang duoc doi tra trong bao nhieu ngay?');
  await expect(page.getByText('Mất kết nối, chưa nhận được câu trả lời.')).toBeVisible();
  await expect(page.getByLabel('Câu hỏi của bạn')).toHaveValue('Khach hang duoc doi tra trong bao nhieu ngay?');
  await expect(page.getByRole('article', { name: 'Câu trả lời' })).toHaveCount(0);

  await page.unroute('**/api/v1/conversations/*/messages');
  await page.getByRole('button', { name: 'Gửi lại' }).click();
  await expect(page.getByRole('article', { name: 'Câu trả lời' }).last()).toContainText('14 ngay');
});
