# SEED-001: Recursive Semantic Milkdown Rendering

## Original SEED Alignment
Derived directly from the original `SEED.md` conceptual specification and extended by Phase 3 discussions.

## Concept
The scrollable markdown panel renders the chat history in a recursive-semantic chunk aggregation over structured markdown fields using semantic embeddings. We are building a billboarded version of the left-hand side from the Milkdown playground (https://milkdown.dev/playground) with a persistent prompt panel at the bottom.

## Architectural Shifts
- **Input Isolation**: We no longer show the user's prompt directly in the markdown panel.
- **Context Handling**: The LLM still sees a regular chat stream (user prompts + recursive context chunks), but the UI rendering diverges significantly from the raw LLM context.
- **Reference Changes**: `@` mention logic is entirely removed. We rely exclusively on `/` and `\` for semantic retrieval.

## Rendering Paradigm
- **Semantic Aggregation**: Instead of chronological rendering, the Milkdown UI renders a dynamic recursive tree structure.
- **Chunk Grouping**: For all selected semantic chunks within the user's prompt (which includes the original query as a markdown header), we group these in the same markdown rendering.
- **Lineage Containment**: We group our markdown renders over LLM responses in the same chat context such that the markdown tree structures between LLM responses are retained.
- **Embedding Similarity Order**: Containment and groupings of the tree structures aggregate per-recursive-chunk embedding similarity.
- **Diffuse Effect**: New markdown fields are inserted right between old markdown fields. The rendering order is organized by semantic similarity *within* each markdown element tree containment field type (`#`, `-`, `tables`, ```` `, `numerics`, etc.). This applies a "diffuse effect" to the same base markdown structure of semantic tree nodes, unified over the full history of LLM responses.

## UI Interactions
- **Milkdown Editor**: We use the actual Milkdown library to render an editable, Nord-themed, commonmark-compliant interface.
- **Projector Nodes**: The recursive tree chunks are the nodes in the 3D projector. Global vector embeddings (sessions) are nodes that are twice as large. Dynamic chunk streams cluster and unify with their base session node.
- **Retrieval Popups**: Typing `/` or `\` opens a mini-scrollable popup of ranked retrieval results. Clicking a result adds a 🔮 badge to the prompt panel.
- **Billboard Stickiness**: Hovering shows the panel. Left-clicking persists and allows dragging. Right-clicking closes it.
