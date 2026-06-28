# Tech Stack
*Last updated: 2026-06-27*

## Languages & Frameworks
- **Python**: Backend server logic.
- **Flask**: Lightweight web framework for HTTP endpoints and SSE streams.
- **JavaScript (ES6+)**: Vanilla JS for frontend logic.
- **HTML/CSS**: Custom vanilla styling, specifically emphasizing a brutalist solid black, sharp-cornered aesthetic.
- **Markdown**: Parsed in frontend via `marked` and sanitized with `DOMPurify`.

## Data & AI
- **KuzuDB**: Property graph database acting as the vector and semantic backend storage for global nodes and chunk nodes.
- **GPT4All**: Local LLM execution for chat response generation.
- **Nomic Embed Text (v1.5)**: Local text embeddings.
- **UMAP**: Used for dimensionality reduction of vectors to map into 3D spatial and RGB color representations.

## Visualization
- **Three.js**: Used in the frontend to render the 3D property graph dynamically.
