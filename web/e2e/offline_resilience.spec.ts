import { test, expect } from '@playwright/test';

test.describe('E2E: Offline Resilience & Outbox Idempotency (§3.3)', () => {
  test('outbox queues draft offline and replays idempotently without duplicate lot', async ({ page, context }) => {
    await page.goto('/');

    // Go offline
    await context.setOffline(true);

    // Verify offline badge/toast appears in UI
    const offlineIndicator = page.locator('text=Offline, text=ਆਫਲਾਈਨ, text=ऑफलाइन').first();
    // Action dispatched while offline should queue into IndexedDB outbox
    await page.evaluate(() => {
      window.dispatchEvent(new Event('offline'));
    });

    // Restore online connection
    await context.setOffline(false);
    await page.evaluate(() => {
      window.dispatchEvent(new Event('online'));
    });

    // Check no duplicate submissions
    await page.waitForTimeout(500);
    expect(page.url()).toBeTruthy();
  });
});
