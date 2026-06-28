import os
import tempfile
import pytest
from app import app
from db import get_connection, init_schema, link_chunk_to_global

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_subtree_db_tdd_db_03():
    """
    TDD-DB-03: Instantiate a GlobalNode and three ChunkNodes. 
    Fire the linker function. Execute raw Cypher to MATCH (c)-[r:PART_OF]->(g) 
    and assert that count(r) strictly equals 3.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.environ["KUZU_DB_PATH"] = os.path.join(tmpdirname, "kuzu.db")
        import db
        db._db = None
        db._conn = None
        init_schema()
        
        # Link 3 chunks
        link_chunk_to_global("c1", "g1")
        link_chunk_to_global("c2", "g1")
        link_chunk_to_global("c3", "g1")
        
        conn = get_connection()
        result = conn.execute("MATCH (c)-[r:PART_OF]->(g:GlobalNode {id: 'g1'}) RETURN count(r)").get_next()
        assert result[0] == 3

def test_subtree_api_tdd_api_03(client):
    """
    TDD-API-03: Boot a Flask test client. Call GET /api/details/<global_id>. 
    Assert the returned JSON dictionary contains exactly 3 parsed children 
    in its body payload array.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.environ["KUZU_DB_PATH"] = os.path.join(tmpdirname, "kuzu.db")
        import db
        db._db = None
        db._conn = None
        init_schema()
        
        # Link 3 chunks to a new global
        link_chunk_to_global("c_a", "g2")
        link_chunk_to_global("c_b", "g2")
        link_chunk_to_global("c_c", "g2")
        
        response = client.get('/api/details/g2')
        assert response.status_code == 200
        
        data = response.json.get("data")
        assert data is not None
        assert data["global_id"] == "g2"
        assert len(data["children"]) == 3
        
        child_ids = [c["id"] for c in data["children"]]
        assert "c_a" in child_ids
        assert "c_b" in child_ids
        assert "c_c" in child_ids
