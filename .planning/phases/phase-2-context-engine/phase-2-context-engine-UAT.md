# Phase 2 Context Engine UAT

## Backend TDD Constraints

- [ ] pending: **UAT-CTX-01**: Force a 500-token semantic retrieval payload; Context Grouper MUST strictly truncate at the 256-token limit boundary (Maps to `TDD-CTX-01` in `test_context_engine.py`).
- [ ] pending: **UAT-EMB-01**: Cast a random `(5, 768)` numpy array; Embedding pipeline MUST enforce UMAP parameter fallback checks (Maps to `TDD-EMB-01` in `test_embedding_pipeline.py`).
- [ ] pending: **UAT-KUZ-01**: Feed an explicit 2-dimensional `[0.1, 0.2]` array; KuzuDB MUST throw a schema dimension validation exception (Maps to `TDD-KUZ-01` in `test_kuzu_graph.py`).
- [ ] pending: **UAT-KUZ-02**: Dispatch two asynchronous chunk-creation payloads simultaneously; KuzuDB MUST successfully record both nodes via write-locks without throwing concurrency errors (Maps to `TDD-KUZ-02`).
