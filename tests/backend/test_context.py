import os
import tempfile
import threading
import pytest
from app import DocumentGrouper
from db import get_db, get_connection, init_schema, insert_chunk_safely

def test_token_budget_tdd_ctx_01():
    """
    TDD-CTX-01: Force a 500-token semantic retrieval payload; 
    test MUST assert that the context grouper violently truncates 
    exactly at the 256-token limit boundary.
    """
    # Create a dummy chunk that is roughly 100 words (130 tokens)
    word_str = "word " * 100
    
    chunks = [
        {"id": "c1", "content": word_str, "doc_title": "Doc A"},
        {"id": "c2", "content": word_str, "doc_title": "Doc A"},
        {"id": "c3", "content": word_str, "doc_title": "Doc B"},
        {"id": "c4", "content": word_str, "doc_title": "Doc C"},
    ]
    
    # 4 chunks * 130 tokens = 520 tokens.
    doc_groups = DocumentGrouper.enforce_token_budget(chunks, limit=256)
    
    # Assert it truncated correctly
    # It should only include c1 (130 tokens) and c2 (which makes it 260... wait!)
    # Actually, current_tokens + tokens > 256. 
    # c1 (130). 130 + 130 = 260 > 256. So it should only include c1!
    
    # Let's count what we expect:
    assert "Doc A" in doc_groups
    assert len(doc_groups["Doc A"]) == 1
    assert "Doc B" not in doc_groups
    assert "Doc C" not in doc_groups

def test_pipeline_sequencer_tdd_kuz_02():
    """
    TDD-KUZ-02: Dispatch two asynchronous chunk-creation payloads simultaneously; 
    test MUST assert Kuzu successfully records both nodes without throwing a 
    write-lock or cursor concurrency error.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Override the path for this test
        db_file = os.path.join(tmpdirname, "kuzu.db")
        os.environ["KUZU_DB_PATH"] = db_file
        
        # Reset globals for testing isolation
        import db
        db._db = None
        db._conn = None
        
        # Initialize schema
        init_schema()
        
        # Thread function to insert
        def thread_worker(chunk_id, text):
            insert_chunk_safely(chunk_id, text)
            
        t1 = threading.Thread(target=thread_worker, args=("c1", "Text 1"))
        t2 = threading.Thread(target=thread_worker, args=("c2", "Text 2"))
        
        t1.start()
        t2.start()
        
        t1.join()
        t2.join()
        
        # Verify both exist
        conn = get_connection()
        result1 = conn.execute("MATCH (c:ChunkNode {id: 'c1'}) RETURN c.text").get_next()
        result2 = conn.execute("MATCH (c:ChunkNode {id: 'c2'}) RETURN c.text").get_next()
        
        assert result1[0] == "Text 1"
        assert result2[0] == "Text 2"
