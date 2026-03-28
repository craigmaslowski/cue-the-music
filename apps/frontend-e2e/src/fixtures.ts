import { test as base, expect } from '@playwright/test';

const API_BASE_URL = 'http://localhost:8000';

/** Extended test fixture that resets the database and browser state before each test. */
export const test = base.extend({
  page: async ({ page }, use) => {
    // Reset database to seed state
    const response = await page.request.post(`${API_BASE_URL}/api/test/reset`);
    expect(response.ok()).toBeTruthy();

    // Clear sessionStorage (host mode state) to prevent leaking between tests
    await page.goto('/crate');
    await page.evaluate(() => sessionStorage.clear());

    await use(page);
  },
});

export { expect } from '@playwright/test';

/** Host PIN used in seed data and test configuration. */
export const TEST_HOST_PIN = '1234';
