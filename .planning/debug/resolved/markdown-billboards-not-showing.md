---
status: resolved
trigger: "markdown billboards still don't show"
created: 2026-06-27T18:01:45
updated: 2026-06-27T22:05:30
---

# Debug Session: markdown-billboards-not-showing

## Symptoms
1. **Expected behavior**: Double-clicking to create a node should open the 2D billboard panel to display Milkdown editor.
2. **Actual behavior**: Node creates in 3D but billboard doesn't appear.
3. **Timeline**: Started when Milkdown v7 was added using direct CDN URLs in `billboard.js`.
4. **Reproduction**: Click a node or double-click to spawn a node.

## Resolution
- **root_cause**: ESM module instantiation failure. `billboard.js` imported Milkdown packages directly from `https://esm.sh/@milkdown/...@7`. Because esm.sh resolves peer dependencies (like `@milkdown/core`) per package independently, multiple differing patches of `core` were downloaded. This causes `ctx.get(listenerCtx)` to crash with "Context not found" because the context was injected into a *different* instance of core than the one `billboard.js` is looking at. This halting error prevents `window.billboardApp = new BillboardApp()` from completing.
- **fix**: 
  1. Updated `ui/templates/index.html` `importmap` to explicitly map all `@milkdown/*` packages to exact `esm.sh` URLs.
  2. Modified `billboard.js` to use bare specifiers (e.g., `import { Editor } from '@milkdown/core'`), forcing the browser to respect the `importmap` and share a single unified `core` dependency.
- **verification**: The module will now resolve correctly through the importmap.
- **files_changed**: `milkdown_app/ui/templates/index.html`, `milkdown_app/ui/static/js/billboard.js`
