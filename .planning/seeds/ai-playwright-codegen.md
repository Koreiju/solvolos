# Seed: AI-Driven Playwright Codegen Engine

## Trigger
Execute this seed during **Phase 9/10: Automated QA scaling and Simulation** or when the testing payload gets too large for manual Playwright `.spec.js` scripting.

## Concept
We need a system that harnesses our local agent framework to act as an exploratory end-user. The AI agent navigates the Solvolos app (double-clicking to spawn nodes, executing retrieval gestures, sending multi-turn LLM chats) and distills its entire session trace into a permanent, deterministic Playwright script.

### Key Components:
1. **The Explorer Agent**: Uses `browser_subagent` capabilities to organically test the app based on high-level personas/goals (e.g., "Create a 3-node graph using retrieval logic").
2. **The DOM Snapshotter**: Reads the DOM delta after every action to formulate dynamic `expect(locator).toHaveText()` assertions based on actual runtime results.
3. **The Static Injector**: Injects universal architectural assertions (from `gsd-model-design-test`) blindly into every generated suite to guarantee base constraints.
4. **The Synthesizer**: Compiles the interaction trace, DOM snapshots, and static rules into valid JS/Playwright code (`tests/e2e/synthetic-*.spec.js`).

## Expected Output
A fully autonomous script generation pipeline that creates resilient Playwright integration tests directly from emergent AI-led usage patterns.
