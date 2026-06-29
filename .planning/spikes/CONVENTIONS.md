# Spike Conventions

Patterns and stack choices established across spike sessions. New spikes follow these unless the question requires otherwise.

## Stack
- Backend: Flask serving HTML and running ML tasks natively on port 5000.
- Frontend: Vanilla JS + CSS, Three.js, Milkdown.
- Testing/QA: Playwright (`@playwright/test`) running locally against `http://127.0.0.1:5000`.

## Structure
- Playwright tests are stored in `tests/e2e/`.

## Patterns
- **AI UI Navigation:** When an AI agent explores the UI, it must click the `#webgl-canvas` instead of the 2D wrapper (`#ui-layer`) to spawn 3D nodes, because the canvas natively intercepts raycast pointers.
- **Dynamic Assertions:** When querying LLM responses in UI testing, tests must use partial Regex substring matching (e.g., `/(Hello|Hi)/i`) rather than exact hardcoded strings because LLMs are inherently non-deterministic.
- **Architectural UI Constraints:** We universally enforce static rules (like pure black background via `TDD-UI-06`) on all generated traces. When doing this, assertions must target high-level components (e.g. `.billboard-container`) because Playwright strict mode will fail wildcard `*` assertions if they resolve to multiple descendant elements.

## Tools & Libraries
- `playwright` for synthetic browser codegen.
