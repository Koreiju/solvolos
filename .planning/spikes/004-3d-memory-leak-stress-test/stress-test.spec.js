import { test, expect } from '@playwright/test';

test.describe('Spike 004: 3D Memory Leak Stress Test', () => {
    test('stress test WebGL memory by looping node creation', async ({ page }) => {
        // Step 1: Navigate to app
        await page.goto('http://127.0.0.1:5000/');
        
        // Ensure scene is loaded
        const canvas = page.locator('#webgl-canvas');
        await expect(canvas).toBeVisible();

        const getMemory = async () => {
            return await page.evaluate(() => {
                if (performance && performance.memory) {
                    return performance.memory.usedJSHeapSize;
                }
                return 0;
            });
        };

        const initialMemory = await getMemory();
        console.log(`Initial Memory: ${initialMemory / (1024 * 1024)} MB`);

        // Loop 50 times to spawn nodes
        for (let i = 0; i < 50; i++) {
            const box = await canvas.boundingBox();
            // offset slightly so we don't click exactly the same spot
            const offset = (i * 5) % 100;
            await canvas.dblclick({ position: { x: box.width / 2 + offset, y: box.height / 2 + offset } });

            // Type and submit chat
            const billboard = page.locator('.billboard-container').last();
            await expect(billboard).toBeVisible();
            const chatPanel = billboard.locator('.chat-panel');
            await chatPanel.click();
            await page.keyboard.type(`Stress message ${i}`);
            await page.keyboard.press('Enter');

            // Wait a tiny bit for the stream to at least start
            await page.waitForTimeout(100);
        }

        // Wait a few seconds for all streams to settle and geometry to update
        await page.waitForTimeout(5000);

        const finalMemory = await getMemory();
        console.log(`Final Memory: ${finalMemory / (1024 * 1024)} MB`);

        // Check that memory didn't explode astronomically (e.g., > 500MB increase)
        // Note: 50 nodes might take some memory, but shouldn't leak endlessly
        const diffMB = (finalMemory - initialMemory) / (1024 * 1024);
        console.log(`Memory Difference: ${diffMB} MB`);
        
        // We assert the browser hasn't crashed and elements are present
        await expect(page.locator('.billboard-container')).toHaveCount(50);
        
        // Assert that memory leak isn't over 100MB for just 50 nodes
        expect(diffMB).toBeLessThan(100);
    });
});
