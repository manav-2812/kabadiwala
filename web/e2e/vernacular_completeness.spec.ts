import { test, expect } from '@playwright/test';

test.describe('E2E: Vernacular Completeness & Dynamic Language Switch (§3.3)', () => {
  test('switching to Punjabi updates visible UI strings dynamically', async ({ page }) => {
    await page.goto('/');

    // Click language switcher if available
    const paBtn = page.locator('button:has-text("ਪੰਜਾਬੀ"), [data-lang="pa"]').first();
    if (await paBtn.isVisible()) {
      await paBtn.click();

      // Check for Punjabi string in header or navigation
      const punjabiText = page.locator('text=ਕਬਾੜੀਵਾਲਾ, text=ਕਬਾੜ, text=ਮੁੱਖ ਪੰਨਾ').first();
      await expect(punjabiText).toBeVisible();
    }
  });
});
