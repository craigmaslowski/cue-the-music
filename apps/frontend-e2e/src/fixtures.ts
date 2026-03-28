import { test as base, expect } from '@playwright/test';

const API_BASE_URL = 'http://localhost:8000';

/** Extended test fixture that resets the database before each test file. */
export const test = base.extend({
  /** Automatically reset the database before each test. */
  page: async ({ page }, use) => {
    // Reset database to seed state before each test
    const response = await page.request.post(`${API_BASE_URL}/api/test/reset`);
    expect(response.ok()).toBeTruthy();
    await use(page);
  },
});

export { expect } from '@playwright/test';

/** Host PIN used in seed data and test configuration. */
export const TEST_HOST_PIN = '1234';
