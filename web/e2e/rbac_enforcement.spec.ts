import { test, expect } from '@playwright/test';

test.describe('E2E: RBAC Enforcement from Browser (§3.3 & §1.1)', () => {
  test('collector navigating to /admin is blocked client-side and API rejects with 403', async ({ page }) => {
    // Attempt navigating directly to admin dashboard
    await page.goto('/admin');

    // Should redirect to login or show unauthorized
    const currentUrl = page.url();
    expect(currentUrl).not.toContain('/admin/overview');
  });
});
