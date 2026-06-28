# Phase 2: Implementation Plan

**Goal:** Implement 2D Milkdown Chat UI and Flask/KuzuDB API endpoints to fulfill the failing test stubs.
**Status:** Ready for execution
**Mode:** mvp

<objective>
This plan maps the UI specifications from `02-UI-SPEC.md` and the existing failing test stubs into concrete implementation tasks. We will wire the Flask backend for KuzuDB and SSE streams, and build the 2D Glassmorphic overlay in Vanilla JS.
</objective>

---

### [Task 1] Initialize KuzuDB Schema
Configure the `app.py` script to create the necessary nodes (`GlobalNode`, `ChunkNode`) in KuzuDB if they don't already exist.
- **Files:** `milkdown_app/app.py`
- **Actions:** 
  - Add Cypher queries to `db.execute` during startup to `CREATE NODE TABLE IF NOT EXISTS ChunkNode (...)`.
  - Ensure vector dimensions match Nomic (`768`).

### [Task 2] Implement Semantic Search API
Implement the `POST /api/search` endpoint.
- **Files:** `milkdown_app/app.py`
- **Actions:** 
  - Extract query from JSON body.
  - Call Nomic embedding pipeline.
  - Execute KuzuDB vector search query.
  - Return JSON `{ "nodes": [...] }`.

### [Task 3] Implement SSE Chat Stream
Implement the `POST /api/chat/stream` endpoint.
- **Files:** `milkdown_app/app.py`
- **Actions:** 
  - Accept user message.
  - Setup a generator function that queries `GPT4All` and `yields` tokens in SSE format (`data: {"type": "token", "content": "..."}\n\n`).
  - On completion, chunk the full response, embed it, save to KuzuDB, and yield the final `graph_update`.

### [Task 4] Build Glassmorphic UI (HTML/CSS)
Set up the DOM structure and CSS variables based on `02-UI-SPEC.md`.
- **Files:** `milkdown_app/ui/templates/index.html`, `milkdown_app/ui/static/css/main.css`
- **Actions:** 
  - Create the `#billboard-container` markup.
  - Apply the Nord color palette and `backdrop-filter: blur(10px)`.

### [Task 5] Implement Frontend SSE Consumer
Implement the JavaScript logic to consume the SSE API.
- **Files:** `milkdown_app/ui/static/js/billboard.js`
- **Actions:** 
  - Add an event listener to `#chat-input`.
  - Use `fetch` to send the `POST /api/chat/stream` request, then parse the readable stream chunks.
  - Use `marked` and `DOMPurify` to update the DOM as tokens arrive.

### [Task 6] Turn Tests Green
Verify that the implementation passes the tests created earlier.
- **Files:** none (run tests)
- **Actions:** 
  - Run `pytest milkdown_app/tests/` and fix any discrepancies.
  - Run `npm test` and fix any missing mocks or contracts in JS.
