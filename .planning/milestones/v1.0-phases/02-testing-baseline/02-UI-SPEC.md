# Phase 2: UI-SPEC (Chat Interface & Vectors)

**Status:** Approved
**Mode:** mvp

<domain>
## Core Views

### 1. 2D Glassmorphic Billboard (`billboard.js`)
- Floating overlay on top of the Three.js canvas.
- Acts as the primary input mechanism for user queries.
- Parses and renders Markdown using `marked` + `DOMPurify` (Milkdown aesthetic).
- **Interactions:**
  - Standard text input.
  - '@' for linking existing GlobalNodes (Chat Context).
  - '\' for executing semantic searches against KuzuDB via Nomic embeddings.

### 2. SSE Stream Renderer
- Reads incoming tokens from the `/api/chat/stream` endpoint.
- Appends tokens dynamically to the current chat bubble in the DOM.
- Triggers a Three.js graph update when the final `graph_update` event arrives.
</domain>

<components>
## Component Tree

- `div#billboard-container` (Glassmorphic panel)
  - `div#chat-history` (Scrollable list of past messages)
    - `div.chat-message.user` (User messages)
    - `div.chat-message.ai` (AI responses, parsed markdown)
  - `div#input-area`
    - `textarea#chat-input`
    - `div#auto-suggest-popup` (Hidden by default, shown for `@` and `\`)
      - `ul.suggestion-list`
        - `li.suggestion-item`
</components>

<styling>
## Nord/Milkdown Aesthetic

- **Backgrounds:** `rgba(46, 52, 64, 0.8)` (Nord0) with `backdrop-filter: blur(10px)`.
- **Borders:** `1px solid rgba(216, 222, 233, 0.2)` (Nord4).
- **Text:** `rgb(236, 239, 244)` (Nord6) for primary text, `rgb(216, 222, 233)` (Nord4) for secondary.
- **Accents:** `rgb(136, 192, 208)` (Nord8) for highlights and active states (like auto-suggest).
- **Typography:** Inter or system sans-serif, clean padding, prominent line-height (1.6) for readability mimicking Milkdown editors.
</styling>

<decisions>
## Technical Decisions

- **Event Handling:** We will use the native `EventSource` API in vanilla JS to consume the SSE stream from Flask.
- **Parsing:** Incoming markdown chunks will be aggregated in memory and pushed through `marked.parse()` on a throttled interval (e.g., every 50ms) to update the DOM without causing excessive reflows.
- **Sanitization:** `DOMPurify.sanitize()` will wrap all `marked` outputs before setting `innerHTML`.
</decisions>
