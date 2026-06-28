import pytest

def test_kuzu_schema_constraint():
    """
    TDD-KUZ-01: If a chunk embedding vector is empty or malformed, 
    sequence MUST abort node creation. Failing TDD asserts the database 
    throws schema constraint error.
    """
    try:
        from milkdown_app.app import save_chunk_nodes, init_db
        import os
        import tempfile
        import shutil
        
        # Test requires a temp DB to avoid polluting real state
        test_dir = tempfile.mkdtemp()
        os.environ['KUZU_PATH'] = test_dir
        
        init_db() # Should build schema
        
        # Pass a mock structure that bypasses the Nomic pipeline and directly feeds bad vectors
        # If the app doesn't validate, Kuzu should throw a strict schema exception.
        malformed_markdown = "# Bad \n Vector"
        
        # We will mock embed_texts inside save_chunk_nodes to return a 5-dimension vector instead of 768
        # using a monkeypatch in actual execution. For now we just call it and expect it handles it if we mock.
        
        with pytest.raises(Exception, match=r"constraint|schema|dimension"):
            # We assume save_chunk_nodes can accept an override or we test the raw cypher logic
            # This is a strict placeholder for the exact DB constraint test.
            # In TDD, we want the DB to reject a CREATE call where embedding size != 768.
            from milkdown_app.app import conn
            query = "CREATE (c:ChunkNode {id: 'bad', chunk_type: 'p', content: 'test', lineage: '', embedding: [0.1, 0.2], ux: 0, uy: 0, uz: 0, ur: 0, ug: 0, ub: 0})"
            conn.execute(query)
            
        shutil.rmtree(test_dir)
        
    except ImportError:
        pytest.fail("Kuzu graph logic not fully extractable in milkdown_app.app yet")
