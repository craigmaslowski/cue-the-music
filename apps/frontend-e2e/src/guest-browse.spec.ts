import { expect, test } from './fixtures';

test.describe('Guest collection browsing', () => {
  test('crate page shows album grid with seeded albums', async ({ page }) => {
    await page.goto('/crate');

    // Wait for albums to load
    await expect(page.getByText('Kind of Blue')).toBeVisible();
    await expect(page.getByText('London Calling')).toBeVisible();
  });

  test('search by artist "Miles" — only Miles Davis album shown', async ({
    page,
  }) => {
    await page.goto('/crate');
    await expect(page.getByText('Kind of Blue')).toBeVisible();

    const searchInput = page.getByPlaceholder('Search artists and albums...');
    await searchInput.fill('Miles');

    // Only Miles Davis album should appear
    await expect(page.getByText('Kind of Blue')).toBeVisible();
    await expect(page.getByText('London Calling')).not.toBeVisible();
    await expect(page.getByText('Trans-Europe Express')).not.toBeVisible();
  });

  test('search by title "Paranoid" — only Black Sabbath shown', async ({
    page,
  }) => {
    await page.goto('/crate');
    await expect(page.getByText('Paranoid')).toBeVisible();

    const searchInput = page.getByPlaceholder('Search artists and albums...');
    await searchInput.fill('Paranoid');

    await expect(page.getByText('Paranoid')).toBeVisible();
    await expect(page.getByText('Kind of Blue')).not.toBeVisible();
    await expect(page.getByText('Discovery')).not.toBeVisible();
  });

  test('clear search with X button — all albums return', async ({ page }) => {
    await page.goto('/crate');
    await expect(page.getByText('Kind of Blue')).toBeVisible();

    const searchInput = page.getByPlaceholder('Search artists and albums...');
    await searchInput.fill('Miles');

    // Only Miles Davis visible
    await expect(page.getByText('London Calling')).not.toBeVisible();

    // Click the clear search button
    const clearButton = page.getByRole('button', { name: 'Clear search' });
    await clearButton.click();

    // All albums should return
    await expect(page.getByText('Kind of Blue')).toBeVisible();
    await expect(page.getByText('London Calling')).toBeVisible();
    await expect(page.getByText('Discovery')).toBeVisible();
  });

  test('filter by genre "Jazz" using genre filter modal', async ({ page }) => {
    await page.goto('/crate');
    await expect(page.getByText('Kind of Blue')).toBeVisible();

    // Open filters first
    const showFiltersButton = page.getByRole('button', {
      name: /Show Filters/,
    });
    await showFiltersButton.click();

    // Click "+ More" to open genre modal
    const moreButton = page.getByRole('button', {
      name: 'Browse all genres',
    });
    await moreButton.click();

    // In the modal, click "Jazz"
    const jazzButton = page.getByRole('button', { name: /^Jazz\b/ });
    await jazzButton.click();

    // Close the modal
    const closeModalButton = page
      .getByRole('dialog')
      .getByText('✕');
    await closeModalButton.click();

    // Only Jazz album(s) should be shown
    await expect(page.getByText('Kind of Blue')).toBeVisible();
    await expect(page.getByText('London Calling')).not.toBeVisible();
    await expect(page.getByText('Discovery')).not.toBeVisible();
  });

  test('filter by decade "1970" using decade chip filter', async ({ page }) => {
    await page.goto('/crate');
    await expect(page.getByText('Kind of Blue')).toBeVisible();

    // Open filters
    const showFiltersButton = page.getByRole('button', {
      name: /Show Filters/,
    });
    await showFiltersButton.click();

    // Click the 1970 decade chip (exact match to avoid album card "Paranoid Black Sabbath 1970")
    const decadeChip = page.getByRole('button', { name: '1970', exact: true });
    await decadeChip.click();

    // Albums from the 1970s: London Calling (1979), Trans-Europe Express (1977), Paranoid (1970)
    await expect(page.getByText('London Calling')).toBeVisible();
    await expect(page.getByText('Trans-Europe Express')).toBeVisible();
    await expect(page.getByText('Paranoid')).toBeVisible();

    // Albums NOT from the 1970s should be hidden
    await expect(page.getByText('Kind of Blue')).not.toBeVisible();
    await expect(page.getByText('Discovery')).not.toBeVisible();
  });

  test('album count text updates when filtered', async ({ page }) => {
    await page.goto('/crate');
    await expect(page.getByText('6 albums')).toBeVisible();

    const searchInput = page.getByPlaceholder('Search artists and albums...');
    await searchInput.fill('Miles');

    await expect(page.getByText('1 of 6 albums')).toBeVisible();
  });

  test('toggle show/hide filters button works', async ({ page }) => {
    await page.goto('/crate');
    await expect(page.getByText('Kind of Blue')).toBeVisible();

    // Initially filters are hidden, "Show Filters" button should be present
    const showFiltersButton = page.getByRole('button', {
      name: /Show Filters/,
    });
    await expect(showFiltersButton).toBeVisible();

    // Click to show filters
    await showFiltersButton.click();

    // Now "Hide Filters" button should appear
    const hideFiltersButton = page.getByRole('button', {
      name: /Hide Filters/,
    });
    await expect(hideFiltersButton).toBeVisible();

    // Genre and Decade labels should be visible
    await expect(page.getByText('Genre', { exact: true })).toBeVisible();
    await expect(page.getByText('Decade', { exact: true })).toBeVisible();

    // Click to hide filters again
    await hideFiltersButton.click();

    // "Show Filters" should reappear
    await expect(
      page.getByRole('button', { name: /Show Filters/ }),
    ).toBeVisible();
  });
});
