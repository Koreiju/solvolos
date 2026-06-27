# Architecture
*Last updated: 2026-06-27*

## Core Patterns
- **Backend-Driven 3D UI**: The Flask backend constructs the graph (nodes, edges) and streams AI content while calculating semantic coordinates. The frontend is primarily a dumb renderer of these states, updating Three.js visually based on API pulls and SSE streams.
- **Hierarchical Knowledge Graph**: Top-level `GlobalNode`s represent chat messages. Each message is split into recursive components, embedded, and mapped to `ChunkNode`s which point back to their parent.
- **Glassmorphism Overlay**: A 2D "Milkdown" inspired billboard overlay is rendered independently from the WebGL canvas, linked temporally to the 3D space by tracking node coordinates on screen.

## Data Flow
1. **User Input**: The user sends a query from the 2D billboard.
2. **Context Assembly**: `@` references directly link GlobalNodes. `\` semantic searches execute a Nomic vector search over KuzuDB to append ChunkNodes to the prompt window.
3. **LLM Generation**: GPT4All generates tokens asynchronously. 
4. **SSE Stream**: Tokens are piped to the frontend to update the DOM in real-time.
5. **Post-Processing**: Upon stream completion, the backend regex-chunks the output, generates embeddings, applies UMAP, pushes to KuzuDB, and streams back the final graph nodes to be rendered in the Three.js scene.
