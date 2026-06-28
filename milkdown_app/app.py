import os
import json
import sys
import traceback
import uuid
import re
import numpy as np
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import kuzu
from nomic import embed
import umap
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import joblib
from gpt4all import GPT4All
from datetime import datetime
import threading

db_write_lock = threading.Lock()
_orig_execute = kuzu.Connection.execute

def _safe_execute(self, query, parameters=None):
    if isinstance(query, str):
        q_upper = query.upper()
        if any(kw in q_upper for kw in ['CREATE ', 'SET ', 'DELETE ', 'MERGE ', 'DROP ', 'ALTER ']):
            with db_write_lock:
                if parameters: return _orig_execute(self, query, parameters)
                return _orig_execute(self, query)
    if parameters: return _orig_execute(self, query, parameters)
    return _orig_execute(self, query)

kuzu.Connection.execute = _safe_execute

app = Flask(__name__, template_folder='ui/templates', static_folder='ui/static')

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_ROOT, 'chat_db.kuzu')
UMAP_MODEL_PATH = os.path.join(APP_ROOT, 'umap_reducer.joblib')
SCALER_MODEL_PATH = os.path.join(APP_ROOT, 'scaler.joblib')
NOMIC_API_KEY = os.environ.get("NOMIC_API_KEY", "") 

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

llm = None
umap_reducer = None
scaler = None

# We store a reference to the active sessions in memory, but could rely solely on Kuzu
CHAT_SESSIONS = {}

print(f"[System] Initializing Kuzu Database at {DB_PATH}")
try:
    db = kuzu.Database(DB_PATH)
    print("[System] Database initialized successfully")
except Exception as e:
    print(f"[FATAL] Failed to initialize database: {e}")
    traceback.print_exc()
    sys.exit(1)

def get_conn():
    return kuzu.Connection(db)

def init_llm():
    global llm
    model_name = "Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf"
    print(f"[System] Initializing GPT4All Model: {model_name}")
    model_path = os.path.join(APP_ROOT, model_name)
    try:
        if os.path.exists(model_path):
            llm = GPT4All(model_path, device="cuda", n_threads=4, ngl=100, verbose=False)
        else:
            llm = GPT4All(model_name, device="cuda", n_threads=4, ngl=100, verbose=False)
        print("[System] LLM Initialized successfully.")
    except Exception as e:
        print(f"[WARN] Failed to init LLM on CUDA: {e}. Falling back to CPU/Default.")
        try:
            llm = GPT4All(model_name, device="cpu")
        except Exception as e2:
            print(f"[ERROR] LLM Initialization failed completely: {e2}")

def init_db():
    global umap_reducer, scaler
    conn = get_conn()
    try:
        conn.execute("INSTALL vector; LOAD vector;")
    except: pass

    if os.path.exists(UMAP_MODEL_PATH) and os.path.exists(SCALER_MODEL_PATH):
        try:
            umap_reducer = joblib.load(UMAP_MODEL_PATH)
            scaler = joblib.load(SCALER_MODEL_PATH)
        except Exception as e:
            print(f"[WARN] Failed to load ML models: {e}")
    else:
        # Initialize a basic umap and scaler for cold starts
        umap_reducer = umap.UMAP(n_components=6, n_neighbors=15, min_dist=0.1, metric='cosine')
        scaler = StandardScaler()
        # Create a dummy fit so we can use transform immediately
        dummy_data = np.random.rand(20, 768)
        scaler.fit(dummy_data)
        umap_reducer.fit(scaler.transform(dummy_data))
        joblib.dump(scaler, SCALER_MODEL_PATH)
        joblib.dump(umap_reducer, UMAP_MODEL_PATH)

    try:
        conn.execute("ALTER TABLE ChunkNode ADD lineage STRING DEFAULT ''")
    except: pass

    try:
        res = conn.execute("MATCH (n:GlobalNode) RETURN count(n)")
        count = res.get_next()[0] if res.has_next() else 0
        print(f"[DEBUG] DB already initialized with {count} GlobalNodes.")
    except Exception as e:
        print(f"[DEBUG] DB schema not found. Creating schema...")
        try:
            conn.execute("CREATE NODE TABLE GlobalNode(id STRING, type STRING, title STRING, role STRING, content STRING, created_at STRING, embedding FLOAT[768], ux FLOAT, uy FLOAT, uz FLOAT, ur FLOAT, ug FLOAT, ub FLOAT, PRIMARY KEY (id))")
            conn.execute("CREATE NODE TABLE ChunkNode(id STRING, chunk_type STRING, content STRING, lineage STRING, embedding FLOAT[768], ux FLOAT, uy FLOAT, uz FLOAT, ur FLOAT, ug FLOAT, ub FLOAT, PRIMARY KEY (id))")
            conn.execute("CREATE REL TABLE IN_SESSION(FROM GlobalNode TO GlobalNode)") # Message -> ChatSession
            conn.execute("CREATE REL TABLE PART_OF(FROM ChunkNode TO GlobalNode)") # Chunk -> Message
            conn.execute("CREATE REL TABLE REFERENCES(FROM GlobalNode TO GlobalNode)") # Message -> GlobalNode
            conn.execute("CREATE REL TABLE RETRIEVES(FROM GlobalNode TO ChunkNode)") # Message -> ChunkNode
            print("[DEBUG] Schema created successfully.")
        except Exception as ce:
            print(f"[CRITICAL] Error creating schema: {ce}")
        count = 0

    if count == 0:
        print("[DEBUG] DB is empty. Creating default empty node...")
        empty_id = f"node_{uuid.uuid4().hex[:8]}"
        emb = embed_texts(["Empty Node"])[0]
        c_c, _ = project_embeddings(np.array([emb]))
        ux, uy, uz = (float(c_c[0][0]), float(c_c[0][1]), float(c_c[0][2])) if len(c_c) > 0 else (0.0, 0.0, 0.0)
        params = {
            "id": empty_id, "type": "empty", "title": "New Node", "role": "system", "content": "", 
            "created_at": datetime.now().isoformat(), "emb": emb.tolist(),
            "ux": ux, "uy": uy, "uz": uz,
            "ur": 0.5, "ug": 0.5, "ub": 0.5
        }
        conn.execute("CREATE (s:GlobalNode {id: $id, type: $type, title: $title, role: $role, content: $content, created_at: $created_at, embedding: $emb, ux: $ux, uy: $uy, uz: $uz, ur: $ur, ug: $ug, ub: $ub})", params)

def parse_markdown_to_chunks(md_text):
    chunks = []
    lines = md_text.split('\n')
    
    current_chunk_type = None
    current_lines = []
    header_stack = {}
    
    def get_line_type(text):
        if re.match(r'^(#{1,6})\s', text): return 'heading'
        if text.startswith('- ') or text.startswith('* ') or re.match(r'^\d+\.\s', text): return 'list'
        if '|' in text and '-' in text: return 'table'
        return 'paragraph'
    
    def get_lineage():
        if not header_stack: return ""
        return "\n".join(header_stack[lvl] for lvl in sorted(header_stack.keys()))
    
    def push_chunk():
        nonlocal current_chunk_type, current_lines
        if current_lines:
            content = '\n'.join(current_lines).strip()
            if content:
                if not current_chunk_type:
                    current_chunk_type = get_line_type(content)
                
                lineage = get_lineage()
                
                if current_chunk_type == 'heading':
                    match = re.match(r'^(#{1,6})\s', content)
                    if match:
                        lvl = len(match.group(1))
                        header_stack[lvl] = content
                        for k in list(header_stack.keys()):
                            if k > lvl: del header_stack[k]
                            
                chunks.append({"type": current_chunk_type, "content": content, "lineage": lineage})
            
            current_lines = []
            current_chunk_type = None

    in_code_block = False
    
    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('```'):
            if in_code_block:
                current_lines.append(line)
                current_chunk_type = 'code'
                push_chunk()
                in_code_block = False
            else:
                push_chunk()
                in_code_block = True
                current_lines.append(line)
            continue
            
        if in_code_block:
            current_lines.append(line)
            continue
            
        if not stripped:
            push_chunk()
            continue
            
        line_type = get_line_type(stripped)
        
        if current_lines:
            if not current_chunk_type:
                current_chunk_type = get_line_type(current_lines[0].strip())
            
            if line_type == 'heading' or current_chunk_type == 'heading' or line_type != current_chunk_type:
                push_chunk()
                
        current_chunk_type = line_type
        current_lines.append(line)
        
    push_chunk()
    return chunks

embed_lock = threading.Lock()

def embed_texts(texts):
    if not texts: return []
    try:
        with embed_lock:
            res = embed.text(texts=texts, model='nomic-embed-text-v1.5', task_type='search_document', inference_mode="local", device="cpu")
        return np.array(res['embeddings'])
    except Exception as e:
        print(f"[ERROR] Embedding failed: {e}")
        return np.random.rand(len(texts), 768)

def project_embeddings(embeddings):
    if len(embeddings) == 0: return [], []
    emb_scaled = scaler.transform(embeddings)
    proj = umap_reducer.transform(emb_scaled)
    coords = proj[:, 0:3]
    colors_raw = proj[:, 3:6]
    color_scaler = MinMaxScaler(feature_range=(0, 1))
    colors = color_scaler.fit_transform(colors_raw)
    return coords, colors

def safe_float(val):
    try:
        f = float(val)
        return 0.0 if np.isnan(f) else f
    except: return 0.0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/nodes', methods=['GET'])
def get_nodes():
    conn = get_conn()
    nodes = []
    edges = []
    
    # Global nodes
    res_global = conn.execute("MATCH (n:GlobalNode) RETURN n.id, n.type, n.title, n.role, n.ux, n.uy, n.uz, n.ur, n.ug, n.ub")
    while res_global.has_next():
        row = res_global.get_next()
        nodes.append({
            "id": row[0], "node_type": "global", "type": row[1], "title": row[2], "role": row[3],
            "x": safe_float(row[4]), "y": safe_float(row[5]), "z": safe_float(row[6]),
            "r": safe_float(row[7]), "g": safe_float(row[8]), "b": safe_float(row[9]),
            "size": 2.0
        })

    # Chunk nodes
    res_chunk = conn.execute("MATCH (n:ChunkNode) RETURN n.id, n.chunk_type, n.ux, n.uy, n.uz, n.ur, n.ug, n.ub")
    while res_chunk.has_next():
        row = res_chunk.get_next()
        nodes.append({
            "id": row[0], "node_type": "chunk", "type": row[1], 
            "x": safe_float(row[2]), "y": safe_float(row[3]), "z": safe_float(row[4]),
            "r": safe_float(row[5]), "g": safe_float(row[6]), "b": safe_float(row[7]),
            "size": 1.0
        })
        
    # Edges
    res_edges = conn.execute("MATCH (c:ChunkNode)-[:PART_OF]->(m:GlobalNode) RETURN c.id, m.id")
    while res_edges.has_next():
        row = res_edges.get_next()
        edges.append({"source": row[0], "target": row[1], "type": "PART_OF"})
        
    res_ref = conn.execute("MATCH (m1:GlobalNode)-[r]->(m2:GlobalNode) WHERE LABEL(r) IN ['REFERENCES', 'FOLLOWS', 'REPLIES_TO'] RETURN m1.id, m2.id, LABEL(r)")
    while res_ref.has_next():
        row = res_ref.get_next()
        edges.append({"source": row[0], "target": row[1], "type": row[2]})

    return jsonify({"nodes": nodes, "edges": edges})

@app.route('/api/details/<node_id>', methods=['GET'])
def get_details(node_id):
    conn = get_conn()
    # Check Global
    res = conn.execute(f"MATCH (n:GlobalNode) WHERE n.id = '{node_id}' RETURN n.id, n.type, n.title, n.role, n.content")
    if res.has_next():
        row = res.get_next()
        return jsonify({"id": row[0], "node_type": "global", "type": row[1], "title": row[2], "role": row[3], "content": row[4]})
    
    # Check Chunk -> Return Parent GlobalNode with scroll_target
    res = conn.execute(f"MATCH (n:ChunkNode)-[:PART_OF]->(g:GlobalNode) WHERE n.id = '{node_id}' RETURN g.id, g.title, g.content, n.content")
    if res.has_next():
        row = res.get_next()
        return jsonify({"id": row[0], "node_type": "global", "title": row[1], "content": row[2], "scroll_target": row[3]})
        
    return jsonify({"error": "Not found"}), 404

@app.route('/api/nodes/create', methods=['POST'])
def create_node():
    data = request.json or {}
    ux = data.get('x', 0.0)
    uy = data.get('y', 0.0)
    uz = data.get('z', 0.0)
    
    empty_id = f"node_{uuid.uuid4().hex[:8]}"
    emb = embed_texts(["Empty Node"])[0]
    
    conn = get_conn()
    params = {
        "id": empty_id, "type": "empty", "title": "New Node", "role": "system", "content": "", 
        "created_at": datetime.now().isoformat(), "emb": emb.tolist(),
        "ux": float(ux), "uy": float(uy), "uz": float(uz),
        "ur": 0.5, "ug": 0.5, "ub": 0.5
    }
    conn.execute("CREATE (s:GlobalNode {id: $id, type: $type, title: $title, role: $role, content: $content, created_at: $created_at, embedding: $emb, ux: $ux, uy: $uy, uz: $uz, ur: $ur, ug: $ug, ub: $ub})", params)
    
    return jsonify({
        "id": empty_id, "node_type": "global", "type": "empty", "title": "New Node", "role": "system",
        "x": float(ux), "y": float(uy), "z": float(uz),
        "r": 0.5, "g": 0.5, "b": 0.5,
        "size": 2.0
    })

@app.route('/api/nodes/update', methods=['POST'])
def update_node():
    data = request.json or {}
    node_id = data.get('node_id')
    content = data.get('content', '')
    
    if not node_id: return jsonify({"error": "Missing node_id"}), 400
    
    conn = get_conn()
    conn.execute(f"MATCH (n:GlobalNode) WHERE n.id = '{node_id}' SET n.content = $content", {"content": content})
    conn.execute(f"MATCH (c:ChunkNode)-[r:PART_OF]->(g:GlobalNode) WHERE g.id = '{node_id}' DETACH DELETE c")
    
    chunks = parse_markdown_to_chunks(content)
    if not chunks:
        return jsonify({"success": True, "chunks": []})
        
    texts = [c['content'] for c in chunks]
    embs = embed_texts(texts)
    
    sum_emb = np.zeros(768)
    chunks_data = []
    for i, c in enumerate(chunks):
        c_id = f"chunk_{uuid.uuid4().hex[:8]}"
        c_emb = embs[i]
        sum_emb += c_emb
        
        c_coords, c_colors = project_embeddings(np.array([c_emb]))
        c_ux, c_uy, c_uz = (float(c_coords[0][0]), float(c_coords[0][1]), float(c_coords[0][2])) if len(c_coords) > 0 else (0.0, 0.0, 0.0)
        c_ur, c_ug, c_ub = (float(c_colors[0][0]), float(c_colors[0][1]), float(c_colors[0][2])) if len(c_colors) > 0 else (0.5, 0.5, 0.5)
        
        params = {
            "id": c_id, "type": c["type"], "content": c["content"], "lineage": c.get("lineage", ""), "emb": c_emb.tolist(),
            "ux": c_ux, "uy": c_uy, "uz": c_uz,
            "ur": c_ur, "ug": c_ug, "ub": c_ub
        }
        conn.execute("CREATE (c:ChunkNode {id: $id, chunk_type: $type, content: $content, lineage: $lineage, embedding: $emb, ux: $ux, uy: $uy, uz: $uz, ur: $ur, ug: $ug, ub: $ub})", params)
        conn.execute(f"MATCH (c:ChunkNode), (g:GlobalNode) WHERE c.id = '{c_id}' AND g.id = '{node_id}' CREATE (c)-[:PART_OF]->(g)")
        
        chunks_data.append({
            "id": c_id, "parent_id": node_id,
            "x": c_ux, "y": c_uy, "z": c_uz,
            "r": c_ur, "g": c_ug, "b": c_ub
        })

    avg_emb = sum_emb / len(chunks)
    g_coords, g_colors = project_embeddings(np.array([avg_emb]))
    g_ux, g_uy, g_uz = (float(g_coords[0][0]), float(g_coords[0][1]), float(g_coords[0][2])) if len(g_coords) > 0 else (0.0, 0.0, 0.0)
    g_ur, g_ug, g_ub = (float(g_colors[0][0]), float(g_colors[0][1]), float(g_colors[0][2])) if len(g_colors) > 0 else (0.5, 0.5, 0.5)
    
    conn.execute(f"MATCH (g:GlobalNode) WHERE g.id = '{node_id}' SET g.embedding = $emb, g.ux = $ux, g.uy = $uy, g.uz = $uz, g.ur = $ur, g.ug = $ug, g.ub = $ub", 
        {"emb": avg_emb.tolist(), "ux": g_ux, "uy": g_uy, "uz": g_uz, "ur": g_ur, "ug": g_ug, "ub": g_ub})
        
    return jsonify({
        "success": True, 
        "chunks": chunks_data,
        "global_node": {
            "id": node_id, "x": g_ux, "y": g_uy, "z": g_uz,
            "r": g_ur, "g": g_ug, "b": g_ub
        }
    })

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '')
    
    if not query: return jsonify({"results": []})
    
    target_vec = embed_texts([query])[0]
    
    conn = get_conn()
    results = []
    
    norm_target = np.linalg.norm(target_vec)
    
    # Search Chunks
    res_chunks = conn.execute("MATCH (c:ChunkNode) RETURN c.id, c.chunk_type, c.content, c.embedding")
    while res_chunks.has_next():
        cid, ctype, content, emb = res_chunks.get_next()
        vec = np.array(emb)
        sim = np.dot(target_vec, vec) / (norm_target * np.linalg.norm(vec)) if norm_target and np.linalg.norm(vec) else 0
        results.append({"id": cid, "node_type": "chunk", "type": ctype, "content": content, "score": float(sim)})
        
    results.sort(key=lambda x: x['score'], reverse=True)
    return jsonify({"nodes": results[:10]})

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    data = request.json or {}
    message = data.get('message', '')
    session_id = data.get('session_id')
    context_ids = data.get('context_ids', '') # Comma separated for @ refs
    
    if not session_id: session_id = f"session_{uuid.uuid4().hex[:8]}"
    
    if not llm:
        return Response("data: " + json.dumps({'error': 'LLM not loaded'}) + "\n\n", mimetype='text/event-stream')
    
    conn = get_conn()
    
    # Ensure session exists
    res = conn.execute(f"MATCH (s:GlobalNode) WHERE s.id = '{session_id}' RETURN s.ux, s.uy, s.uz")
    if not res.has_next():
        s_emb = embed_texts(["Chat Session"])[0]
        c_c, c_color = project_embeddings(np.array([s_emb]))
        s_ux, s_uy, s_uz = float(c_c[0][0]), float(c_c[0][1]), float(c_c[0][2])
        params = {
            "id": session_id, "type": "session", "title": "New Chat", "role": "", "content": "", "created_at": datetime.now().isoformat(),
            "emb": s_emb.tolist(), "ux": s_ux, "uy": s_uy, "uz": s_uz,
            "ur": float(c_color[0][0]), "ug": float(c_color[0][1]), "ub": float(c_color[0][2])
        }
        conn.execute("CREATE (s:GlobalNode {id: $id, type: $type, title: $title, role: $role, content: $content, created_at: $created_at, embedding: $emb, ux: $ux, uy: $uy, uz: $uz, ur: $ur, ug: $ug, ub: $ub})", params)
    else:
        row = res.get_next()
        s_ux, s_uy, s_uz = row[0], row[1], row[2]

    def generate():
        # Handle User Message
        user_msg_id = f"msg_{uuid.uuid4().hex[:8]}"
        u_emb = embed_texts([message])[0]
        c_c, c_color = project_embeddings(np.array([u_emb]))
        
        # Save User Message GlobalNode
        params = {
            "id": user_msg_id, "type": "message", "title": "", "role": "user", "content": message, "created_at": datetime.now().isoformat(),
            "emb": u_emb.tolist(), "ux": float(c_c[0][0]), "uy": float(c_c[0][1]), "uz": float(c_c[0][2]),
            "ur": 0.2, "ug": 0.8, "ub": 1.0 # Cyan for user
        }
        conn.execute("CREATE (m:GlobalNode {id: $id, type: $type, title: $title, role: $role, content: $content, created_at: $created_at, embedding: $emb, ux: $ux, uy: $uy, uz: $uz, ur: $ur, ug: $ug, ub: $ub})", params)
        conn.execute(f"MATCH (m:GlobalNode {{id: '{user_msg_id}'}}), (s:GlobalNode {{id: '{session_id}'}}) CREATE (m)-[:IN_SESSION]->(s)")
        
        # Process Context (@ references)
        context_text = ""
        if context_ids:
            c_ids = [cid.strip() for cid in context_ids.split(',') if cid.strip()]
            all_chunks = []
            
            for cid in c_ids:
                # Check GlobalNode
                res_g = conn.execute(f"MATCH (g:GlobalNode) WHERE g.id = '{cid}' RETURN count(g)")
                is_global = res_g.get_next()[0] > 0 if res_g.has_next() else False
                
                if is_global:
                    conn.execute(f"MATCH (m:GlobalNode {{id: '{user_msg_id}'}}), (t:GlobalNode {{id: '{cid}'}}) CREATE (m)-[:REFERENCES]->(t)")
                    res_c = conn.execute(f"MATCH (c:ChunkNode)-[:PART_OF]->(t:GlobalNode {{id: '{cid}'}}) RETURN c.id, c.content, c.embedding, c.lineage, t.title")
                    while res_c.has_next():
                        row = res_c.get_next()
                        all_chunks.append({"id": row[0], "content": row[1], "emb": np.array(row[2]), "lineage": row[3], "doc_title": row[4]})
                else:
                    # Check ChunkNode
                    res_c2 = conn.execute(f"MATCH (c:ChunkNode)-[:PART_OF]->(t:GlobalNode) WHERE c.id = '{cid}' RETURN c.id, c.content, c.embedding, c.lineage, t.title")
                    if res_c2.has_next():
                        conn.execute(f"MATCH (m:GlobalNode {{id: '{user_msg_id}'}}), (c:ChunkNode {{id: '{cid}'}}) CREATE (m)-[:RETRIEVES]->(c)")
                        row = res_c2.get_next()
                        all_chunks.append({"id": row[0], "content": row[1], "emb": np.array(row[2]), "lineage": row[3], "doc_title": row[4]})

            # Rank by cosine similarity to u_emb
            if all_chunks:
                norm_u = np.linalg.norm(u_emb)
                for c in all_chunks:
                    norm_c = np.linalg.norm(c["emb"])
                    c["score"] = np.dot(u_emb, c["emb"]) / (norm_u * norm_c) if norm_u and norm_c else 0
                
                all_chunks.sort(key=lambda x: x["score"], reverse=True)
                
                current_tokens = 0
                doc_groups = {}
                for c in all_chunks:
                    tokens = len(c["content"].split()) * 1.3
                    if current_tokens + tokens > 256:
                        break
                    doc_title = c["doc_title"] or "Untitled"
                    if doc_title not in doc_groups: doc_groups[doc_title] = []
                    doc_groups[doc_title].append(c)
                    current_tokens += tokens
                    
                for title, chunks_list in doc_groups.items():
                    context_text += f"\n--- From Document: {title} ---\n"
                    for c in chunks_list:
                        if c["lineage"]: context_text += f"{c['lineage']}\n"
                        context_text += f"{c['content']}\n"
        
        # Build prompt
        system_prompt = "You are a helpful AI assistant."
        prompt = f"### Instruction:\n{system_prompt}\n"
        if context_text:
            prompt += f"\nContext:\n{context_text}\n"
            
        # Get history (last 4 messages in session)
        res_hist = conn.execute(f"MATCH (m:GlobalNode)-[:IN_SESSION]->(s:GlobalNode {{id: '{session_id}'}}) WHERE m.id <> '{user_msg_id}' RETURN m.role, m.content ORDER BY m.created_at DESC LIMIT 4")
        hist = []
        while res_hist.has_next():
            row = res_hist.get_next()
            hist.insert(0, row) # reverse to chronological
            
        for role, content in hist:
            r = "User" if role == "user" else "Assistant"
            prompt += f"{r}: {content}\n"
            
        prompt += f"User: {message}\n### Response:\n"

        # Do not yield user_msg_id as a separate node in the frontend, as we are aggregating into the session

        output_text = ""
        try:
            for token in llm.generate(prompt, streaming=True, max_tokens=400):
                output_text += token
                yield "data: " + json.dumps({'type': 'token', 'content': token}) + "\n\n"
        except Exception as e:
            yield "data: " + json.dumps({'error': str(e)}) + "\n\n"

        # Save AI Response
        ai_msg_id = f"msg_{uuid.uuid4().hex[:8]}"
        chunks = parse_markdown_to_chunks(output_text)
        
        # Embed AI Response and Chunks
        a_emb = embed_texts([output_text])[0]
        c_a_c, c_a_color = project_embeddings(np.array([a_emb]))
        
        # We don't render ai_msg_id in frontend either, just store it
        params_ai = {
            "id": ai_msg_id, "type": "message", "title": "", "role": "assistant", "content": output_text, "created_at": datetime.now().isoformat(),
            "emb": a_emb.tolist(), "ux": float(s_ux), "uy": float(s_uy), "uz": float(s_uz),
            "ur": 1.0, "ug": 0.5, "ub": 0.2 # Orange for AI
        }
        conn.execute("CREATE (m:GlobalNode {id: $id, type: $type, title: $title, role: $role, content: $content, created_at: $created_at, embedding: $emb, ux: $ux, uy: $uy, uz: $uz, ur: $ur, ug: $ug, ub: $ub})", params_ai)
        conn.execute(f"MATCH (m:GlobalNode {{id: '{ai_msg_id}'}}), (s:GlobalNode {{id: '{session_id}'}}) CREATE (m)-[:IN_SESSION]->(s)")
        
        # Save chunks
        chunk_nodes = []
        chunk_texts = [c['content'] for c in chunks]
        if chunk_texts:
            chunk_embs = embed_texts(chunk_texts)
            chunk_coords, chunk_colors = project_embeddings(chunk_embs)
            c_mean = np.mean(chunk_coords, axis=0) if len(chunk_coords) > 0 else np.array([0,0,0])
            for i, chunk in enumerate(chunks):
                chunk_id = f"chunk_{uuid.uuid4().hex[:8]}"
                # Cluster chunks around the base session node
                rel_pos = (chunk_coords[i] - c_mean) * 0.2 # Scale down for tight cluster
                c_ux = float(s_ux + rel_pos[0])
                c_uy = float(s_uy + rel_pos[1])
                c_uz = float(s_uz + rel_pos[2])
                
                cp = {
                    "id": chunk_id, "chunk_type": chunk['type'], "content": chunk['content'], "lineage": chunk.get("lineage", ""),
                    "emb": chunk_embs[i].tolist(), "ux": c_ux, "uy": c_uy, "uz": c_uz,
                    "ur": float(chunk_colors[i][0]), "ug": float(chunk_colors[i][1]), "ub": float(chunk_colors[i][2])
                }
                conn.execute("CREATE (c:ChunkNode {id: $id, chunk_type: $chunk_type, content: $content, lineage: $lineage, embedding: $emb, ux: $ux, uy: $uy, uz: $uz, ur: $ur, ug: $ug, ub: $ub})", cp)
                conn.execute(f"MATCH (c:ChunkNode {{id: '{chunk_id}'}}), (s:GlobalNode {{id: '{session_id}'}}) CREATE (c)-[:PART_OF]->(s)")
                
                chunk_nodes.append({
                    'id': chunk_id, 'node_type': 'chunk', 'type': chunk['type'],
                    'pos': [c_ux, c_uy, c_uz],
                    'color': [float(chunk_colors[i][0]), float(chunk_colors[i][1]), float(chunk_colors[i][2])],
                    'size': 1.0,
                    'parent_id': session_id
                })

        # Calculate Diffuse Layout
        diffuse_layout = {}
        res_all_c = conn.execute(f"MATCH (c:ChunkNode)-[:PART_OF]->(s:GlobalNode {{id: '{session_id}'}}) RETURN c.id, c.chunk_type, c.embedding, c.content")
        all_session_chunks = []
        while res_all_c.has_next():
            r = res_all_c.get_next()
            all_session_chunks.append({"id": r[0], "type": r[1], "emb": np.array(r[2]), "content": r[3]})
            
        type_groups = {}
        for sc in all_session_chunks:
            ctype = sc["type"]
            if ctype not in type_groups: type_groups[ctype] = []
            type_groups[ctype].append(sc)
            
        for ctype, items in type_groups.items():
            if not items: continue
            # centroid
            centroid = np.mean([item["emb"] for item in items], axis=0)
            norm_centroid = np.linalg.norm(centroid)
            
            for item in items:
                norm_item = np.linalg.norm(item["emb"])
                item["score"] = np.dot(centroid, item["emb"]) / (norm_centroid * norm_item) if norm_centroid and norm_item else 0

        type_order = ['heading', 'paragraph', 'list', 'code', 'table']
        sorted_types = sorted(type_groups.keys(), key=lambda k: type_order.index(k) if k in type_order else 99)
        
        diffused_parts = []
        for ctype in sorted_types:
            items = type_groups[ctype]
            items.sort(key=lambda x: x["score"], reverse=True)
            diffuse_layout[ctype] = [item["id"] for item in items]
            for item in items:
                diffused_parts.append(item["content"])
                
        diffused_content = "\n\n".join(diffused_parts)
        
        # update GlobalNode in db
        if all_session_chunks:
            sum_emb = np.sum([c["emb"] for c in all_session_chunks], axis=0)
            avg_emb = sum_emb / len(all_session_chunks)
            g_coords, _ = project_embeddings(np.array([avg_emb]))
            g_ux, g_uy, g_uz = (float(g_coords[0][0]), float(g_coords[0][1]), float(g_coords[0][2])) if len(g_coords) > 0 else (s_ux, s_uy, s_uz)
            conn.execute("MATCH (n:GlobalNode {id: $id}) SET n.content = $content, n.embedding = $emb, n.ux = $ux, n.uy = $uy, n.uz = $uz", 
                {"id": session_id, "content": diffused_content, "emb": avg_emb.tolist(), "ux": g_ux, "uy": g_uy, "uz": g_uz})
        else:
            conn.execute("MATCH (n:GlobalNode {id: $id}) SET n.content = $content", {"id": session_id, "content": diffused_content})
            g_ux, g_uy, g_uz = s_ux, s_uy, s_uz

        yield "data: " + json.dumps({
            'type': 'graph_update',
            'nodes': chunk_nodes,
            'edges': [],
            'diffuse_layout': diffuse_layout,
            'diffused_content': diffused_content,
            'global_node': {
                'id': session_id, 'x': g_ux, 'y': g_uy, 'z': g_uz
            }
        }) + "\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    print("[System] Starting Flask Server...")
    init_db()
    init_llm()
    app.run(debug=True, port=5000, use_reloader=False)
