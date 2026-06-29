---
spike: 002
name: ai-codegen-synthesis
type: standard
validates: "Given the subagent's successful trace, when it is prompted to synthesize its interactions, then it outputs a valid Playwright `.spec.js` script containing the correct locators and actions."
verdict: VALIDATED
related: [001]
tags: [codegen, generation]
---

# Spike 002: AI Codegen Synthesis

## What This Validates
Can we successfully synthesize the actions taken by the AI in Spike 001 into a deterministic Playwright test that actually passes against the UI logic?

## Research
In Spike 001, the AI executed the following:
1. Double click center of `#ui-layer` or `#webgl-canvas` to spawn `.billboard-container`.
2. Click `.chat-panel`, type "Hello, world!", press Enter.
3. Wait for stream to complete (checking `.ProseMirror` contents).
4. Click `.chat-panel`, type `\Hello`, wait for `.reference-popup`, click `.popup-item`.
5. Verify `.chat-panel` contains embedded `[ 🔮 Hello!...](node://...)`.

## How to Run
```bash
npx playwright test .planning/spikes/002-ai-codegen-synthesis/synthetic-001.spec.js
```

## Results
We successfully generated `synthetic-001.spec.js` using the exact trace from Spike 001.
We ran `npx playwright test tests/e2e/synthetic-001.spec.js` and it successfully passed.

**Key Finding**: Playwright can easily re-create the AI trace, but a minor adjustment was needed: we had to target `#webgl-canvas` for the initial click instead of `#ui-layer` because the canvas intercepts 3D pointer events. This proves that an AI Synthesizer could read the DOM event trace and compile it into extremely robust tests that pass locally.
