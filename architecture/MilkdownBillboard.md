# Milkdown Billboard

This module manages the 2D brutalist UI (solid black, no rounding, no noisy close buttons/labels), prompt panel, and diffuse semantic rendering of AI responses over the existing document tree, implemented in `billboard.js` and `app.py`.

## Object Model

```mermaid
classDiagram
    class BillboardApp {
        +HTMLElement el
        +HTMLElement content
        +Editor editor
        +String documentText
        
        +initMilkdown()
        +debouncedSave()
        +fetchNodeData(id)
        
        +initInput()
        +handleSpecialChars(e)
        +fetchSuggestions(query, isRetrieval)
        +renderPopup(items, isRetrieval)
        +sendMessage()
    }
    note for BillboardApp "Positioning and drag state modeled in InteractionLayer.md"
    note for BillboardApp "Chat panel must adaptively grow on focus and collapse to exactly 3 lines on blur."
    note for BillboardApp "Hovering over search results MUST apply a 150ms debounce/abort controller to avoid DOM spam."
    note for BillboardApp "Font colors MUST continuously rotate derived from their UMAP HSV data arrays, even when locked to 2D."
    
    class Flask_chat_stream {
        +calculate_diffuse_layout(session_id)
        +yield_graph_update_sse()
    }
    
    BillboardApp --> Flask_chat_stream : /api/chat/stream POST
```

## Algorithmic Pseudocode (from `app.py`)

```python
# From app.py: chat_stream()
def calculate_diffuse_layout(all_session_chunks):
    # AI stream does not append linearly. 
    # We group by chunk_type and sort by similarity to the group centroid.
    
    type_groups = {}
    for sc in all_session_chunks:
        ctype = sc["type"]
        if ctype not in type_groups: type_groups[ctype] = []
        type_groups[ctype].append(sc)
        
    for ctype, items in type_groups.items():
        if not items: continue
        # 1. Calculate centroid for the semantic type
        centroid = np.mean([item["emb"] for item in items], axis=0)
        norm_centroid = np.linalg.norm(centroid)
        
        # 2. Score elements against centroid
        for item in items:
            norm_item = np.linalg.norm(item["emb"])
            item["score"] = np.dot(centroid, item["emb"]) / (norm_centroid * norm_item)
            
    # 3. Rebuild document text ordered by semantic hierarchy, not chronology
    type_order = ['heading', 'paragraph', 'list', 'code', 'table']
    sorted_types = sorted(type_groups.keys(), key=lambda k: type_order.index(k) if k in type_order else 99)
    
    diffuse_layout = {}
    diffused_parts = []
    
    for ctype in sorted_types:
        items = type_groups[ctype]
        items.sort(key=lambda x: x["score"], reverse=True)
        diffuse_layout[ctype] = [item["id"] for item in items]
        
        for item in items:
            diffused_parts.append(item["content"])
            
    diffused_content = "\n\n".join(diffused_parts)
    return diffused_content, diffuse_layout
```

## Function Design & TDD Assertions

```mermaid
sequenceDiagram
    participant Stream as chat_stream
    participant Grouper as DiffuseLayout
    participant UI as MilkdownEditor

    Stream->>Grouper: yield AI chunk AST
    Grouper->>Grouper: group by chunk_type
    Grouper->>Grouper: sort by centroid score
    
    note right of Grouper: TDD-DIF-01: If chunk_type unknown, sequence MUST safely append to bottom.<br/>Failing TDD asserts no parsing failure crash.
    
    Grouper->>UI: dispatch SSE text update
    UI->>UI: buffer fractured SSE tokens
    UI->>UI: render diffused text
    
    note right of UI: TDD-DIF-02: If an SSE chunk payload splits across network frames midway through a JSON token, UI MUST buffer it.<br/>Failing TDD asserts the naive JSON.parse crashes with SyntaxError.
```

## State Persistence: Diff-Sync Feedback Loop

```mermaid
sequenceDiagram
    participant User as MilkdownEditor
    participant App as BillboardApp
    participant API as /api/sync
    participant Graph as KuzuGraph

    User->>App: user types edit
    App->>App: debouncedSave()
    App->>App: extract AST diffs mapped to chunk IDs
    App->>API: POST diff payload
    API->>Graph: isomorphic update
    
    note right of API: TDD-ISO-01: Sync MUST pass explicit chunk ID for MERGE rather than bulk append.<br/>Failing TDD asserts Kuzu creates a duplicate chunk node.
    note right of User: TDD-ISO-02: Recursive subtree fields of the original markdown MUST remain strictly isomorphic as subtrees post-diff inline DOM update.<br/>Failing TDD asserts duplicates or diffeomorphisms exist between user/SLM inputs.
```
