import pytest

def test_isomorphic_chunk_sync():
    """
    TDD-ISO-01: Force a frontend update to an existing AST chunk; 
    test MUST assert Kuzu updates the node rather than creating a duplicate.
    """
    try:
        from milkdown_app.app import save_chunk_nodes, init_db, conn
        import os
        import tempfile
        import shutil
        
        # Test requires a temp DB
        test_dir = tempfile.mkdtemp()
        os.environ['KUZU_PATH'] = test_dir
        
        init_db() # Should build schema
        
        session_id = "session_test"
        
        # 1. Create initial global session node
        conn.execute("CREATE (g:GlobalNode {id: $id, type: 'session'})", {"id": session_id})
        
        # 2. Simulate initial backend generation
        save_chunk_nodes(session_id, "# Original Header\nOriginal Text")
        
        # Check initial chunk count
        result = conn.execute("MATCH (c:ChunkNode) RETURN count(c) as count")
        initial_count = result.get_next()[0]
        assert initial_count > 0, "Initial node was not created"
        
        # 3. Simulate continuous frontend feedback diff-sync
        # The frontend sends back the exact same ID, but with modified text
        # Because save_chunk_nodes currently uses CREATE, it will duplicate it.
        # When TDD-ISO-01 is implemented, it will use MERGE and the count will remain the same.
        
        # EXPECTED FAILURE: 
        # The naive implementation will append another chunk because it doesn't parse IDs for MERGE.
        
        save_chunk_nodes(session_id, "# Original Header\nEdited Text") # (Naive implementation lacks ID passing)
        
        result = conn.execute("MATCH (c:ChunkNode) RETURN count(c) as count")
        new_count = result.get_next()[0]
        
        assert new_count == initial_count, f"Isomorphism failed! Duplicate chunk created. {new_count} != {initial_count}"
        
        shutil.rmtree(test_dir)
        
    except ImportError:
        pytest.fail("Kuzu graph logic not fully extractable in milkdown_app.app yet")
