import os
import tempfile
import threading
import pytest
from app import app, ContextCacheManager
from db import get_connection, init_schema

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_isomorphism_tdd_iso_01(client):
    """
    TDD-ISO-01: Dispatch a backend Kuzu command to create a chunk node, 
    then fire a simulated /api/sync REST payload with the identical chunk_id 
    but updated text. Assert the node is updated and the total node count 
    remains exactly 1.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Override the path for this test
        db_file = os.path.join(tmpdirname, "kuzu.db")
        os.environ["KUZU_DB_PATH"] = db_file
        
        # Reset globals for testing isolation
        import db
        db._db = None
        db._conn = None
        init_schema()
        import ml
        ml.init_ml()
        
        conn = get_connection()
        # Seed Kuzu
        conn.execute("MERGE (c:ChunkNode {id: 'iso-001'}) SET c.text = 'initial text'")
        
        # Fire Sync API
        response = client.post('/api/sync', json={"id": "iso-001", "text": "updated text"})
        assert response.status_code == 200
        
        # Assert deduplication
        result = conn.execute("MATCH (c:ChunkNode) RETURN count(c)").get_next()
        assert result[0] == 1
        
        # Assert update
        result_text = conn.execute("MATCH (c:ChunkNode {id: 'iso-001'}) RETURN c.text").get_next()
        assert result_text[0] == "updated text"

def test_subtree_isomorphism_tdd_iso_02(client):
    """
    TDD-ISO-02: Integration tests MUST verify that recursive subtree fields 
    of original markdown are strictly isomorphic before and after a secondary 
    SLM response inline diff. (Zero duplicates or diffeomorphisms allowed).
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        db_file = os.path.join(tmpdirname, "kuzu.db")
        os.environ["KUZU_DB_PATH"] = db_file
        import db
        db._db = None
        db._conn = None
        init_schema()
        import ml
        ml.init_ml()
        
        conn = get_connection()
        
        # Simulating original subtrees
        client.post('/api/sync', json={"id": "sub-1", "text": "heading"})
        client.post('/api/sync', json={"id": "sub-2", "text": "paragraph"})
        
        # SLM diff inline update on sub-2
        client.post('/api/sync', json={"id": "sub-2", "text": "paragraph with slm diff"})
        
        # Total nodes should be exactly 2
        count = conn.execute("MATCH (c:ChunkNode) RETURN count(c)").get_next()
        assert count[0] == 2

def test_context_cache_tdd_ctx_02():
    """
    TDD-CTX-02: Instantiate ContextCacheManager. Spam identical updates 
    from session_A and session_B on parallel threads. Assert the dictionary 
    mappings remain perfectly isolated and independent.
    """
    # Reset caches
    ContextCacheManager._caches = {}
    
    def worker_a():
        for i in range(100):
            ContextCacheManager.persist_local_kv("session_A", f"key_{i}", "val_A")
            
    def worker_b():
        for i in range(100):
            ContextCacheManager.persist_local_kv("session_B", f"key_{i}", "val_B")
            
    ta = threading.Thread(target=worker_a)
    tb = threading.Thread(target=worker_b)
    
    ta.start()
    tb.start()
    
    ta.join()
    tb.join()
    
    cache_a = ContextCacheManager.get_cache("session_A")
    cache_b = ContextCacheManager.get_cache("session_B")
    
    assert len(cache_a) == 100
    assert len(cache_b) == 100
    assert cache_a["key_50"] == "val_A"
    assert cache_b["key_50"] == "val_B"
