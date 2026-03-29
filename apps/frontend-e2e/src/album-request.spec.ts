import { expect, test } from './fixtures';

test.describe('Album detail and request flow', () => {
  test('click album opens detail overlay with title and artist', async ({
    page,
  }) => {
    await page.goto('/crate');
    await expect(page.getByText('Kind of Blue')).toBeVisible();

    // Click the album card for Kind of Blue
    const albumCard = page.getByRole('button', { name: /Kind of Blue/i });
    await albumCard.click();

    // Overlay should show album details
    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible();
    await expect(dialog.getByText('Kind of Blue')).toBeVisible();
    await expect(dialog.getByText('Miles Davis')).toBeVisible();
  });

  test('album with tracklist shows track entries', async ({ page }) => {
    await page.goto('/crate');
    await expect(page.getByText('Kind of Blue')).toBeVisible();

    const albumCard = page.getByRole('button', { name: /Kind of Blue/i });
    await albumCard.click();

    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible();

    // Should show Tracklist heading
    await expect(dialog.getByText('Tracklist')).toBeVisible();

    // Wait for tracks to load — "So What" is the first track on Kind of Blue
    await expect(dialog.getByText('So What')).toBeVisible();
  });

  test('close overlay with close button', async ({ page }) => {
    await page.goto('/crate');
    await expect(page.getByText('Kind of Blue')).toBeVisible();

    const albumCard = page.getByRole('button', { name: /Kind of Blue/i });
    await albumCard.click();

    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible();

    // Close via the close trigger (the X button in the Dialog)
    const closeButton = dialog.getByText('✕');
    await closeButton.click();

    await expect(dialog).not.toBeVisible();
  });

  test('request album — button shows "Requested" then overlay closes', async ({
    page,
  }) => {
    await page.goto('/crate');
    await expect(page.getByText('Kind of Blue')).toBeVisible();

    const albumCard = page.getByRole('button', { name: /Kind of Blue/i });
    await albumCard.click();

    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible();

    // Click the request button (initially says "Request")
    const requestButton = dialog.getByRole('button', { name: /Request/i });
    await requestButton.click();

    // Should briefly show "Requested" text
    await expect(dialog.getByText('Requested')).toBeVisible();

    // Overlay should close automatically
    await expect(dialog).not.toBeVisible({ timeout: 5000 });
  });

  test('after requesting, album appears in queue', async ({ page }) => {
    await page.goto('/crate');
    await expect(page.getByText('Kind of Blue')).toBeVisible();

    // Request the album
    const albumCard = page.getByRole('button', { name: /Kind of Blue/i });
    await albumCard.click();

    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible();

    const requestButton = dialog.getByRole('button', { name: /Request/i });
    await requestButton.click();

    // Overlay auto-closes and navigates to queue
    await page.waitForURL('**/queue', { timeout: 5000 });

    // Album should appear in the queue
    await expect(page.getByText('Kind of Blue')).toBeVisible();
    await expect(page.getByText('Miles Davis')).toBeVisible();
  });

  test('return to crate — album detail shows "In Queue" button (disabled)', async ({
    page,
  }) => {
    await page.goto('/crate');
    await expect(page.getByText('Kind of Blue')).toBeVisible();

    // Request the album first
    const albumCard = page.getByRole('button', { name: /Kind of Blue/i });
    await albumCard.click();

    const dialog = page.getByRole('dialog');
    const requestButton = dialog.getByRole('button', { name: /Request/i });
    await requestButton.click();

    // Overlay auto-closes to queue
    await page.waitForURL('**/queue', { timeout: 5000 });

    // Navigate back to crate
    await page.getByRole('tab', { name: /The Crate/ }).click();
    await page.waitForURL('**/crate');

    // Re-open album detail
    await page.getByRole('button', { name: /Kind of Blue/i }).click();
    await expect(dialog).toBeVisible();

    // Button should now show "In Queue" and be disabled
    const inQueueButton = dialog.getByRole('button', { name: /In Queue/i });
    await expect(inQueueButton).toBeVisible();
    await expect(inQueueButton).toBeDisabled();
  });

  test('go to queue and cancel own request', async ({ page }) => {
    await page.goto('/crate');
    await expect(page.getByText('Kind of Blue')).toBeVisible();

    // Request the album
    const albumCard = page.getByRole('button', { name: /Kind of Blue/i });
    await albumCard.click();

    const dialog = page.getByRole('dialog');
    const requestButton = dialog.getByRole('button', { name: /Request/i });
    await requestButton.click();

    // Overlay auto-closes to queue
    await page.waitForURL('**/queue', { timeout: 5000 });
    await expect(page.getByText('Kind of Blue')).toBeVisible();

    // Cancel the request
    const cancelButton = page.getByRole('button', { name: 'Cancel request' });
    await cancelButton.click();

    // Album should disappear from queue
    await expect(page.getByText('Kind of Blue')).not.toBeVisible();
    await expect(page.getByText('Queue is empty')).toBeVisible();
  });
});
