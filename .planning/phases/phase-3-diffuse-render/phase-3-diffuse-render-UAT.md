# Phase 3 Diffuse Render UAT

## Frontend TDD Constraints

- [ ] pending: **UAT-DIF-01**: Stream an AI markdown header `chunk_type` that matches no existing type in AST; UI MUST default safely to the bottom of the document rather than throwing a parsing error (Maps to `TDD-DIF-01` in `diffuse_render.test.js`).
- [ ] pending: **UAT-DIF-02**: Pass a deliberately fractured JSON string across network frames; UI MUST buffer the SSE tokens rather than crashing with a SyntaxError (Maps to `TDD-DIF-02`).
- [ ] pending: **UAT-UI-01**: Playwright MUST verify double-clicking the background spawns a pinned 2D Milkdown editor with no 3D sphere primitive.
- [ ] pending: **UAT-UI-02**: Playwright MUST verify instant markdown AST rendering of nested lists/tables upon keystrokes.
- [ ] pending: **UAT-UI-03**: Playwright MUST verify the chat panel adaptively grows on focus and collapses to exactly 3 lines on blur.
- [ ] pending: **UAT-UI-04**: Playwright MUST verify the forward-slash (`/`) operator triggers the hover-linked secondary billboard, and clicking pins it.
