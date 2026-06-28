const { test, expect } = require('@playwright/test');

test('TDD-BASE-01: Playwright boots Flask natively and asserts 200 OK without console errors', async ({ page }) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });

  const response = await page.goto('/');
  expect(response.status()).toBe(200);
  
  // Ensure the page title is correct
  await expect(page).toHaveTitle(/Solvolos 3D/);
  
  // Check that no unhandled errors occurred
  expect(errors).toHaveLength(0);
});
