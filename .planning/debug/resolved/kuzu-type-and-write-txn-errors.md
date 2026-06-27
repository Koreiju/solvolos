---
status: resolved
trigger: "[System] Initializing Kuzu Database... RuntimeError: Cannot start a new write transaction in the system... Catalog exception: function TYPE does not exist"
created: 2026-06-27T17:58:00
updated: 2026-06-27T22:00:10
---

# Debug Session: kuzu-type-and-write-txn-errors

## Symptoms
1. **Expected behavior**: Creating an empty node should succeed and open the panel.
2. **Actual behavior**: Two separate crashes occurred: `GET /api/nodes` crashed with `function TYPE does not exist` and `POST /api/nodes/create` crashed with `Cannot start a new write transaction`.
3. **Timeline**: Previous builds did not throw this error; regression in the newest features modifying the database mapping.
4. **Reproduction**: Loading the main page and double-clicking to create an empty node.

## Resolution
- **root_cause**: 
  1. `type(r)` is Cypher syntax but Kuzu uses `LABEL(r)` for edge labels.
  2. Kuzu strictly limits databases to 1 concurrent write transaction. Concurrent Flask requests using multiple un-locked connections would conflict and crash on `CREATE` or `SET`.
- **fix**: 
  1. Replaced `type(r)` with `LABEL(r)` in `app.py`.
  2. Added a global `threading.Lock()` wrapped dynamically around `kuzu.Connection.execute` for all write-mutating queries (`CREATE`, `SET`, `DELETE`, `MERGE`, `DROP`, `ALTER`).
- **verification**: Ran `pytest` backend tests to ensure DB interaction remains functionally identical but now thread-safe.
- **files_changed**: `milkdown_app/app.py`
