import { test, expect } from '@playwright/test';

test('signin: user can sign in with registered credentials', async ({ page }) => {
  // Generate unique email with timestamp suffix for a fresh user
  const timestamp = Date.now();
  const testEmail = `testuser+${timestamp}@example.com`;
  const testPassword = 'TestPassword123456';
  const testUsername = `testuser${timestamp}`.slice(0, 30);

  // First, register a new user via signup
  await page.goto('/signup');
  await page.fill('#form-signup-firstname', 'John');
  await page.fill('#form-signup-lastname', 'Doe');
  await page.fill('#form-signup-email', testEmail);
  await page.fill('#form-signup-username', testUsername);
  await page.fill('#form-signup-password', testPassword);
  await page.fill('#form-signup-confirm-password', testPassword);
  await page.click('button[form="form-signup"]');

  // Wait for redirect to home after signup
  await page.waitForURL('/', { timeout: 30000 });

  // Clear localStorage to force signin flow (removes auth tokens)
  await page.evaluate(() => localStorage.clear());

  // Navigate to signin page
  await page.goto('/signin');

  // Fill in signin form with the credentials used during signup
  await page.fill('#form-signin-email', testEmail);
  await page.fill('#form-signin-password', testPassword);

  // Submit the signin form
  await page.click('button[form="form-login"]');

  // Wait for redirect to home page after successful signin
  await page.waitForURL('/', { timeout: 30000 });

  // Verify we're on the home page
  expect(new URL(page.url()).pathname).toBe('/');
});
