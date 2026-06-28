# Phase 11: Continuity Physics & Alien Affordances - Context

**Gathered:** 2026-06-27
**Status:** Ready for planning
**Mode:** Auto-generated (Autonomous Mode)

<domain>
## Phase Boundary

**Goal:** Implement 3D spatial normalization for dynamic coordinate updates and visual structural cues for semantic groups (REQ-2.1.1, REQ-2.1.4).
</domain>

<decisions>
## Implementation Decisions

### Agent Discretion
- **Bug Resolution**: The user noted that "the node view tracking and continuity is not normalized over dynamic updates to the same structure". This is because `/api/nodes/update` and `chat_stream` modify the textual content of a GlobalNode (and create new chunks) but either completely fail to update the 3D scene (in the case of manual milkdown editing), or fail to update the GlobalNode's own semantic coordinates (in the case of chat streaming). 
- **Alien Affordances**: To visually indicate that chunks belong to a semantic group, instead of spawning chunks rigidly at their target UMAP coordinates, `addStreamingNode` will be updated to spawn chunks *directly at the core of their parent GlobalNode*, allowing the Euler physics engine we built to physically "burst" them outward to their target coordinates.
- **Data Sync**: We will wire `/api/nodes/update` and `chat_stream` to properly emit the recalculated GlobalNode UMAP coordinates and newly generated Chunk IDs, and implement a `syncDynamicUpdates` method in `projector.js` to ingest them.
</decisions>
