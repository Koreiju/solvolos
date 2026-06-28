# Phase 6: Semantic DOM Diffing - Context

**Gathered:** 2026-06-27
**Status:** Ready for planning
**Mode:** Auto-generated (Autonomous Mode)

<domain>
## Phase Boundary

**Goal:** Calculate target DOM insertion indices for incoming SSE stream chunks based on embedding similarity within containment types (REQ-1.3.1, REQ-1.3.2).
</domain>

<decisions>
## Implementation Decisions

### Agent Discretion
- **Diffuse Effect Architecture**: As defined in SEED-001, new markdown chunks are not appended chronologically to the end of the document. Instead, they are inserted among *existing* chunks of the same structural type (`paragraph`, `list`, `heading`, etc.) based on vector similarity.
- **Backend vs Frontend**: The frontend handles the visual display, but the backend is responsible for vector math. At the end of the AI's generation, when the backend evaluates the new chunks, it will query the database for *all previous chunks in the session* grouped by type, calculate where the new chunk sits semantically within its type-group (sorted by embedding similarity), and return a specific `insertion_index` and `insert_before_id` for the frontend.
</decisions>
