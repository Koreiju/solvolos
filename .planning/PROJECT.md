# Solvolos 3D Milkdown App

## What This Is

A local-only, backend-driven 3D web application integrating a Milkdown-inspired 2D glassmorphic UI with a 3D knowledge graph property network. It visualizes and retrieves LLM-generated semantic responses recursively mapped into chunked property nodes.

## Core Value

Visually and intuitively interact with locally-generated LLM context mapping and recursive semantic retrieval in a fully offline spatial environment.

## Requirements

### Validated

- ✓ Local LLM Chat generation with SSE streaming endpoints — existing
- ✓ Recursive Markdown chunking of LLM responses — existing
- ✓ Local vector embeddings of text chunks via nomic-embed-text-v1.5 — existing
- ✓ Graph topology persistence using KuzuDB — existing
- ✓ 3D spatial visualization of the semantic graph via Three.js — existing
- ✓ 2D Glassmorphic Milkdown billboard overlay for chat interactions — existing
- ✓ Context linking auto-suggest UI via `@` references — existing
- ✓ Vector retrieval auto-suggest UI via `\` commands — existing

### Active

(None currently - formalizing v1.0 prototype)

### Out of Scope

- External SaaS APIs or Cloud deployment — Must run entirely locally offline.
- Complex bundle build pipelines (e.g., Webpack/React) — Sticking to vanilla JS and simple Python Flask to ensure it remains lightweight and simple to run.

## Context

The project evolved from legacy trackers (`tracker` and `tracker - Copy`) which separated the chat interface and the 3D visualizer. We've merged these functionalities, centering everything in the 3D projector view and streamlining the interface into a single, cohesive spatial experience using a new unified KuzuDB schema to map the relationship between high-level chat sessions/messages and low-level semantic recursive markdown chunks.

## Constraints

- **Architecture**: Monolithic local server (Flask + Python ML pipelines) — Ensures ease of local setup.
- **Frontend**: Vanilla Javascript and CSS — Reduces build complexity and dependency footprint.
- **Storage**: KuzuDB file-based storage — Avoids needing a standalone database server.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Vanilla JS Marked.js styling | Replicating Milkdown aesthetics without pulling in heavy bundler requirements | ✓ Good |
| KuzuDB property graph | Native vector integrations in a graph topology fit the hierarchical nature of chunks to messages perfectly | ✓ Good |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-27 after initialization*
