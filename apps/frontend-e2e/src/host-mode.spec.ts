import { expect, test, TEST_HOST_PIN } from './fixtures';

/** Helper: enter PIN digits on the keypad overlay. */
async function enterPin(page: import('@playwright/test').Page, pin: string) {
  for (const digit of pin) {
    const digitButton = page
      .locator('button')
      .filter({ hasText: new RegExp(`^${digit}$`) })
      .first();
    await digitButton.click();
  }
}

/** Helper: activate host mode with the correct PIN. */
async function activateHostMode(page: import('@playwright/test').Page) {
  const lockButton = page.getByRole('button', {
    name: /Activate host mode/i,
  });
  await lockButton.click();

  await enterPin(page, TEST_HOST_PIN);

  // Wait for host mode to activate
  await expect(page.getByText('Host Mode Active')).toBeVisible();
}

/** Helper: request an album from the crate. */
async function requestAlbum(
  page: import('@playwright/test').Page,
  albumName: string,
) {
  await page.goto('/crate');
  await expect(page.getByText(albumName)).toBeVisible();

  const albumCard = page.getByRole('button', {
    name: new RegExp(albumName, 'i'),
  });
  await albumCard.click();

  const dialog = page.getByRole('dialog');
  await expect(dialog).toBeVisible();

  const requestButton = dialog.getByRole('button', { name: /Request/i });
  await requestButton.click();
  await expect(dialog).not.toBeVisible({ timeout: 5000 });
}

test.describe('Host mode flows', () => {
  test('enter wrong PIN — error shown', async ({ page }) => {
    await page.goto('/crate');

    const lockButton = page.getByRole('button', {
      name: /Activate host mode/i,
    });
    await lockButton.click();

    // Enter wrong PIN
    await enterPin(page, '9999');

    // Should show error state (PIN dots turn red / shake animation)
    // The overlay should still be visible (not dismissed)
    // Look for the error state on the dot container
    await expect(page.getByText('Host Access')).toBeVisible();

    // Host mode should NOT be active
    await expect(page.getByText('Host Mode Active')).not.toBeVisible();
  });

  test('enter correct PIN — host mode activates', async ({ page }) => {
    await page.goto('/queue');

    await activateHostMode(page);

    // Host mode indicator should be visible with controls
    await expect(page.getByText('Host Mode Active')).toBeVisible();
    await expect(
      page.getByRole('button', { name: /Clear All/i }),
    ).toBeVisible();
    await expect(page.getByRole('button', { name: /Exit/i })).toBeVisible();
  });

  test('promote queue item to now playing', async ({ page }) => {
    // Request an album first
    await requestAlbum(page, 'Kind of Blue');

    // Navigate to queue and activate host mode
    const queueTab = page.getByRole('tab', { name: /Queue/ });
    await queueTab.click();
    await page.waitForURL('**/queue');

    await activateHostMode(page);

    // Album should be in queue
    await expect(page.getByText('Kind of Blue')).toBeVisible();

    // Click Play button to promote to now playing
    const playButton = page.getByRole('button', { name: /Play/i });
    await playButton.click();

    // Album should now appear in the Now Playing section
    await expect(page.getByText('Now Playing')).toBeVisible();

    // The queue should be empty
    await expect(page.getByText('Queue is empty')).toBeVisible();
  });

  test('remove queue item', async ({ page }) => {
    // Request two albums
    await requestAlbum(page, 'Kind of Blue');
    await requestAlbum(page, 'London Calling');

    // Navigate to queue and activate host mode
    const queueTab = page.getByRole('tab', { name: /Queue/ });
    await queueTab.click();
    await page.waitForURL('**/queue');

    await activateHostMode(page);

    await expect(page.getByText('Kind of Blue')).toBeVisible();
    await expect(page.getByText('London Calling')).toBeVisible();

    // Remove the first item using the host Remove button
    const removeButtons = page.getByRole('button', { name: '✕ Remove' });
    await removeButtons.first().click();

    // One album should be gone
    await expect(page.getByText('1 album in queue')).toBeVisible({ timeout: 5000 });
  });

  test('Clear All button clears queue and now playing', async ({ page }) => {
    // Request an album and promote it
    await requestAlbum(page, 'Kind of Blue');

    const queueTab = page.getByRole('tab', { name: /Queue/ });
    await queueTab.click();
    await page.waitForURL('**/queue');

    await activateHostMode(page);

    // Promote to now playing
    const playButton = page.getByRole('button', { name: /Play/i });
    await playButton.click();
    await expect(page.getByText('Now Playing')).toBeVisible();

    // Request another album so queue is not empty
    const crateTab = page.getByRole('tab', { name: /The Crate/ });
    await crateTab.click();
    await requestAlbum(page, 'Discovery');

    await queueTab.click();
    await page.waitForURL('**/queue');
    await expect(page.getByText('Discovery')).toBeVisible();

    // Click Clear All
    const clearAllButton = page.getByRole('button', { name: /Clear All/i });
    await clearAllButton.click();

    // Both now playing and queue should be cleared
    await expect(page.getByText('Nothing playing yet')).toBeVisible();
    await expect(page.getByText('Queue is empty')).toBeVisible();
  });

  test('deactivate host mode — host controls disappear', async ({ page }) => {
    await page.goto('/queue');

    await activateHostMode(page);
    await expect(page.getByText('Host Mode Active')).toBeVisible();

    // Click Exit to deactivate
    const exitButton = page.getByRole('button', { name: /Exit/i });
    await exitButton.click();

    // Host mode indicator and controls should disappear
    await expect(page.getByText('Host Mode Active')).not.toBeVisible();
    await expect(
      page.getByRole('button', { name: /Clear All/i }),
    ).not.toBeVisible();

    // Lock button should show "Activate host mode" again
    await expect(
      page.getByRole('button', { name: /Activate host mode/i }),
    ).toBeVisible();
  });
});
