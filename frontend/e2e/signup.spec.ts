import { test, expect } from '@playwright/test';

test('signup: user can register and redirect to home', async ({ page }) => {
  // Generate unique email with timestamp suffix to avoid duplicate signup collisions
  const timestamp = Date.now();
  const testEmail = `testuser+${timestamp}@example.com`;
  const testPassword = 'TestPassword123456';
  const testUsername = `testuser${timestamp % 1000000}`;

  // Navigate to signup page
  await page.goto('/signup');

  // Fill in all required fields using actual form field IDs
  await page.fill('#form-signup-firstname', 'Jane');
  await page.fill('#form-signup-lastname', 'Doe');
  await page.fill('#form-signup-email', testEmail);
  await page.fill('#form-signup-username', testUsername);
  await page.fill('#form-signup-password', testPassword);
  await page.fill('#form-signup-confirm-password', testPassword);

  // Submit the form by clicking the "Create account" button
  await page.click('button[form="form-signup"]');

  // Wait for redirect to home page
  await page.waitForURL('/', { timeout: 30000 });

  // Verify we're on the home page
  expect(page.url()).toBe('http://localhost:3000/');
});
