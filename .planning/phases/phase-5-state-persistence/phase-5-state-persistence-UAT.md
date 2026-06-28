# Phase 5 State Persistence UAT

## Architecture Constraints

- [ ] pending: **UAT-ISO-01**: Force a frontend AST diff payload targeting an existing chunk ID; backend MUST process a `MERGE` query to update the node rather than duplicating it (Maps to `TDD-ISO-01` in `test_isomorphism_sync.py`).
- [ ] pending: **UAT-ISO-02**: Integration tests MUST verify that recursive subtree fields of original markdown are strictly isomorphic before and after a secondary SLM response inline diff (Maps to `TDD-ISO-02`).
- [ ] pending: **UAT-CTX-02**: Dispatch queries from two separate session IDs in parallel; ContextCacheManager MUST securely route and isolate the local SLM cache states without contamination (Maps to `TDD-CTX-02` in `test_multi_agent_cache.py`).
