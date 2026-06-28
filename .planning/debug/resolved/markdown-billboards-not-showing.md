---
status: resolved
trigger: "milkdown billboards still don't show when double-clicking to create a new node"
created: 2026-06-27T18:01:45
updated: 2026-06-27T21:49:00
---

# Debug Session: markdown-billboards-not-showing

## Symptoms
1. **Expected behavior**: Double-clicking to create a node should open the 2D billboard panel to display Milkdown editor.
2. **Actual behavior**: Node creates in 3D but billboard doesn't appear. Server eventually crashed in the user's terminal causing `ERR_CONNECTION_REFUSED`.
3. **Timeline**: Started when Milkdown v7 was added.

## Resolution
- **root_cause**: 
  1. The Flask dev server crashed due to hot-reloading when database locks were briefly held during restart. This caused the user's browser to fail when trying to connect or `POST /api/nodes/create`.
  2. Milkdown v7 has significant changes to its plugin architecture. `plugin-slash` and `plugin-tooltip` no longer export `slash` and `tooltip` directly, and instead require using `slashFactory` and providing a custom DOM view (`SlashProvider`), which we haven't implemented yet. The use of `.use(slashFactory)` instead of `.use(slashFactory('name'))` also threw `TypeError: n is not a function` during `Editor.create()`.
- **fix**: 
  1. Implemented cache busting `?v=3` in `index.html` to guarantee the browser gets the latest script.
  2. Removed `slash` and `tooltip` plugins from `billboard.js` entirely for now, as they require custom headless UI setup in v7. We can implement these later using their respective Providers when we build out custom Slash command popups.
  3. The `history`, `clipboard`, `prism`, and `listener` plugins are now properly configured and initializing.
- **verification**: The browser subagent successfully double-clicked the canvas, the billboard slid into view, and the subagent successfully typed "Hello World" into the rendered ProseMirror editor.
- **files_changed**: `milkdown_app/ui/templates/index.html`, `milkdown_app/ui/static/js/billboard.js`
