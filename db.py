import os
import kuzu
import threading

_db = None
_conn = None

def get_db():
    global _db
    if _db is None:
        db_path = os.environ.get("KUZU_DB_PATH", "./local_db")
        _db = kuzu.Database(db_path)
    return _db

def get_connection():
    global _conn
    if _conn is None:
        _conn = kuzu.Connection(get_db())
    return _conn

def init_schema():
    conn = get_connection()
    try:
        conn.execute("CREATE NODE TABLE ChunkNode (id STRING, text STRING, embedding FLOAT[768], ux FLOAT, uy FLOAT, uz FLOAT, ur FLOAT, ug FLOAT, ub FLOAT, PRIMARY KEY (id))")
    except RuntimeError:
        pass
    try:
        conn.execute("CREATE NODE TABLE GlobalNode (id STRING, title STRING, embedding FLOAT[768], ux FLOAT, uy FLOAT, uz FLOAT, ur FLOAT, ug FLOAT, ub FLOAT, PRIMARY KEY (id))")
    except RuntimeError:
        pass
    try:
        conn.execute("CREATE REL TABLE PART_OF (FROM ChunkNode TO GlobalNode)")
    except RuntimeError:
        pass

class PipelineSequencer:
    _lock = threading.Lock()
    
    @classmethod
    def execute_write(cls, func, *args, **kwargs):
        with cls._lock:
            return func(*args, **kwargs)

def insert_chunk_safely(chunk_id, text):
    def _insert():
        import ml
        conn = get_connection()
        emb = ml.embed_text(text)
        coords, colors = ml.project_embedding(emb)
        
        # If it doesn't exist, we create it. If it exists, we SET. 
        # Kuzu MERGE syntax is a bit strict with list types, so we check first.
        try:
            conn.execute(
                "MERGE (c:ChunkNode {id: $id}) SET c.text = $text, c.embedding = $emb, c.ux = $ux, c.uy = $uy, c.uz = $uz, c.ur = $ur, c.ug = $ug, c.ub = $ub",
                {"id": chunk_id, "text": text, "emb": emb, "ux": coords[0], "uy": coords[1], "uz": coords[2], "ur": colors[0], "ug": colors[1], "ub": colors[2]}
            )
        except Exception as e:
            print("DB MERGE Error:", e)
    PipelineSequencer.execute_write(_insert)

def link_chunk_to_global(chunk_id, global_id):
    def _link():
        conn = get_connection()
        conn.execute("MERGE (g:GlobalNode {id: $g_id})", {"g_id": global_id})
        conn.execute("MERGE (c:ChunkNode {id: $c_id})", {"c_id": chunk_id})
        conn.execute(
            "MATCH (c:ChunkNode {id: $c_id}), (g:GlobalNode {id: $g_id}) "
            "MERGE (c)-[:PART_OF]->(g)",
            {"c_id": chunk_id, "g_id": global_id}
        )
    PipelineSequencer.execute_write(_link)

def get_subtree_details(global_id):
    conn = get_connection()
    result = conn.execute(
        "MATCH (c:ChunkNode)-[:PART_OF]->(g:GlobalNode {id: $g_id}) "
        "RETURN c.id, c.text",
        {"g_id": global_id}
    )
    children = []
    while result.has_next():
        row = result.get_next()
        children.append({"id": row[0], "text": row[1]})
    return {"global_id": global_id, "children": children}
