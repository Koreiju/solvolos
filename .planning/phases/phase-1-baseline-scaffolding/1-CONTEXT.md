# Phase 1 Context & Decisions

This document captures the decisions made during the `gsd-discuss-phase 1` execution regarding the project's baseline scaffolding and testing environment. These decisions are locked and should guide all downstream research and planning for this phase.

## Decisions

### 1. Testing Environment (Playwright to Flask)
**Decision**: Native `subprocess` runner inside the JS test config.
**Rationale**: Docker containerization introduces unnecessary overhead for a local-first application. Flask will be booted natively via Python `subprocess` during Playwright's `globalSetup` to ensure tests run fast and have direct access to the local filesystem for KuzuDB.

### 2. Node Package Manager
**Decision**: `npm`.
**Rationale**: As this is a vanilla JS application with no bundler (Webpack/Vite), Node is only required for Playwright and ESLint. Standard `npm` is sufficient and avoids adding another dependency layer.

### 3. KuzuDB Test Isolation
**Decision**: Fresh temporary directory per test suite.
**Rationale**: KuzuDB is an embedded file-based database. To prevent state contamination and properly test transaction locking concurrency without false positives, every test run will spin up its own temporary Kuzu directory (`/tmp/kuzu_test_xxx`) and tear it down upon completion. Mocks will not be used, as we specifically need to test the Kuzu C++ engine's behavior under load.
