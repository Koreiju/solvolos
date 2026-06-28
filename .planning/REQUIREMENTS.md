# Full Design Requirements

## v1.1: Verification of Milkdown, Chat, and Semantic Retrieval
- [ ] **VERIFY-01**: User can edit the Milkdown node and edits are correctly synchronized.
- [ ] **VERIFY-02**: User can send chats from the Milkdown panel.
- [ ] **VERIFY-03**: System correctly receives semantic recursive chunk diffuse updates.
- [ ] **VERIFY-04**: Semantic retrieval works correctly in the editable Milkdown panel.
- [ ] **VERIFY-05**: Semantic retrieval works correctly in the chat panel.

## v1.2: Token-Budgeted Context Engine
- **REQ-1.2.1 (Dual Intellisense Triggers)**: The prompt panel must support `@` for opening a mini-scrollable dropdown to explicitly hard-link specific chats/entities in the projector, and `\` for semantic vector searching. Selected queries render as uneditable visual badges (e.g., `🔮 violet text`).
- **REQ-1.2.2 (Semantic Chunk Ranking)**: Linked context queries (`\` or `@`) must trigger the backend to fetch associated chunks and sort them strictly by cosine similarity against the user's active prompt.
- **REQ-1.2.3 (Hard Token Budgets)**: The Context Engine must iterate down the ranked chunks and build the LLM injection payload, hard-stopping when a strict token limit (e.g., 256 tokens) is reached to prevent prompt bloat.
- **REQ-1.2.4 (Structural Lineage Injection)**: Selected chunks must be grouped by their parent documents, and injected into the LLM context hidden predicates alongside their preceding header/sub-header hierarchy to preserve structural meaning.

## v1.3: Diffuse Semantic Rendering
- **REQ-1.3.1 (Non-Chronological Mapping)**: AI response streams must NOT append linearly at the bottom of the Milkdown view. The chat history acts as a singular, unified document that evolves organically in-place.
- **REQ-1.3.2 (Interstitial Insertion)**: New AI-generated chunks must be inserted into the existing Milkdown DOM by finding the most semantically similar existing structure within identical containment types (e.g., putting new `# headers` next to similar old `# headers`).

## v2.0: Projective Physics & Visual Topologies
- **REQ-2.0.1 (UI Dimensions)**: Billboards must take up exactly 1/6th to 1/7th of the screen area, rendering exactly as the left-hand view in the Milkdown playground.
- **REQ-2.0.2 (Hover Target Scrolling)**: Hovering a 3D Chunk Node mounts the billboard in the distance and automatically scrolls the 2D view to center that exact chunk. Hovering a Global Node highlights its children without auto-scrolling.
- **REQ-2.0.3 (Fly-to-View Physics)**: Left-clicking a billboard persists it and animates the plane to a full-view projective distance directly in front of the camera, enabling 2D drag-and-drop.
- **REQ-2.0.4 (Unstick Mechanics)**: Right-clicking a persisted billboard breaks the fly-to-view tether, smoothly returning it to its 3D origin coordinates. A second right-click closes the billboard.
- **REQ-2.0.5 (Topological Graph Rendering)**: Global Session Nodes must render at 2x the scale of Chunk Nodes. Explicit graph edges (`REFERENCES`, `FOLLOWS`, `REPLIES_TO`, `PART_OF`) must be rendered as glowing cylinders connecting the nodes in the 3D space.

## v2.1: Feedback-Driven UX & Continuity
- **REQ-2.1.1 (Dynamic Continuity Physics)**: As nodes update dynamically via live streams or user edits, their 3D coordinates must smoothly interpolate via a normalization physics layer, ensuring continuity without partitioning or erratic jumping.
- **REQ-2.1.2 (Milkdown Playground Parity)**: The Milkdown editor must match the *exact* feature set of the milkdown playground, including full plugin support for math, diagrams, block menus, tooltips, and slash commands.
- **REQ-2.1.3 (Per-Token ProseMirror Streaming)**: SSE streams must parse tokens instantly and continuously dispatch transactions directly to the ProseMirror state, guaranteeing zero-latency live visual streams.
- **REQ-2.1.4 (Alien Grouping Affordances)**: The non-chronological, semantic grouping of chunks must include subtle visual affordances (e.g., structural tints or dynamic dividers) within the editor to make the "alien" structural organization visually intuitive.

## v2.2: Legacy Integration
- **REQ-2.2.1 (Legacy 3D Spatial Topology)**: Integrate the continuous rotation matrices, color shifting, 5x UMAP scaling, and background video features from the legacy tracker without breaking the current force-directed Milkdown physics.
