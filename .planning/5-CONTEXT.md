# Phase 5: Lineage Injector - Context

**Gathered:** 2026-06-27
**Status:** Ready for planning
**Mode:** Auto-generated (Autonomous Mode)

<domain>
## Phase Boundary

**Goal:** Assemble the LLM hidden predicate payload grouped by document with preceding headers attached (REQ-1.2.4).
</domain>

<decisions>
## Implementation Decisions

### Agent Discretion
- **Header Tracking**: We will enhance `parse_markdown_to_chunks` in `app.py` to maintain a stack of markdown headers (H1-H6) as it parses the document top-to-bottom.
- **Database Schema**: We will dynamically patch KuzuDB's `ChunkNode` table to include a `lineage` string property (falling back gracefully if it already exists). This avoids expensive reverse-AST parsing on the fly.
- **Context Generation**: In `chat_stream`, the retrieved and ranked chunks will be grouped by their parent `GlobalNode` title. The payload injected into the prompt will prefix each chunk with its structural lineage, providing deep contextual meaning to the semantic snippets.
</decisions>
