import { test, expect } from '@playwright/test';

test.describe('E2E: Expired License Recycler Exclusion (§3.3 & §2.4)', () => {
  test('Malwa Materials Recovery (expired license) is never shown in FindBuyers', async ({ page }) => {
    await page.goto('/');

    // Ensure Malwa Materials Recovery does not appear on buyer lists
    const malwa = page.locator('text=Malwa Materials Recovery');
    await expect(malwa).toHaveCount(0);
  });
});
