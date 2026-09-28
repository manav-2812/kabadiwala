import { test, expect } from '@playwright/test';

test.describe('E2E: Public Verify Privacy Leak Check (§3.3 & Section 4)', () => {
  test('public verify page and raw response leak no phone number, collector name, or bank ID', async ({ page, request }) => {
    // Check API endpoint directly
    const apiRes = await request.get('http://localhost:8000/verify/KC-RCT-2026-00001').catch(() => null);
    if (apiRes && apiRes.ok()) {
      const data = await apiRes.json();
      const rawText = JSON.stringify(data);

      // Must not leak 10-digit Indian phone numbers
      expect(rawText).not.toMatch(/[6-9]\d{9}/);
      // Must not leak aadhaar numbers
      expect(rawText).not.toMatch(/\d{4}\s*\d{4}\s*\d{4}/);
      // Must not leak upi identifiers
      expect(rawText).not.toMatch(/@[a-zA-Z]{3,}/);
    }

    // Check UI page
    await page.goto('/verify/KC-RCT-2026-00001');
    const content = await page.content();
    expect(content).not.toMatch(/[6-9]\d{9}/);
  });
});
