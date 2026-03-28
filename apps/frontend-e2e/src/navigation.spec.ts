import { expect, test } from './fixtures';

test.describe('Tab switching and state persistence', () => {
  test('tab switch from Crate to Queue and back', async ({ page }) => {
    await page.goto('/crate');
    await expect(page.getByText('Kind of Blue')).toBeVisible();

    // Switch to Queue
    const queueTab = page.getByRole('tab', { name: 'Queue' });
    await queueTab.click();
    await page.waitForURL('**/queue');
    expect(page.url()).toContain('/queue');

    // Switch back to Crate
    const crateTab = page.getByRole('tab', { name: 'The Crate' });
    await crateTab.click();
    await page.waitForURL('**/crate');
    expect(page.url()).toContain('/crate');

    // Albums should still be visible
    await expect(page.getByText('Kind of Blue')).toBeVisible();
  });

  test('search text persists across tab switches', async ({ page }) => {
    await page.goto('/crate');
    await expect(page.getByText('Kind of Blue')).toBeVisible();

    // Type a search term
    const searchInput = page.getByPlaceholder('Search artists and albums...');
    await searchInput.fill('Miles');

    // Verify filter is applied
    await expect(page.getByText('1 of 6 albums')).toBeVisible();

    // Switch to Queue
    const queueTab = page.getByRole('tab', { name: 'Queue' });
    await queueTab.click();
    await page.waitForURL('**/queue');

    // Switch back to Crate
    const crateTab = page.getByRole('tab', { name: 'The Crate' });
    await crateTab.click();
    await page.waitForURL('**/crate');

    // Search text should be persisted
    const searchInputAfter = page.getByPlaceholder(
      'Search artists and albums...',
    );
    await expect(searchInputAfter).toHaveValue('Miles');

    // Filter should still be applied
    await expect(page.getByText('1 of 6 albums')).toBeVisible();
  });

  test('genre filter persists across tab switches', async ({ page }) => {
    await page.goto('/crate');
    await expect(page.getByText('Kind of Blue')).toBeVisible();

    // Open filters and select a genre
    const showFiltersButton = page.getByRole('button', {
      name: /Show Filters/,
    });
    await showFiltersButton.click();

    // Click "+ More" to open genre modal and select Jazz
    const moreButton = page.getByRole('button', {
      name: 'Browse all genres',
    });
    await moreButton.click();

    const jazzButton = page.getByRole('button', { name: /^Jazz\b/ });
    await jazzButton.click();

    // Close genre modal
    const closeModalButton = page.getByRole('dialog').getByText('✕');
    await closeModalButton.click();

    // Verify filter is active
    await expect(page.getByText('Kind of Blue')).toBeVisible();
    await expect(page.getByText('London Calling')).not.toBeVisible();

    // Switch to Queue
    const queueTab = page.getByRole('tab', { name: 'Queue' });
    await queueTab.click();
    await page.waitForURL('**/queue');

    // Switch back to Crate
    const crateTab = page.getByRole('tab', { name: 'The Crate' });
    await crateTab.click();
    await page.waitForURL('**/crate');

    // Genre filter should still be applied
    await expect(page.getByText('Kind of Blue')).toBeVisible();
    await expect(page.getByText('London Calling')).not.toBeVisible();
  });

  test('album overlay closed on tab switch', async ({ page }) => {
    await page.goto('/crate');
    await expect(page.getByText('Kind of Blue')).toBeVisible();

    // Open album detail overlay
    const albumCard = page.getByRole('button', { name: /Kind of Blue/i });
    await albumCard.click();

    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible();

    // Switch to Queue tab
    const queueTab = page.getByRole('tab', { name: 'Queue' });
    await queueTab.click();
    await page.waitForURL('**/queue');

    // Switch back to Crate
    const crateTab = page.getByRole('tab', { name: 'The Crate' });
    await crateTab.click();
    await page.waitForURL('**/crate');

    // Overlay should not be visible
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });
});
