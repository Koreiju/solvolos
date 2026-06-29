import { test, expect } from '@playwright/test';

test.describe('Synthetic Trace 001: Navigation and Retrieval', () => {
    test('organic subagent interaction trace', async ({ page }) => {
        // Step 1: Navigate to app
        await page.goto('http://127.0.0.1:5000/');
        
        // Ensure scene is loaded
        const canvas = page.locator('#webgl-canvas');
        await expect(canvas).toBeVisible();

        // Step 2: Double click center to create node
        const box = await canvas.boundingBox();
        await canvas.dblclick({ position: { x: box.width / 2, y: box.height / 2 } });

        // Verify billboard is created
        const billboard = page.locator('.billboard-container').first();
        await expect(billboard).toBeVisible();

        // Step 3: Chat panel input and send
        const chatPanel = billboard.locator('.chat-panel');
        await chatPanel.click();
        
        // In playwright we can't type directly if it's not a standard input, but we can evaluate or use keyboard
        // The subagent used keyboard simulation
        await page.keyboard.type('Hello, world!');
        await page.keyboard.press('Enter');

        // Step 4: Verify streaming response in Milkdown
        const prosemirror = billboard.locator('.ProseMirror');
        // Wait for streaming to finish by waiting for the response text to appear
        // The LLM response usually contains "Hello" or "Hi there"
        await expect(prosemirror).toContainText(/(Hello|Hi)/i, { timeout: 30000 });

        // Step 5: Retrieval interaction
        await chatPanel.click();
        await page.keyboard.type('\\Hello');
        
        // Wait for popup
        const popup = billboard.locator('.reference-popup');
        await expect(popup).toBeVisible();
        
        // Click first item
        const popupItem = popup.locator('.popup-item').first();
        await popupItem.click();

        // Step 6: Verify embedded text
        // Note: Playwright doesn't easily assert the precise span structure of contenteditable 
        // without getting innerText, so we assert the text content includes the crystal ball
        await expect(chatPanel).toContainText('🔮');

        // --- STATIC HYBRID ASSERTION INJECTION ---
        // These are universally injected by the Synthesizer from architecture/MAIN.md constraints
        
        // Assert TDD-UI-06: Background must be exactly #000000 (rgb(0, 0, 0))
        await expect(billboard).toHaveCSS('background-color', 'rgb(0, 0, 0)');
        
        // Assert TDD-UI-07: No buttons or .label allowed
        await expect(billboard.locator('button')).toHaveCount(0);
        await expect(billboard.locator('.label')).toHaveCount(0);
        await expect(billboard).toHaveCSS('border-radius', '0px');
        await expect(chatPanel).toHaveCSS('border-radius', '0px');
    });
});
