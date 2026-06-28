# Phase 8: UI Implementation & Polish - UI Specification

## 1. Aesthetic Guidelines (Brutalist Black)
- **Background**: All nodes, panels, and billboards MUST be solid black (`#000000`).
- **Borders**: All corners MUST be perfectly sharp (`border-radius: 0`). No rounding whatsoever.
- **Chrome/Noise**: Remove all extra UI elements. No title labels, no "X" close buttons, no traditional window chrome.

## 2. Dynamic Text Colors (UMAP HSV)
The core visual indicator of a node's semantic position is its text color.
- The 6D UMAP data array `[x, y, z, h, s, v]` dictates the color of the text.
- **In 3D Space**: The `BlackSlatePanel` text mesh continuously rotates its HSV values based on the `[h, s, v]` vector payload.
- **In 2D Space**: The `MilkdownBillboard` DOM element must sync this exact same rotating HSV color to its `color` CSS property, ensuring the text visually aligns with the 3D representation even when pinned.

## 3. Cross-Dimensional Edge Linking
Cylindrical edge connections must persist regardless of where the connected nodes reside.
- **3D-to-3D**: Standard WebGL coordinate bridging.
- **3D-to-2D**: When Node A is a pinned DOM billboard (2D) and Node B is a floating BlackSlatePanel (3D), the edge renderer must un-project the screen-space bounding box of Node A back into the 3D frustum to anchor the cylinder endpoint to the billboard.
- **2D-to-2D**: When both Node A and Node B are pinned billboards (e.g., retrieving an external reference via `/` and pinning it), the edge renderer must un-project both DOM elements into the WebGL scene behind them to render a connecting cylinder.

## 4. UI Implementation Tasks
- Update `main.css` to enforce the `#000000` and `border-radius: 0` rules globally on `.billboard-container`.
- Update `billboard.js` DOM construction to strip out label/close buttons.
- Update `projector.js` to implement the `EdgeRenderer` projection math for `project2DTo3D()`.
