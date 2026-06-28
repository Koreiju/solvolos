# Phase 7: Billboard Sizing & States - Context

**Gathered:** 2026-06-27
**Status:** Ready for planning
**Mode:** Auto-generated (Autonomous Mode)

<domain>
## Phase Boundary

**Goal:** Enforce 1/6th screen dimensions and implement hover-scrolling mechanics (REQ-2.0.1, REQ-2.0.2).
</domain>

<decisions>
## Implementation Decisions

### Agent Discretion
- **Billboard Sizing**: The billboard CSS will be updated to `width: 16.666vw` (1/6th screen width) to enforce the minimal, projective aesthetic without dominating the 3D space.
- **Hover-Scrolling**: When a user hovers over a `ChunkNode` in the 3D graph, the backend `/api/details` endpoint currently returns just the isolated chunk. We will modify this to instead return the parent `GlobalNode`'s full document content along with a `scroll_target` property containing the chunk's text. The frontend `billboard.js` will then load the full document and execute a DOM `TreeWalker` to smoothly scroll and highlight the target semantic chunk in the editor.
</decisions>
