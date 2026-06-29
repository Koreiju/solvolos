import { test, expect } from '@playwright/test';

test.describe('Spike 004: 3D Memory Leak Stress Test', () => {
    test('stress test WebGL memory by looping node creation', async ({ page }) => {
        test.setTimeout(120000);
        // Step 1: Navigate to app
        await page.goto('http://127.0.0.1:5000/');
        
        // Ensure scene is loaded
        const canvas = page.locator('#webgl-canvas');
        await expect(canvas).toBeVisible();

        // MOCK the /api/chat/stream to respond instantly and avoid LLM bottleneck
        await page.route('/api/chat/stream', async route => {
            const body = `data: {"text": "Fast ", "is_end": false}\n\ndata: {"text": "mock ", "is_end": false}\n\ndata: {"text": "response!", "is_end": true}\n\n`;
            await route.fulfill({
                status: 200,
                contentType: 'text/event-stream',
                body: body
            });
        });

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

        // Loop 50 times to spawn nodes using grid offsets
        for (let i = 0; i < 50; i++) {
            const box = await canvas.boundingBox();
            const row = Math.floor(i / 10);
            const col = i % 10;
            const offsetX = col * 80 - 350; 
            const offsetY = row * 80 - 150; 
            await canvas.dblclick({ position: { x: box.width / 2 + offsetX, y: box.height / 2 + offsetY }, force: true });

            // wait a tiny bit to make sure it spawned
            await page.waitForTimeout(50);
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

        // Assert that memory leak isn't over 100MB for 50 nodes
        expect(diffMB).toBeLessThan(100);
    });
});
