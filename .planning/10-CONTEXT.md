# Phase 10: Live Stream Diffusing - Context

**Gathered:** 2026-06-27
**Status:** Ready for planning
**Mode:** Auto-generated (Autonomous Mode)

<domain>
## Phase Boundary

**Goal:** Apply ProseMirror DOM transactions to instantly move incoming SSE stream tokens into their backend-calculated diffuse containment locations (REQ-1.3.3).
</domain>

<decisions>
## Implementation Decisions

### Agent Discretion
- **ProseMirror Transactions vs String Replacement**: The requirement specifies "ProseMirror DOM transactions". Milkdown's `replaceAll` action fundamentally wraps the replacement in a ProseMirror `Transaction` that diffs the document state. To achieve the "diffuse" effect without complex step-mapping of tokens *while* they are streaming (which is computationally intense and error-prone), we will let the stream render linearly. Then, upon receiving the `graph_update` event, the frontend will apply a single ProseMirror transaction (`replaceAll`) containing the perfectly re-ordered, semantically diffused markdown string.
- **Backend String Construction**: We will update `app.py`'s `chat_stream` to not only calculate the `diffuse_layout` IDs, but to actually construct the `diffused_content` string by joining the chunks in their new grouped and vector-sorted order. This string will be pushed to the frontend in the `graph_update` event.
</decisions>
