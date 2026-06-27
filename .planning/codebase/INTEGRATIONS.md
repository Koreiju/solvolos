# Integrations
*Last updated: 2026-06-27*

## Internal Systems
- **Kuzu Graph Database**: Interacted with via local file-based storage `db/`. Nodes are structured as `GlobalNode` (chat sessions) and `ChunkNode` (recursive markdown elements).
- **GPT4All Model**: Loads a local `.gguf` model for offline text generation, simulating conversational endpoints via streaming SSE in `app.py`.
- **Nomic Embeddings**: Uses `nomic-embed-text-v1.5` locally for semantic retrieval matching, executed within the python process.

## External APIs
- Currently, this application runs entirely locally ("runs perfectly and only locally in a browser with a backend") with no external web APIs or SaaS integrations. Everything is offline-first.
