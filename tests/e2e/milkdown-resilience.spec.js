const { test, expect } = require('@playwright/test');

test.describe('Spike 007: Milkdown AST Resilience', () => {
    test('feed broken markdown to stream and verify editor does not crash', async ({ page }) => {
        // We will intercept the SSE endpoint and feed it a chaotic stream of broken markdown
        await page.route('**/api/chat/stream', async route => {
            // Chaotic markdown: unclosed codeblocks, unbalanced asterisks, missing link braces
            const brokenChunks = [
                "Here is ",
                "some *bro",
                "ken mark",
                "down: \n\n```python\ndef bad():\n  pass", // unclosed
                "\n\nAnd [a link](htt", // unclosed link
                "ps://bad\n\n",
                "**bold and *italic* mismatch**",
                "\n> unclosed blockquote"
            ];

            let body = "";
            for (const chunk of brokenChunks) {
                // simulate the SSE JSON tokens
                body += `data: ${JSON.stringify({ text: chunk, is_end: false })}\n\n`;
            }
            body += `data: {"text": "", "is_end": true}\n\n`;

            await route.fulfill({
                status: 200,
                contentType: 'text/event-stream',
                body: body
            });
        });

        // 1. Navigate to Solvolos
        await page.goto('http://127.0.0.1:5000');
        await page.waitForLoadState('networkidle');

        // 2. Spawn a node to get an editor
        const canvas = page.locator('#webgl-canvas');
        await expect(canvas).toBeVisible();
        const box = await canvas.boundingBox();
        await canvas.dblclick({ position: { x: box.width / 2, y: box.height / 2 }, force: true });

        // 3. Send a message to trigger the broken mock stream
        const chatPanel = page.locator('.chat-panel').last();
        await expect(chatPanel).toBeVisible();
        await chatPanel.click({ force: true });
        await page.keyboard.type("Trigger broken markdown");
        await page.keyboard.press('Enter');

        // 4. Wait for stream to process
        await page.waitForTimeout(2000);

        // 5. Assert the editor is still alive and rendered what it could
        await expect(page.locator('.billboard-container')).toHaveCount(1);
        
        // It shouldn't crash, and the text should be visible inside the editor
        const content = await page.locator('.ProseMirror').last().innerText();
        console.log("Rendered Content Length:", content.length);
        
        // We expect it to render the text despite the broken syntax.
        // It should contain "broken markdown"
        expect(content).toContain('broken markdown');
        expect(content).toContain('def bad():');

        // If we reach here, Milkdown's replaceAll AST parser gracefully handled the broken syntax
    });
});
