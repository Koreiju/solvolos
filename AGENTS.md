<!-- GSD:project-start source:PROJECT.md -->

## Project

**Solvolos 3D Milkdown App**

A local-only, backend-driven 3D web application integrating a Milkdown-inspired 2D glassmorphic UI with a 3D knowledge graph property network. It visualizes and retrieves LLM-generated semantic responses recursively mapped into chunked property nodes.

**Core Value:** Visually and intuitively interact with locally-generated LLM context mapping and recursive semantic retrieval in a fully offline spatial environment.

### Constraints

- **Architecture**: Monolithic local server (Flask + Python ML pipelines) — Ensures ease of local setup.
- **Frontend**: Vanilla Javascript and CSS — Reduces build complexity and dependency footprint.
- **Storage**: KuzuDB file-based storage — Avoids needing a standalone database server.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->

## Technology Stack

## Languages & Frameworks

- **Python**: Backend server logic.
- **Flask**: Lightweight web framework for HTTP endpoints and SSE streams.
- **JavaScript (ES6+)**: Vanilla JS for frontend logic.
- **HTML/CSS**: Custom vanilla styling, specifically emphasizing a Nord/Milkdown glassmorphic aesthetic.
- **Markdown**: Parsed in frontend via `marked` and sanitized with `DOMPurify`.

## Data & AI

- **KuzuDB**: Property graph database acting as the vector and semantic backend storage for global nodes and chunk nodes.
- **GPT4All**: Local LLM execution for chat response generation.
- **Nomic Embed Text (v1.5)**: Local text embeddings.
- **UMAP**: Used for dimensionality reduction of vectors to map into 3D spatial and RGB color representations.

## Visualization

- **Three.js**: Used in the frontend to render the 3D property graph dynamically.

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

## Code Style

- **Python**: Standard PEP8 conventions. Extensive use of error boundary blocks (`try`/`except`) when interacting with local ML models and KuzuDB since native execution can crash the host server unexpectedly.
- **JavaScript**: Object-oriented encapsulation class patterns (`ProjectorApp`, `BillboardApp`) attached directly to the `window` namespace for global cross-communication (`window.app` and `window.billboardApp`).

## UI & CSS

- Variables are defined at the `:root` level representing the custom Nord/Glassmorphism theme in `main.css`.
- Flexbox is utilized extensively over grid or absolute positioning where possible for 2D UI elements.

## API Patterns

- Real-time endpoints (`/api/chat/stream`) utilize HTTP Server-Sent Events (SSE) `text/event-stream` for pushing partial chunk tokens to the browser.
- Graph data is exposed via REST GET methods (`/api/nodes`, `/api/details/<id>`) pulling direct JSON maps of the Kuzu graph state.

<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

## Core Patterns

- **Backend-Driven 3D UI**: The Flask backend constructs the graph (nodes, edges) and streams AI content while calculating semantic coordinates. The frontend is primarily a dumb renderer of these states, updating Three.js visually based on API pulls and SSE streams.
- **Hierarchical Knowledge Graph**: Top-level `GlobalNode`s represent chat messages. Each message is split into recursive components, embedded, and mapped to `ChunkNode`s which point back to their parent.
- **Glassmorphism Overlay**: A 2D "Milkdown" inspired billboard overlay is rendered independently from the WebGL canvas, linked temporally to the 3D space by tracking node coordinates on screen.

## Data Flow

<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.agents/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
