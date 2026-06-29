# Phase 2 Learnings

## Surprises
- Local embedding models (like GPT4All or Nomic python wrappers) are often not thread-safe. When typing in the UI, debounced search API calls can hit the backend concurrently with chat chunking embedding requests. This caused a C++ access violation `0x0000000000000000` because the underlying model state was overwritten concurrently.

## Decisions
- We introduced a simple `threading.Lock()` around the embedding call `embed.text()`. This ensures that even if multiple requests fire for embeddings simultaneously, they queue up safely without crashing the backend server.

## Patterns
- ESM Modules for Milkdown v7 require factory instantiation (e.g. `slashFactory()`) rather than direct plugin references.
- Browser Caching for ESM modules can be aggressive, requiring `?v=X` cache busting in `<script>` tags when iterating.
