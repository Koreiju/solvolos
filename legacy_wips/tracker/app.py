import os
import json
import csv
import sys
import traceback
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import kuzu
from nomic import embed
import umap
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import joblib
from gpt4all import GPT4All
import uuid

app = Flask(__name__, template_folder='ui/templates', static_folder='ui/static')

# Configuration
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_ROOT, 'company_db.kuzu')
CSV_PATH = os.path.join(APP_ROOT, 'companies.csv')
UMAP_MODEL_PATH = os.path.join(APP_ROOT, 'umap_reducer.joblib')
SCALER_MODEL_PATH = os.path.join(APP_ROOT, 'scaler.joblib')
# Nomic API key is still required for local inference to authenticate/download the model initially
NOMIC_API_KEY = os.environ.get("NOMIC_API_KEY", "") 

# Disable caching for static files during development
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Global State
llm = None
umap_reducer = None
scaler = None
CHAT_SESSIONS = {}  # In-memory storage for chat sessions {id: {name: str, history: []}}

# Initialize Database
print(f"[System] Initializing Kuzu Database at {DB_PATH}")
try:
    db = kuzu.Database(DB_PATH)
    print("[System] Database initialized successfully")
except Exception as e:
    print(f"[FATAL] Failed to initialize database: {e}")
    traceback.print_exc()
    sys.exit(1)

def get_conn():
    try:
        return kuzu.Connection(db)
    except Exception as e:
        print(f"[ERROR] Failed to create DB connection: {e}")
        traceback.print_exc()
        raise

@app.before_request
def log_request_info():
    if not request.path.startswith('/static') and not request.path == '/favicon.ico':
        print(f"[REQUEST] {request.method} {request.path}")

@app.after_request
def log_response_info(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/favicon.ico')
def favicon():
    return "", 204

# --- LLM Initialization ---
def init_llm():
    global llm
    model_name = "Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf"
    # Check if file exists locally or let gpt4all handle download
    print(f"[System] Initializing GPT4All Model: {model_name}")
    try:
        # allow_download=True will download if not present in default cache
        llm = GPT4All(
            model_name,
            device="cuda", # Attempt CUDA as requested
            n_threads=4,
            ngl=100,       # Layers to GPU
            verbose=False
        )
        print("[System] LLM Initialized successfully on CUDA.")
    except Exception as e:
        print(f"[WARN] Failed to init LLM on CUDA: {e}. Falling back to CPU/Default.")
        try:
            llm = GPT4All(model_name, device="cpu")
            print("[System] LLM Initialized on CPU.")
        except Exception as e2:
            print(f"[ERROR] LLM Initialization failed completely: {e2}")

# --- Data Loading & UMAP ---

def init_db():
    global umap_reducer, scaler
    print("[DEBUG] Starting init_db()...")
    conn = get_conn()
    try:
        print("[DEBUG] Installing/Loading vector extension...")
        conn.execute("INSTALL vector; LOAD vector;")
    except Exception as e:
        print(f"[WARN] Vector extension load ignored: {e}")

    # Load UMAP reducer and Scaler if exist
    if os.path.exists(UMAP_MODEL_PATH) and os.path.exists(SCALER_MODEL_PATH):
        try:
            umap_reducer = joblib.load(UMAP_MODEL_PATH)
            scaler = joblib.load(SCALER_MODEL_PATH)
            print("[System] Loaded persisted UMAP reducer and Scaler.")
        except Exception as e:
            print(f"[WARN] Failed to load ML models: {e}")

    try:
        print("[DEBUG] Checking if Company table exists...")
        res = conn.execute("MATCH (c:Company) RETURN count(c)")
        if res.has_next():
            count = res.get_next()[0]
            print(f"[DEBUG] Table 'Company' found with {count} rows.")
            if count == 0:
                print("[DEBUG] Table is empty. Triggering data load...")
                load_data()
    except Exception as e:
        print(f"[DEBUG] Table 'Company' check failed ({e}). Creating schema...")
        try:
            conn.execute("""
                CREATE NODE TABLE Company(
                    id SERIAL,
                    name STRING,
                    location STRING,
                    description STRING,
                    website STRING,
                    embedding FLOAT[768],
                    umap_x FLOAT,
                    umap_y FLOAT,
                    umap_z FLOAT,
                    umap_r FLOAT,
                    umap_g FLOAT,
                    umap_b FLOAT,
                    status STRING,
                    tags STRING[],
                    PRIMARY KEY (id)
                )
            """)
            print("[DEBUG] Schema created successfully.")
            load_data()
        except Exception as create_error:
            print(f"[CRITICAL] Error creating schema: {create_error}")
            traceback.print_exc()

def load_data():
    global umap_reducer, scaler
    print("[DEBUG] Starting load_data()...")
    if not os.path.exists(CSV_PATH):
        print(f"[WARN] {CSV_PATH} not found.")
        return

    print(f"[DEBUG] Reading CSV from {CSV_PATH}...")
    try:
        df = pd.read_csv(CSV_PATH, on_bad_lines='warn', engine='python')
        print(f"[DEBUG] CSV loaded. Found {len(df)} rows.")
        
        # Deduplication
        initial_count = len(df)
        df['Entity Name'] = df['Entity Name'].astype(str).str.strip()
        df['Website'] = df['Website'].astype(str).str.strip()
        df['Description'] = df['Description'].astype(str).str.strip()
        df['desc_len'] = df['Description'].str.len()
        df.sort_values('desc_len', ascending=False, inplace=True)
        df.drop_duplicates(subset=['Entity Name'], keep='first', inplace=True)
        
        mask_website = df['Website'].str.len() > 3
        df_websites = df[mask_website].copy()
        df_no_websites = df[~mask_website].copy()
        df_websites.drop_duplicates(subset=['Website'], keep='first', inplace=True)
        df = pd.concat([df_websites, df_no_websites])
        
        print(f"[DEBUG] Deduplication complete. Remaining: {len(df)}")
        
    except Exception as e:
        print(f"[CRITICAL] Error reading/processing CSV: {e}")
        traceback.print_exc()
        return

    if len(df) == 0: return

    df.fillna('', inplace=True)
    descriptions = df['Description'].tolist()
    
    print("[DEBUG] Generating embeddings locally on CUDA...")
    try:
        output = embed.text(
            texts=descriptions, 
            model='nomic-embed-text-v1.5', 
            task_type='search_document',
            inference_mode="local", 
            device="cuda"
        )
        embeddings = np.array(output['embeddings'])
    except Exception as e:
        print(f"[ERROR] Embedding failed: {e}. Falling back to random.")
        embeddings = np.random.rand(len(df), 768)

    print("[DEBUG] Computing 6D UMAP projection...")
    try:
        # Fit Scaler
        scaler = StandardScaler()
        scaled_embeddings = scaler.fit_transform(embeddings)
        joblib.dump(scaler, SCALER_MODEL_PATH)

        # Fit UMAP
        umap_reducer = umap.UMAP(n_components=6, n_neighbors=15, min_dist=0.1, metric='cosine')
        umap_result = umap_reducer.fit_transform(scaled_embeddings)
        joblib.dump(umap_reducer, UMAP_MODEL_PATH)
        
        print("[System] Scaler and UMAP reducer saved to disk.")
        
        umap_coords = umap_result[:, 0:3]
        umap_colors = umap_result[:, 3:6]
        
        color_scaler = MinMaxScaler(feature_range=(0, 1))
        umap_colors = color_scaler.fit_transform(umap_colors)
    except Exception as e:
        print(f"[ERROR] UMAP failed: {e}")
        return
    
    print("[DEBUG] Inserting into Kuzu DB...")
    conn = get_conn()
    
    try:
        conn.execute("MATCH (n:Company) DELETE n") 
    except:
        pass
    
    for i, (idx, row) in enumerate(df.iterrows()):
        try:
            name = str(row.get('Entity Name', 'Unknown')).replace('"', "'")
            location = str(row.get('Location', '')).replace('"', "'")
            desc = str(row.get('Description', '')).replace('"', "'")
            web = str(row.get('Website', '')).replace('"', "'")
            
            params = {
                "name": name, 
                "location": location, 
                "description_text": desc, 
                "web": web,
                "emb": embeddings[i].tolist(),
                "ux": float(umap_coords[i][0]), 
                "uy": float(umap_coords[i][1]), 
                "uz": float(umap_coords[i][2]),
                "ur": float(umap_colors[i][0]),
                "ug": float(umap_colors[i][1]),
                "ub": float(umap_colors[i][2]),
                "status": "unreviewed", 
                "tags": []
            }
            conn.execute(
                """CREATE (c:Company {
                    name: $name, location: $location, description: $description_text, 
                    website: $web, embedding: $emb, 
                    umap_x: $ux, umap_y: $uy, umap_z: $uz, 
                    umap_r: $ur, umap_g: $ug, umap_b: $ub, 
                    status: $status, tags: $tags
                })""", params)
        except Exception: pass
            
    print(f"[INFO] Data load complete.")

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/companies', methods=['GET'])
def get_companies():
    conn = get_conn()
    try:
        result = conn.execute("MATCH (c:Company) RETURN c.id, c.name, c.umap_x, c.umap_y, c.umap_z, c.umap_r, c.umap_g, c.umap_b, c.status, c.location, c.tags")
        nodes = []
        while result.has_next():
            row = result.get_next()
            def safe_float(val):
                try:
                    f = float(val)
                    return 0.0 if np.isnan(f) else f
                except: return 0.0
            nodes.append({
                "id": row[0], "name": row[1], 
                "x": safe_float(row[2]), "y": safe_float(row[3]), "z": safe_float(row[4]),
                "r": safe_float(row[5]), "g": safe_float(row[6]), "b": safe_float(row[7]),
                "status": row[8], "location": row[9], "tags": row[10] if row[10] else []
            })
        return jsonify({"nodes": nodes})
    except Exception as e:
        return jsonify({"error": str(e), "nodes": []}), 500

@app.route('/api/details/<int:node_id>', methods=['GET'])
def get_details(node_id):
    conn = get_conn()
    try:
        result = conn.execute(f"MATCH (c:Company) WHERE c.id = {node_id} RETURN c.name, c.location, c.description, c.website, c.status, c.tags")
        if result.has_next():
            row = result.get_next()
            return jsonify({
                "id": node_id, "name": row[0], "location": row[1], "description": row[2],
                "website": row[3], "status": row[4], "tags": row[5] if row[5] else []
            })
    except Exception: pass
    return jsonify({"error": "Not found"}), 404

@app.route('/api/search', methods=['POST'])
def search_companies():
    try:
        data = request.json
        target_id = data.get('target_id')
        query_text = data.get('query')
        limit = data.get('limit', 10)
        conn = get_conn()
        target_vec = None

        if target_id is not None:
            res = conn.execute(f"MATCH (c:Company) WHERE c.id = {target_id} RETURN c.embedding")
            if res.has_next(): target_vec = np.array(res.get_next()[0])
        elif query_text:
            output = embed.text(texts=[query_text], model='nomic-embed-text-v1.5', task_type='search_query', inference_mode="local", device="cuda")
            target_vec = np.array(output['embeddings'][0])

        if target_vec is None: return jsonify({"results": []})

        res = conn.execute("MATCH (c:Company) RETURN c.id, c.name, c.description, c.status, c.location, c.tags, c.embedding")
        results = []
        norm_target = np.linalg.norm(target_vec)
        
        while res.has_next():
            row = res.get_next()
            cid, name, desc, status, loc, tags, emb = row
            if target_id and cid == target_id: continue
            vec = np.array(emb)
            sim = np.dot(target_vec, vec) / (norm_target * np.linalg.norm(vec)) if norm_target and np.linalg.norm(vec) else 0
            results.append({"id": cid, "name": name, "description": desc, "status": status, "location": loc, "tags": tags, "score": float(sim)})
            
        results.sort(key=lambda x: x['score'], reverse=True)
        return jsonify({"results": results[:limit]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/update', methods=['POST'])
def update_company():
    try:
        data = request.json
        node_id = data.get('id')
        status = data.get('status')
        tags = data.get('tags')
        conn = get_conn()
        if status:
            conn.execute(f"MATCH (c:Company) WHERE c.id = {node_id} SET c.status = '{status}'")
        if tags is not None:
            tag_str = "[" + ", ".join([f"'{t}'" for t in tags]) + "]"
            conn.execute(f"MATCH (c:Company) WHERE c.id = {node_id} SET c.tags = {tag_str}")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Session Management API ---

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    sessions = []
    for sid, data in CHAT_SESSIONS.items():
        sessions.append({'id': sid, 'name': data.get('name', 'Untitled')})
    return jsonify(sessions)

@app.route('/api/sessions', methods=['POST'])
def create_session():
    data = request.json
    sid = data.get('id') or str(uuid.uuid4())
    name = data.get('name', 'New Chat')
    CHAT_SESSIONS[sid] = {'name': name, 'history': []}
    return jsonify({'id': sid, 'name': name})

@app.route('/api/sessions/<session_id>/rename', methods=['POST'])
def rename_session(session_id):
    data = request.json
    if session_id in CHAT_SESSIONS:
        CHAT_SESSIONS[session_id]['name'] = data.get('name', 'Untitled')
        return jsonify({'success': True})
    return jsonify({'error': 'Session not found'}), 404

# --- Chat Stream API ---

@app.route('/api/chat/stream', methods=['GET'])
def chat_stream():
    message = request.args.get('message', '')
    session_id = request.args.get('session_id')
    
    if not llm:
        return Response("data: " + json.dumps({'error': 'LLM not loaded'}) + "\n\n", mimetype='text/event-stream')
    
    if session_id not in CHAT_SESSIONS:
        CHAT_SESSIONS[session_id] = {'name': 'New Chat', 'history': []}
    
    session = CHAT_SESSIONS[session_id]

    def generate():
        # 1. Project User Message
        user_node_id = f"chat_u_{uuid.uuid4().hex[:6]}"
        try:
            if umap_reducer and scaler:
                emb = embed.text([message], inference_mode="local", device="cpu", model="nomic-embed-text-v1.5")['embeddings']
                
                # Apply same scaling as training data
                emb_scaled = scaler.transform(np.array(emb))
                proj = umap_reducer.transform(emb_scaled)
                
                p_x, p_y, p_z = proj[0][0], proj[0][1], proj[0][2]
                
                # Send Node Data
                yield "data: " + json.dumps({
                    'chunk': '', 
                    'nodes': [{
                        'id': user_node_id, 
                        'pos': [float(p_x), float(p_y), float(p_z)],
                        'color': [0.2, 0.8, 1.0], # Cyan for user
                        'label': 'You',
                        'type': 'user'
                    }]
                }) + "\n\n"
        except Exception as e:
            print(f"Projection error: {e}")

        # 2. Build Prompt
        system_prompt = "You are an AI assistant helping a user explore a database of companies. Be concise and helpful."
        prompt = f"### Instruction:\n{system_prompt}\n"
        
        for msg in session['history'][-6:]:
            role = "User" if msg['role'] == 'user' else "Assistant"
            prompt += f"{role}: {msg['content']}\n"
        
        prompt += f"User: {message}\n### Response:\n"

        # 3. Stream LLM
        output_text = ""
        try:
            for token in llm.generate(prompt, streaming=True, max_tokens=400):
                output_text += token
                yield "data: " + json.dumps({'chunk': token}) + "\n\n"
        except Exception as e:
             yield "data: " + json.dumps({'error': str(e)}) + "\n\n"
        
        # 4. Save History
        session['history'].append({'role': 'user', 'content': message})
        session['history'].append({'role': 'assistant', 'content': output_text})

        # 5. Project AI Response
        try:
            if umap_reducer and scaler and output_text:
                emb = embed.text([output_text], inference_mode="local", device="cpu", model="nomic-embed-text-v1.5")['embeddings']
                
                # Apply same scaling
                emb_scaled = scaler.transform(np.array(emb))
                proj = umap_reducer.transform(emb_scaled)
                
                ai_node_id = f"chat_a_{uuid.uuid4().hex[:6]}"
                
                yield "data: " + json.dumps({
                    'chunk': '',
                    'complete': True,
                    'nodes': [
                        # Resend user node ID to link them if frontend missed it
                        {'id': user_node_id, 'type': 'user', 'pos': [0,0,0], 'color': [0,0,0]}, 
                        {
                            'id': ai_node_id,
                            'pos': [float(proj[0][0]), float(proj[0][1]), float(proj[0][2])],
                            'color': [1.0, 0.5, 0.2], # Orange for AI
                            'label': 'AI',
                            'type': 'bot'
                        }
                    ]
                }) + "\n\n"
            else:
                yield "data: " + json.dumps({'complete': True}) + "\n\n"
        except Exception:
            yield "data: " + json.dumps({'complete': True}) + "\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    print("[System] Starting Flask Server...")
    init_db() # Also loads/saves UMAP & Scaler
    init_llm() # Loads GPT4All
    app.run(debug=True, port=5000, use_reloader=False)