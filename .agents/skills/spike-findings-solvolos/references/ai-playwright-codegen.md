# AI Playwright Codegen Engine

## Requirements

- Must support AI agent visually navigating the Solvolos UI logic (especially the `webgl-canvas` and `.billboard-container`).
- Must translate AI exploration traces into Playwright scripts (`.spec.js`).
- Must inject strict architectural constraints (`TDD-UI-06`, `TDD-UI-07`) universally into generated test scripts.

## How to Build It

1. **Browser Subagent**: Trigger an AI subagent to perform an exploration phase organically on the running `http://127.0.0.1:5000` instance.
2. **Synthesize Script**: Convert the subagent's event trace into Playwright code.
   - *Key adjustment*: For initial interactions like spawning a node, the synthesized test must target `#webgl-canvas` instead of `.ui-layer` because the WebGL canvas intercepts pointer events for raycasting.
     ```javascript
     const canvas = page.locator('#webgl-canvas');
     const box = await canvas.boundingBox();
     await canvas.dblclick({ position: { x: box.width / 2, y: box.height / 2 } });
     ```
3. **Hybrid Assertion Injection**: Append static assertions to the synthesized script enforcing overarching UI constraints. Ensure locators are specific enough (e.g. `billboard`) to avoid Playwright's strict mode violation that fails on wildcard selectors (`*`) matching multiple elements.
     ```javascript
     const billboard = page.locator('.billboard-container').first();
     await expect(billboard).toHaveCSS('background-color', 'rgb(0, 0, 0)');
     await expect(billboard.locator('button')).toHaveCount(0);
     ```

## What to Avoid

- Do not use wildcard locators `locator('*')` directly with assertions like `.toHaveCSS()` as it causes a Playwright strict mode violation.
- Do not assert hardcoded strings for LLM responses, as they are non-deterministic. Instead, use regex checks: `await expect(prosemirror).toContainText(/(Hello|Hi)/i, { timeout: 30000 });`

## Constraints

- Playwright tests default to a 30s timeout, which may need to be handled dynamically if LLM response generation takes longer during testing.

## Origin

Synthesized from spikes: 001, 002, 003
Source files available in: sources/001-ai-browser-navigation/, sources/002-ai-codegen-synthesis/, sources/003-hybrid-assertion-injection/
