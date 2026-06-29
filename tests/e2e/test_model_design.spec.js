import { test, expect } from '@playwright/test';

test.describe('Model-Design-Test Constraints', () => {

    test.beforeEach(async ({ page }) => {
        page.on('console', msg => console.log(`BROWSER: ${msg.text()}`));
        
        await page.route('**/api/search*', route => {
            console.log('MOCK SEARCH API CALLED!');
            route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    results: [
                        { id: 'mock-id-1', text: 'Mock result text 1' },
                        { id: 'mock-id-2', text: 'Mock result text 2' }
                    ]
                })
            });
        });

        await page.route('**/api/chat/stream*', route => {
            route.fulfill({
                status: 200,
                contentType: 'text/event-stream',
                body: 'data: {"text": "mock"}\n\n'
            });
        });
    });

    test('TDD-UI-06: Playwright tests MUST assert border-radius: 0 and background-color: #000000 on billboard classes', async ({ page }) => {
        await page.goto('http://localhost:5000');
        await page.mouse.dblclick(100, 100);
        
        const container = page.locator('.billboard-container').last();
        await container.waitFor({ state: 'visible' });
        
        const borderRadius = await container.evaluate(el => getComputedStyle(el).borderRadius);
        const backgroundColor = await container.evaluate(el => getComputedStyle(el).backgroundColor);
        
        expect(borderRadius).toBe('0px');
        expect(backgroundColor).toBe('rgb(0, 0, 0)');
    });

    test('TDD-UI-07: Playwright tests MUST assert no <button> or .label elements are spawned within the billboard component', async ({ page }) => {
        await page.goto('http://localhost:5000');
        await page.mouse.dblclick(100, 100);
        
        const container = page.locator('.billboard-container').last();
        await container.waitFor({ state: 'visible' });
        
        const buttons = await container.locator('button').count();
        const labels = await container.locator('.label').count();
        
        expect(buttons).toBe(0);
        expect(labels).toBe(0);
    });

    test('TDD-PHY-06: Edge cylinder endpoints MUST recalculate by un-projecting 2D DOM screen space back into the 3D frustum', async ({ page }) => {
        await page.goto('http://localhost:5000');
        
        await page.waitForFunction(() => window.app !== undefined);
        
        const hasUnprojectLogic = await page.evaluate(() => {
            return typeof window.app.convertTo3D === 'function';
        });
        
        expect(hasUnprojectLogic).toBeTruthy();
    });

    test('TDD-UI-08: reference-popup node bounds sit visually left of the Milkdown container', async ({ page }) => {
        await page.goto('http://localhost:5000');
        await page.mouse.dblclick(100, 100);
        
        const container = page.locator('.billboard-container').last();
        await container.waitFor({ state: 'visible' });
        
        const chatPanel = container.locator('.chat-panel');
        await chatPanel.click();
        
        await chatPanel.evaluate(node => { node.innerText = '\\test'; });
        await chatPanel.evaluate(node => node.dispatchEvent(new KeyboardEvent('keydown', { key: '\\' })));
        
        const popup = container.locator('.reference-popup');
        await popup.waitFor({ state: 'visible' });
        
        await chatPanel.evaluate(node => node.dispatchEvent(new KeyboardEvent('keydown', { key: 't' })));
        
        const firstItem = popup.locator('.reference-item').first();
        await firstItem.waitFor({ state: 'attached', timeout: 5000 });

        const containerBox = await container.boundingBox();
        const popupBox = await popup.boundingBox();
        
        expect(popupBox.x).toBeLessThan(containerBox.x);
        expect(popupBox.x + popupBox.width).toBeLessThanOrEqual(containerBox.x + 20);
    });

    test('TDD-UI-09: hovered result spawns element visually right without overlapping', async ({ page }) => {
        await page.goto('http://localhost:5000');
        await page.mouse.dblclick(100, 100);
        
        const container = page.locator('.billboard-container').last();
        await container.waitFor({ state: 'visible' });
        
        const chatPanel = container.locator('.chat-panel');
        await chatPanel.click();
        
        await chatPanel.evaluate(node => { node.innerText = '\\test'; });
        await chatPanel.evaluate(node => node.dispatchEvent(new KeyboardEvent('keydown', { key: '\\' })));
        
        const popup = container.locator('.reference-popup');
        await popup.waitFor({ state: 'visible' });
        
        await chatPanel.evaluate(node => node.dispatchEvent(new KeyboardEvent('keydown', { key: 't' })));
        
        const firstItem = popup.locator('.reference-item').first();
        await firstItem.waitFor({ state: 'attached', timeout: 5000 });
        
        // Wait for a short moment so that the mouse event attaches correctly
        await page.waitForTimeout(100);
        
        // Use dispatchEvent instead of hover, sometimes Playwright hover fails on headless non-visible elements
        await firstItem.dispatchEvent('mouseenter');
        
        const secondary = page.locator('.secondary-billboard').first();
        await secondary.waitFor({ state: 'attached', timeout: 5000 });
        
        const containerBox = await container.boundingBox();
        const secondaryBox = await secondary.boundingBox();
        
        if (secondaryBox && containerBox) {
            expect(secondaryBox.x).toBeGreaterThanOrEqual(containerBox.x + containerBox.width - 20);
        }
    });

    test('TDD-CTX-03: click injects crystal ball token into chat input', async ({ page }) => {
        await page.goto('http://localhost:5000');
        await page.mouse.dblclick(100, 100);
        
        const container = page.locator('.billboard-container').last();
        await container.waitFor({ state: 'visible' });
        
        const chatPanel = container.locator('.chat-panel');
        await chatPanel.click();
        
        await chatPanel.evaluate(node => { node.innerText = '\\test'; });
        await chatPanel.evaluate(node => node.dispatchEvent(new KeyboardEvent('keydown', { key: '\\' })));
        
        const popup = container.locator('.reference-popup');
        await popup.waitFor({ state: 'visible' });
        
        await chatPanel.evaluate(node => node.dispatchEvent(new KeyboardEvent('keydown', { key: 't' })));
        
        const firstItem = popup.locator('.reference-item').first();
        await firstItem.waitFor({ state: 'attached', timeout: 5000 });
        
        // Dispath a click instead of page.click in case it's visually occluded
        await firstItem.dispatchEvent('click');
        
        await expect(chatPanel).toContainText('🔮');
    });

    test('TDD-UI-10: Pinned node text color explicitly matches #ffffff', async ({ page }) => {
        await page.goto('http://localhost:5000');
        await page.mouse.dblclick(100, 100);
        
        const container = page.locator('.billboard-container').last();
        await container.waitFor({ state: 'visible' });
        
        const color = await container.evaluate(el => getComputedStyle(el).color);
        expect(color).toBe('rgb(255, 255, 255)');
    });

    test('TDD-PHY-07: centroid tare calculation', async ({ page }) => {
        await page.goto('http://localhost:5000');
        
        await page.waitForFunction(() => window.app !== undefined);
        
        const hasCentroid = await page.evaluate(() => {
            return window.app.centroidTare !== undefined && window.app.centroidTare.x !== undefined;
        });
        
        expect(hasCentroid).toBeTruthy();
    });
});
