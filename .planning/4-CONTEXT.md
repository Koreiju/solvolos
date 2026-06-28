# Phase 4: Semantic Ranker & Token Limiter - Context

**Gathered:** 2026-06-27
**Status:** Ready for planning
**Mode:** Auto-generated (Autonomous Mode)

<domain>
## Phase Boundary

**Goal:** Query target chunks, sort via vector similarity, and enforce the 256-token ceiling (REQ-1.2.2, REQ-1.2.3).
</domain>

<decisions>
## Implementation Decisions

### Agent Discretion
- **Entity Resolution**: The frontend `context_ids` payload can contain IDs for `ChunkNode`s (from `\` search) or `GlobalNode`s (from future `@` linking). The backend must gracefully resolve both: fetching the chunk directly, or fetching all child chunks of a referenced global node.
- **Ranking**: All resolved chunks will be scored via cosine similarity against the user's inbound message embedding.
- **Budgeting**: We will use a fast word-count heuristic (assuming 1.3 tokens per word) to enforce the strict 256-token ceiling, prioritizing the highest-ranked semantic chunks.
</decisions>
