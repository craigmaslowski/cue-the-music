import { expect, test } from '@playwright/test';

test.describe('App Shell', () => {
  test('redirects root to /crate', async ({ page }) => {
    await page.goto('/');
    await page.waitForURL('**/crate');
    expect(page.url()).toContain('/crate');
  });

  test('displays the app title', async ({ page }) => {
    await page.goto('/crate');
    const heading = page.locator('h1');
    await expect(heading).toContainText('Cue The Music');
  });

  test('shows host mode lock button', async ({ page }) => {
    await page.goto('/crate');
    const lockButton = page.getByRole('button', {
      name: /activate host mode/i,
    });
    await expect(lockButton).toBeVisible();
  });
});

test.describe('Navigation', () => {
  test('bottom tabs switch between Crate and Queue', async ({ page }) => {
    await page.goto('/crate');

    // Verify the Crate tab is visible
    const crateTab = page.getByRole('tab', { name: 'The Crate' });
    const queueTab = page.getByRole('tab', { name: 'Queue' });
    await expect(crateTab).toBeVisible();
    await expect(queueTab).toBeVisible();

    // Click Queue tab
    await queueTab.click();
    await page.waitForURL('**/queue');
    expect(page.url()).toContain('/queue');

    // Click Crate tab to go back
    await crateTab.click();
    await page.waitForURL('**/crate');
    expect(page.url()).toContain('/crate');
  });
});

test.describe('The Crate (collection browse)', () => {
  test('renders the crate page or error state', async ({ page }) => {
    await page.goto('/crate');

    // The page should either show collection content or the loading/error state.
    // Without a running backend, the error component will display.
    const content = page.locator('body');
    await expect(content).not.toBeEmpty();

    // Verify we're on the crate page (URL is sufficient)
    expect(page.url()).toContain('/crate');
  });
});

test.describe('Queue', () => {
  test('renders the queue page', async ({ page }) => {
    await page.goto('/queue');

    // The page should render (either queue content or error state)
    const content = page.locator('body');
    await expect(content).not.toBeEmpty();

    // Verify we're on the queue page
    expect(page.url()).toContain('/queue');
  });
});
