# Requirements

## v1 Requirements

### Core Architecture
- [ ] **CORE-01**: Local LLM Chat generation with SSE streaming endpoints
- [ ] **CORE-02**: Graph topology persistence using KuzuDB

### Knowledge Engine
- [ ] **KNOW-01**: Recursive Markdown chunking of LLM responses
- [ ] **KNOW-02**: Local vector embeddings of text chunks via nomic-embed-text-v1.5
- [ ] **KNOW-03**: Context linking auto-suggest UI via `@` references
- [ ] **KNOW-04**: Vector retrieval auto-suggest UI via `\` commands

### Spatial Interface
- [ ] **UI-01**: 3D spatial visualization of the semantic graph via Three.js
- [ ] **UI-02**: 2D Glassmorphic Milkdown billboard overlay for chat interactions

## v2 Requirements (Deferred)
(None currently planned)

## Out of Scope
- External SaaS APIs or Cloud deployment — Must run entirely locally offline.
- Complex bundle build pipelines (e.g., Webpack/React) — Sticking to vanilla JS and simple Python Flask.

## Traceability
*(To be populated by roadmap)*
