# Architecture Concepts & Notes

Based on the updated SEED conceptual specification, here is a comprehensive organization of the core concepts for the new app design. This document outlines the granular behaviors and features expected of the system.

## 1. 3D Projector GUI (Three.js Layer)
The 3D space is the primary interface, replacing traditional 2D sidebars. 
- **Global vs. Chunk Nodes**: The projector visualizes both Global Document nodes (representing full chats/documents) and Recursive Chunk nodes. Global nodes are rendered twice as large as chunk nodes.
- **Knowledge Graph Links**: Visual connections in the 3D space are rendered as glowing cylinders. These specifically represent semantic and contextual knowledge graph links between nodes.
- **Highlighting Logic**: Highlighting a Global Document node automatically highlights all of its constituent Recursive Chunk nodes.

## 2. Interaction Mechanics (Hover, Fly-to-View, Persist)
Interacting with the 3D nodes triggers the display of 2D Milkdown Billboards.
- **Hovering a Chunk Node**: Opens the full chat's Milkdown billboard, but initializes the scroll position to centrally display the specific chunk that is being hovered. This allows users to "feel out" the semantic space intuitively.
- **Hovering a Global Node**: Opens the Milkdown billboard with non-selective scrolling (e.g., at the top or bottom of the document).
- **Clicking & Persisting (Fly-to-View)**: When a user left-clicks an opened billboard, it is persisted and "flown to view" centrally, acting under a projective distance metric. Once stuck, the billboard is completely draggable.
- **Breaking the Link**: Right-clicking on the panel unsticks the invisible fly-to-view-and-focus link. The billboard returns to the distance, anchored to its 3D node coordinates.
- **Closing**: Right-clicking closes the chat billboard, returning the system to the default show-when-hovered state (left-clicking does not close it, but opens/persists it).

## 3. Milkdown Billboards & Prompt Panel
- **Milkdown Rendering**: The UI panels are strictly Milkdown billboards and must look *exactly* as the left-hand rendered view in the Milkdown playground, supporting dynamic, high-quality markdown rendering.
- **Dimensions**: Billboards take up approximately 1/6th to 1/7th of the screen area.
- **Prompt Panel**: Persists at the bottom of the billboard, independent of the scrolling markdown response above it.
- **Intellisense Hooks (`@` and `/`)**:
  - `@`: Opens a mini-scrollable dropdown to manually link other files or specific chats in the projector.
  - `/`: Triggers a semantic vector search. The query string following the slash is vectored and matched. Selected results are injected into the prompt, denoted by a visual badge (e.g., `🔮 violet text`).

## 4. Semantic Search & Context Assembly
The application employs strict, chunk-based context controls rather than sending full documents to the LLM.
- **Global Document Vector Search**: When `/` is used, a full semantic search runs the query vector against the global document vectors first, then retrieves the highly relevant recursive chunks.
- **Rank-and-Render (Token Limited)**:
  - Ranked chunks are accumulated until the hard context window limit (~256 tokens) is satisfied.
  - Chunks are not rendered randomly; they are grouped by their parent documents. This ensures sections from each document are clearly and cohesively represented in the context prompt.
  - **Heading Tracking**: When rendering a chunk into context, the system tracks and includes its preceding headings and subheadings, preserving the structural meaning of the chunk.
- **Hidden Predicates**: The injected context is formatted as inline predicates for the LLM prompt but remains hidden in the user's markdown GUI, as the links are already visually represented in the 3D space.

## 5. Ontology & Database Layer (Kuzu Graph-Vector DB)
- **Recursive Markdown Structures**: The backend parses markdown into recursive trees based on specific structural definitions (headings, subheadings, bullet points, numbers, table rows, and triple-backtick code blocks).
- **Dual-Level Embeddings**:
  - **Recursive Embeddings**: Applied to individual chunks. Dynamically updated when fields are mutated.
  - **Global Embeddings**: Aggregated from the recursive chunks to represent the entire chat/response node.
- **Storage Strategy**: Original prompts and responses are stored with direct links to their dual-level embeddings. The progression of markdown chats is tracked with full links over chat history while native chunks maintain their graph links for projection back into the GUI.
