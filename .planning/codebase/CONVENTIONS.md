# Conventions
*Last updated: 2026-06-27*

## Code Style
- **Python**: Standard PEP8 conventions. Extensive use of error boundary blocks (`try`/`except`) when interacting with local ML models and KuzuDB since native execution can crash the host server unexpectedly.
- **JavaScript**: Object-oriented encapsulation class patterns (`ProjectorApp`, `BillboardApp`) attached directly to the `window` namespace for global cross-communication (`window.app` and `window.billboardApp`).

## UI & CSS
- Variables are defined at the `:root` level representing the custom brutalist solid black theme in `main.css`.
- Flexbox is utilized extensively over grid or absolute positioning where possible for 2D UI elements.

## API Patterns
- Real-time endpoints (`/api/chat/stream`) utilize HTTP Server-Sent Events (SSE) `text/event-stream` for pushing partial chunk tokens to the browser.
- Graph data is exposed via REST GET methods (`/api/nodes`, `/api/details/<id>`) pulling direct JSON maps of the Kuzu graph state.
