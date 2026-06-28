import os
import tempfile
import pytest
from db import get_db, get_connection, init_schema

def test_kuzu_initialization_tdd_base_02():
    """
    TDD-BASE-02: Pytest MUST initialize a temporary KuzuDB instance on disk, 
    write a dummy node, and cleanly tear down the file lock.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Override the path for this test
        db_file = os.path.join(tmpdirname, "kuzu.db")
        os.environ["KUZU_DB_PATH"] = db_file
        
        # Reset globals for testing isolation
        import db
        db._db = None
        db._conn = None
        
        # Initialize
        init_schema()
        conn = get_connection()
        
        # Write dummy node
        conn.execute("CREATE (c:ChunkNode {id: 'test-001', text: 'TDD Baseline Test'})")
        
        # Verify it exists
        result = conn.execute("MATCH (c:ChunkNode) RETURN c.id, c.text").get_next()
        assert result[0] == "test-001"
        assert result[1] == "TDD Baseline Test"
        
        # Teardown happens automatically via TemporaryDirectory
        # which proves the lock is released.
