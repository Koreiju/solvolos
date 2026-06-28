# Architectural Notes & Concepts Organization

## 1. Frontend Billboards (Milkdown integration)
- **Role**: Replaces the old static 2D HTML knowledge panels.
- **Features**:
  - Dynamically renders streaming markdown (instant quantized model outputs).
  - Size: 1/6th to 1/7th of the screen.
  - Scrollable.
  - Tied to 3D node positions, flies into view on click.
  - Draggable when stuck (clicked).
  - Hovering over a chunk node scrolls the billboard to that specific chunk.
  - Left-click locks/persists the billboard. Right-click unlocks/closes it.

## 2. Integrated Chat & Prompt Panel
- **Role**: Replaces the old chat sidebar.
- **Features**:
  - Fixed at the bottom of the Milkdown billboard.
  - Scrollable chat panel itself.
  - Context Linking (`@`): Opens a mini scrollable dropdown to explicitly link other chats/entities from the projector.
  - Retrieval Queries (`\`): Triggers a semantic search query against other entities/chunks. Returns ranked results in a popup.
  - Highlighted UI for retrieval tokens (e.g., violet text with a crystal ball emoji).

## 3. Ontology & Data Structure (KuzuDB)
- **Global Nodes**: Full Chat Sessions and Responses.
- **Recursive Chunk Nodes**: 
  - Markdown parsed into recursive trees (Headings, Subheadings, Bullet points, Table rows, Code artifacts).
  - Each chunk has its own embedding.
  - Global nodes aggregate the embeddings of their recursive chunks.
- **Graph Edges**:
  - `PART_OF` (Chunk -> Document/Message)
  - `PRECEDES`/`FOLLOWS` (Chunk -> Chunk context)
  - `REFERENCES` (Message -> Linked Context Node/Chunk)
  - `REPLIES_TO` (Message -> Message)

## 4. Context Window & Retrieval Logic
- **Hard Limit**: ~256 tokens for context links.
- **Logic**:
  - When prompt is sent, all referenced nodes (`@` links) undergo recursive chunking retrieval.
  - Perform unified retrieve-and-rank over these linked chunks.
  - Fill the context window up to the 256 token limit.
  - Hidden from the markdown view, passed as predicates to the LLM.
- **Visuals**: 
  - Global nodes are 2x the size of chunk nodes.
  - Highlighting a global node highlights all its chunk nodes.

## 5. Streaming & LLM Integration
- **Mechanism**: SSE (Server-Sent Events) from Python backend to frontend.
- **Local Model**: Using GPT4All or similar for local quantized inference.
- **Updates**: As chunks are generated (e.g. code blocks, paragraphs), their embeddings are dynamically updated, pushing new node data to the 3D projector in real-time.
