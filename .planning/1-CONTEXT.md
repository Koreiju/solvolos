# Phase 1: Recursive Markdown Parsing - Context

**Gathered:** 2026-06-27
**Status:** Ready for planning
**Mode:** Auto-generated (Autonomous Mode)

<domain>
## Phase Boundary

**Goal:** Perfect KuzuDB chunking logic to protect code blocks, tables, and nested structures.
</domain>

<decisions>
## Implementation Decisions

### Agent Discretion
All implementation choices are at the agent's discretion. The current `parse_markdown_to_chunks` in `app.py` simply splits by `\n\n+`, which corrupts code blocks containing blank lines and destroys table structures. We will implement a robust AST-based or state-machine-based parser in Python to safely isolate these structures as distinct `ChunkNode`s.
</decisions>
