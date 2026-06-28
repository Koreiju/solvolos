const { test, expect } = require('@playwright/test');
const { ProjectorApp } = require('../../static/js/projector');

test('TDD-UI-06: Brutalist Compliance', async ({ page }) => {
    await page.goto('/');
    
    // Inject test elements
    await page.evaluate(() => {
        const billboard = document.createElement('div');
        billboard.className = 'secondary-billboard';
        document.body.appendChild(billboard);
        
        const milkdown = document.createElement('div');
        milkdown.className = 'milkdown';
        document.body.appendChild(milkdown);
    });
    
    const billboard = page.locator('.secondary-billboard');
    const milkdown = page.locator('.milkdown');
    
    // Assert Computed CSS
    const bbStyle = await billboard.evaluate(el => window.getComputedStyle(el));
    expect(bbStyle.backgroundColor).toBe('rgb(0, 0, 0)');
    expect(bbStyle.borderRadius).toBe('0px');
    
    const mkStyle = await milkdown.evaluate(el => window.getComputedStyle(el));
    expect(mkStyle.backgroundColor).toBe('rgb(0, 0, 0)');
    expect(mkStyle.borderRadius).toBe('0px');
});

test('TDD-UI-07: No UI Bloat', async ({ page }) => {
    await page.goto('/');
    
    // Attempt to inject bloat and check display
    await page.evaluate(() => {
        const billboard = document.createElement('div');
        billboard.className = 'billboard-container';
        
        const label = document.createElement('div');
        label.className = 'label';
        
        const button = document.createElement('button');
        
        billboard.appendChild(label);
        billboard.appendChild(button);
        document.body.appendChild(billboard);
    });
    
    const label = page.locator('.label');
    const button = page.locator('button');
    
    const labelStyle = await label.evaluate(el => window.getComputedStyle(el));
    expect(labelStyle.display).toBe('none');
    
    const buttonStyle = await button.evaluate(el => window.getComputedStyle(el));
    expect(buttonStyle.display).toBe('none');
});

test('TDD-PHY-06: Coordinate Un-Projection', async () => {
    const app = new ProjectorApp();
    
    const nodeState = {
        isLocked: true,
        domX: 1920 / 2, // Center of width
        domY: 1080 / 2  // Center of height
    };
    
    // In node environment, window is undefined, width/height fall back to 1920x1080
    const endpoint = app.calculateEdgeEndpoint(nodeState);
    
    // Center should map to (0, 0, 0) in 3D projection
    expect(endpoint.x).toBe(0);
    expect(endpoint.y).toBe(0);
    expect(endpoint.z).toBe(0);
    
    const nodeStateTopLeft = {
        isLocked: true,
        domX: 0,
        domY: 0
    };
    
    const endpointTL = app.calculateEdgeEndpoint(nodeStateTopLeft);
    expect(endpointTL.x).toBe(-5);
    expect(endpointTL.y).toBe(5);
    expect(endpointTL.z).toBe(0);
});
