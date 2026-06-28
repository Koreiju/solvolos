# Structure
*Last updated: 2026-06-27*

## Directory Layout
- `milkdown_app/` - The core application codebase.
  - `app.py` - Primary Flask backend entry point, LLM inference, embedding pipelines, and KuzuDB ontology logic.
  - `ui/`
    - `templates/`
      - `index.html` - The single-page application markup and layout.
    - `static/`
      - `css/`
        - `main.css` - UI aesthetics, Brutalist black panels, Milkdown and Markdown CSS styling.
      - `js/`
        - `projector.js` - Three.js WebGL canvas scene, node rendering, and raycasting interactions.
        - `billboard.js` - 2D DOM logic, Marked text parsing, chat input events, auto-suggest popups, and SSE event handling.
- `legacy_wips/` - Historical implementations (tracker, tracker - Copy) used as reference material.

## Key Boundaries
- The barrier between 2D markdown text and 3D graph structures is bridged using `window.billboardApp` and `window.app` singleton scopes in JS. 
- Python runs the heavy ML pipelines inline with web requests. Production scaling would likely require decoupling `app.py` into worker queues, though the offline requirement makes monolithic sync patterns viable currently.
