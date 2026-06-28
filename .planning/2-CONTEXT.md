# Phase 2: Debounced Save & Re-embedding - Context

**Gathered:** 2026-06-27
**Status:** Ready for planning
**Mode:** Auto-generated (Autonomous Mode)

<domain>
## Phase Boundary

**Goal:** Wire Milkdown edit events to KuzuDB mutation endpoints, updating embeddings in real-time (REQ-1.1.2, REQ-1.1.3, REQ-1.1.4).
</domain>

<decisions>
## Implementation Decisions

### Agent Discretion
- **Frontend Sync**: Use `@milkdown/plugin-listener` to hook into markdown document updates. We will apply a debounce function (e.g., 1-2 seconds) to avoid spamming the backend during active typing.
- **Backend Sync Logic**: To prevent complex string diffing, the `/api/nodes/update` endpoint will take the full markdown state of a Global Node, delete its existing child `ChunkNode`s, re-parse the full document into new chunks using our new parser, embed them, and average their vectors to calculate the new Global Node embedding.
</decisions>
