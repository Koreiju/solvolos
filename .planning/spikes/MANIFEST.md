# Spike Manifest

## Idea
Prototype an AI Playwright Codegen subagent that can autonomously explore the Solvolos app organically based on high-level goals and synthesize its interaction trace into a deterministic Playwright `.spec.js` script, augmented with static architectural assertions.

## Requirements
- Generated code must be valid Playwright `.spec.js` format.
- Synthetic assertions (like background color and element filters) must be injected unconditionally.
- Must execute the sequence through a simulated subagent environment, proving it can trace dynamically.

## Spikes

| # | Name | Type | Validates | Verdict | Tags |
|---|------|------|-----------|---------|------|
| 001 | ai-browser-navigation | standard | Given the Solvolos app running, when a browser subagent is prompted to create a node and run a slash retrieval, then it successfully completes the actions visually. | VALIDATED | [codegen, subagent, playwright] |
| 002 | ai-codegen-synthesis | standard | Given the subagent's successful trace, when it is prompted to synthesize its interactions, then it outputs a valid Playwright `.spec.js` script containing the correct locators and actions. | VALIDATED | [codegen, generation] |
| 003 | hybrid-assertion-injection | standard | Given a synthesized script, when static architectural rules (e.g. background `#000000`) are supplied, then they are correctly appended into the generated assertions. | VALIDATED | [assertions, testing] |
| 004 | 3d-memory-leak-stress-test | standard | Given an AI Playwright codegen test, When it loops node creation, deletion, and chat streaming 100+ times, Then memory usage remains stable (no WebGL memory leak). | VALIDATED | [stress-test, threejs] |
| 005 | kuzu-graph-recursive-chunking | standard | Given a complex markdown message, When saved to backend, Then KuzuDB correctly splits it into recursive ChunkNodes and links them. | VALIDATED | [kuzudb, backend] |
| 006 | semantic-umap-projection | standard | Given a mock set of 50 semantic chunk vectors, When processed by our local UMAP pipeline, Then it accurately reduces them to 3D coordinates. | VALIDATED | [umap, ml] |
| 007 | milkdown-ast-resilience | standard | Given a Playwright synthetic test, When the chat panel is force-fed broken markdown, Then the Milkdown AST streaming parser gracefully handles it. | VALIDATED | [milkdown, resilience] |
