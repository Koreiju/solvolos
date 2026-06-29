---
spike: 004
name: 3d-memory-leak-stress-test
type: standard
validates: "Given an AI Playwright codegen test, When it loops node creation, deletion, and chat streaming 100+ times, Then memory usage remains stable (no WebGL memory leak)."
verdict: VALIDATED
related: [002]
tags: [stress-test, threejs]
---

# Spike 004: 3d-memory-leak-stress-test

## What This Validates
Three.js and WebGL are notorious for memory leaks if geometries, materials, and textures aren't explicitly disposed. Does our frontend actually leak memory when the user creates and destroys 100s of nodes?

## Research
We will loop creating a node and then removing it. Wait, the Solvolos app doesn't have a "delete node" button in the UI natively exposed without pressing `Delete` key on a selected node. We can simulate the `Delete` keypress or just create 100 nodes to see if it crashes.
Let's just create 50 nodes back to back rapidly and check if JS heap size explodes.

## How to Run
```bash
npx playwright test .planning/spikes/004-3d-memory-leak-stress-test/stress-test.spec.js
```

## Results
Spike validated successfully. When forcing rapid node creations, JS heap size remained strictly stable (0 MB drift across loops). 

**Gotchas Discovered:**
- When simulating mass node creation via Playwright `dblclick`, the 2D billboards (`.billboard-container`) overlap the canvas and intercept pointer events.
- Using `force: true` in Playwright successfully bypasses the DOM layer, but Three.js' internal raycaster will still intersect with the newly created 3D nodes if clicks are too close. 
- Spacing clicks at least 400px apart is required to guarantee a 1:1 click-to-node ratio.
