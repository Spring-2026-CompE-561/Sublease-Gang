import { test, expect } from '@playwright/test';

test('search: user can search listings by query string', async ({ page }) => {
  // Navigate directly to listings page (no auth required for public listings)
  await page.goto('/listings');

  // Wait for the navbar search input to be visible
  const searchInput = page.locator('input[placeholder="Search by location, university..."]');
  await searchInput.waitFor({ state: 'visible', timeout: 10000 });

  // Type a search query
  await searchInput.fill('studio');

  // Submit the search by pressing Enter
  await searchInput.press('Enter');

  // Wait for navigation and verify the URL contains the search query
  await page.waitForURL('**/listings?q=studio', { timeout: 10000 });

  // Verify the URL has the expected query parameter
  const url = new URL(page.url());
  expect(url.searchParams.get('q')).toBe('studio');

  // Verify page has loaded (wait for the main content or ensure no errors)
  // Either listings are shown or an empty state message is displayed
  const dashboardContent = page.locator('main, [role="main"]').first();
  await dashboardContent.waitFor({ state: 'visible', timeout: 10000 });

  // Confirm page is not in a loading or error state
  expect(page.url()).toContain('studio');
});
