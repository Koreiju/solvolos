# Phase 2: Editable Milkdown and Chat Sync Verification - Plan

## Goal
Verify that the core chat functionality and editable Milkdown nodes are fully synchronized.

## Tasks
1. **Fix Milkdown Plugin Errors:**
   - The browser was previously complaining about `slash` and `slashFactory`. We need to ensure that all Milkdown v7 plugins (`slash`, `tooltip`, `listener`, `prism`, `clipboard`, `history`) are correctly initialized.
   - For v7, plugins like `slash` are generated via `slashFactory`. Ensure we are using `slashFactory` correctly with `.use()`.
2. **Double-Click Node Editing:**
   - Verify that double-clicking a node correctly targets the node, stops propagation, opens the 2D billboard in front of the camera, and initializes Milkdown with the node's content.
   - Verify that edits made in Milkdown push updates to the backend and update the node's 3D projection.
3. **Chat Sync Verification:**
   - Verify that chat messages sent from the UI (either the chat panel or the editable billboard) correctly trigger the recursive chunking pipeline.
   - Verify the SSE stream correctly pushes new chunks back to the client and they render in the scene dynamically without crashing the billboard.

## Output
- Tested and functioning `billboard.js`.
- Error-free console logs in the browser.
