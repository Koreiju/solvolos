import sys
import os

# Ensure solvolos root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Set mock DB path before importing db to avoid locking the main local_db
os.environ["KUZU_DB_PATH"] = "./test_kuzu_db"

from db import init_schema, get_connection, insert_chunk_safely, link_chunk_to_global, get_subtree_details
import ml

# Mock ML to avoid running heavy local models during this spike
def mock_embed(text):
    return [0.1] * 768

def mock_project(emb):
    return (0.0, 0.0, 0.0), (0.5, 0.5, 0.5)

ml.embed_text = mock_embed
ml.project_embedding = mock_project

def main():
    print("Testing KuzuDB Recursive Chunking...")
    
    # Initialize DB schema
    init_schema()
    
    complex_markdown = """# Solvolos Architecture
This is a test message.
## Section 1
Here is some complex text that should be chunked.
```python
print("Hello world")
```
## Section 2
More text for the chunks.
"""

    global_node_id = 'test_global_node_001'
    
    print("Saving global node...")
    try:
        conn = get_connection()
        conn.execute("MERGE (g:GlobalNode {id: $id})", {"id": global_node_id})
        
        print("Global node saved.")
        
        # Now chunk it (mocking chunk splits for the spike)
        chunks = [
            ("chunk_1", "# Solvolos Architecture\nThis is a test message."),
            ("chunk_2", "## Section 1\nHere is some complex text that should be chunked.\n```python\nprint(\"Hello world\")\n```"),
            ("chunk_3", "## Section 2\nMore text for the chunks.")
        ]
        
        for idx, (c_id, c_text) in enumerate(chunks):
            insert_chunk_safely(c_id, c_text)
            link_chunk_to_global(c_id, global_node_id)
            print(f"Saved chunk {c_id} and linked to {global_node_id}")
            
        print("\nQuerying DB to verify graph structure...")
        details = get_subtree_details(global_node_id)
        
        retrieved_chunks = details['children']
        for row in retrieved_chunks:
            print(f"Retrieved linked chunk: {row['id']}")
            
        assert len(retrieved_chunks) == 3, f"Expected 3 chunks, got {len(retrieved_chunks)}"
        print("\nSUCCESS: KuzuDB successfully linked and retrieved ChunkNodes!")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
