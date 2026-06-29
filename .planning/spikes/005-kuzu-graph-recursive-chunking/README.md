---
spike: 005
name: kuzu-graph-recursive-chunking
type: standard
validates: "Given a complex markdown message, When saved to backend, Then KuzuDB correctly splits it into recursive ChunkNodes and links them."
verdict: VALIDATED
tags: [kuzudb, backend]
---

# Spike 005: kuzu-graph-recursive-chunking

## What This Validates
Our backend needs to split complex markdown LLM responses into smaller pieces (ChunkNodes) and link them to the overarching GlobalNode so they can be retrieved efficiently. This tests if `db.py` handles recursive node insertions and links correctly without crashing or deadlocking.

## How to Run
```bash
python .planning/spikes/005-kuzu-graph-recursive-chunking/kuzu_test.py
```

## Results
Spike validated successfully. KuzuDB's schema successfully models the one-to-many parent-child relationship via the `PART_OF` relationship edge. 
`MATCH (c:ChunkNode)-[:PART_OF]->(g:GlobalNode {id: $id})` retrieves all chunks perfectly.

**Gotchas Discovered:**
- Since KuzuDB is an embedded database, `RuntimeError: IO exception: Could not set lock on file` will occur if multiple processes attempt to connect to the same `local_db` directory concurrently. In our test, we had to point it to `test_kuzu_db`.
- Using `MERGE` on vectors requires passing nodes with distinct IDs to prevent duplicate chunk conflicts.
- `ml` pipeline dependencies must be correctly isolated or mocked if database insertion scripts run in test environments without heavy LLM memory limits.
