const { test, expect } = require('@playwright/test');
const { HoverCrystalBall } = require('../../static/js/billboard');

test('TDD-UI-04: Semantic slash spawns secondary billboard and clicking pins it', async ({ page }) => {
    await page.goto('/');
    
    // Inject test DOM setup
    await page.evaluate(() => {
        const editor = document.createElement('div');
        editor.className = 'milkdown';
        document.body.appendChild(editor);
        
        const input = document.createElement('input');
        editor.appendChild(input);
        input.focus();
    });
    
    // Type '/'
    await page.keyboard.type('/');
    
    // Wait for the 150ms debounce
    await page.waitForTimeout(200);
    
    // Assert secondary-billboard appears
    const billboard = page.locator('.secondary-billboard');
    await expect(billboard).toBeVisible();
    
    // Click and assert pinned class
    await billboard.click({ force: true });
    await expect(billboard).toHaveClass(/pinned/);
});

test('TDD-UI-05: Hover debounce restricts spam to exactly one fetch/panel', async () => {
    // We can test this in Node environment directly using our exported class
    const crystalBall = new HoverCrystalBall();
    
    // Rapidly trigger 10 hovers
    for (let i = 0; i < 10; i++) {
        crystalBall.handleHover(`result-${i}`, 0, 0);
    }
    
    // Immediately fetchCount should be 0 (debounced)
    expect(crystalBall.fetchCount).toBe(0);
    
    // Wait for 200ms using a Promise
    await new Promise(resolve => setTimeout(resolve, 200));
    
    // Assert exactly 1 fetch executed
    expect(crystalBall.fetchCount).toBe(1);
});
