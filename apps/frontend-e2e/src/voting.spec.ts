import { expect, test } from './fixtures';

/** Helper: request an album from the crate and navigate to the queue. */
async function requestAlbumAndGoToQueue(
  page: import('@playwright/test').Page,
  albumName: string,
) {
  await page.goto('/crate');
  await expect(page.getByText(albumName)).toBeVisible();

  const albumCard = page.getByRole('button', { name: new RegExp(albumName, 'i') });
  await albumCard.click();

  const dialog = page.getByRole('dialog');
  await expect(dialog).toBeVisible();

  const requestButton = dialog.getByRole('button', { name: /Request/i });
  await requestButton.click();

  // Overlay auto-closes and navigates to queue after "Requested" feedback
  await page.waitForURL('**/queue', { timeout: 5000 });
  await expect(page.getByText(albumName)).toBeVisible();
}

test.describe('Voting on queue items', () => {
  test('album in queue shows with 1 upvote from requester', async ({
    page,
  }) => {
    await requestAlbumAndGoToQueue(page, 'Kind of Blue');

    // The requester auto-upvotes, so up count should show 1
    const upVoteButton = page.getByRole('button', { name: 'Remove up vote' });
    await expect(upVoteButton).toBeVisible();
    await expect(upVoteButton).toContainText('1');
  });

  test('downvote the album — down count shows 1', async ({ page }) => {
    await requestAlbumAndGoToQueue(page, 'Kind of Blue');

    // Downvote
    const downVoteButton = page.getByRole('button', { name: 'Vote down' });
    await downVoteButton.click();

    // Down count should show 1
    const activeDownVote = page.getByRole('button', {
      name: 'Remove down vote',
    });
    await expect(activeDownVote).toBeVisible();
    await expect(activeDownVote).toContainText('1');
  });

  test('toggle downvote off — down count back to 0', async ({ page }) => {
    await requestAlbumAndGoToQueue(page, 'Kind of Blue');

    // Downvote
    const downVoteButton = page.getByRole('button', { name: 'Vote down' });
    await downVoteButton.click();

    // Remove downvote
    const activeDownVote = page.getByRole('button', {
      name: 'Remove down vote',
    });
    await activeDownVote.click();

    // Down count should be back to 0
    const resetDownVote = page.getByRole('button', { name: 'Vote down' });
    await expect(resetDownVote).toBeVisible();
    await expect(resetDownVote).toContainText('0');
  });

  test('can toggle upvote off and back on', async ({ page }) => {
    await requestAlbumAndGoToQueue(page, 'Kind of Blue');

    // Auto-upvoted — remove upvote
    const upVoteButton = page.getByRole('button', { name: 'Remove up vote' });
    await upVoteButton.click();

    // Up count should be 0
    const noUpVote = page.getByRole('button', { name: 'Vote up' });
    await expect(noUpVote).toBeVisible();
    await expect(noUpVote).toContainText('0');

    // Upvote again
    await noUpVote.click();

    // Should be back to 1
    const reUpVote = page.getByRole('button', { name: 'Remove up vote' });
    await expect(reUpVote).toBeVisible();
    await expect(reUpVote).toContainText('1');
  });
});
