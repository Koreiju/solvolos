import { test, expect } from '@playwright/test';

test.describe('Manual UI Goal Verification', () => {
    test('User Story: Fullstack verification flow', async ({ page }) => {
        test.setTimeout(180000); // 3 minutes for ML download and inference
        // Go to local instance
        await page.goto('/');

        // 1. Double click on empty background
        await page.mouse.dblclick(500, 500);

        // Wait for billboard container to spawn
        const billboard = page.locator('.billboard-container').first();
        await expect(billboard).toBeVisible();

        // 2. Type in markdown fields
        const milkdown = billboard.locator('.milkdown').first();
        await expect(milkdown).toBeVisible();

        // 3. Chat panel at the bottom of the billboard
        const chatPanel = billboard.locator('.chat-panel');
        await expect(chatPanel).toBeVisible();
        
        // Wait a bit to simulate manual view
        await page.waitForTimeout(1000);

        // 4. Type and hit enter in chat panel
        await chatPanel.click();
        await chatPanel.fill('Can you verify the isomorphism?');
        await page.keyboard.press('Enter');

        // Wait for AI stream to populate milkdown editor
        await page.waitForFunction(() => {
            const editor = document.querySelector('.milkdown');
            return editor && editor.innerText.length > 50;
        }, { timeout: 120000 });
        
        const milkdownText = await milkdown.innerText();
        expect(milkdownText).toContain('AI Response');

        // 7. Right-click fly back
        await billboard.click({ button: 'right' });

        // Verify container is transferred to WebGL CSS3DRenderer (converted to CSS3DObject)
        const isConverted = await page.evaluate(() => {
            return window.app.css3dObjects.size > 0;
        });
        expect(isConverted).toBeTruthy();
        // 11. Slash operator popup
        await milkdown.click();
        await page.keyboard.press('/');
        await page.waitForTimeout(500);
        const hoverPanel = page.locator('.hover-panel').first();
        await expect(hoverPanel).toBeVisible();
        await expect(hoverPanel).toHaveText('Result: slash-search');
        
        // Final review delay for screenshots/tracing
        await page.waitForTimeout(1000);
    });
});
