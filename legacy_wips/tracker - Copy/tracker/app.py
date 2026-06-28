import os
import json
import csv
import sys
import traceback
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify
import kuzu
from nomic import embed
import umap
from sklearn.preprocessing import StandardScaler, MinMaxScaler

app = Flask(__name__, template_folder='ui/templates', static_folder='ui/static')

# Configuration
DB_PATH = 'company_db.kuzu'
CSV_PATH = 'companies.csv'
# Nomic API key is still required for local inference to authenticate/download the model initially
NOMIC_API_KEY = os.environ.get("NOMIC_API_KEY", "") 

# Disable caching for static files during development to ensure JS updates apply immediately
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Initialize Database
# Note: KuzuDB requires exclusive access to the database directory.
print(f"[System] Initializing Kuzu Database at {DB_PATH}")
try:
    db = kuzu.Database(DB_PATH)
    print("[System] Database initialized successfully")
except Exception as e:
    print(f"[FATAL] Failed to initialize database: {e}")
    traceback.print_exc()
    sys.exit(1)

def get_conn():
    """Create a new connection to the database. Best practice for Flask threading."""
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

# Stop 404 spam
@app.route('/favicon.ico')
def favicon():
    return "", 204

def init_db():
    print("[DEBUG] Starting init_db()...")
    conn = get_conn()
    try:
        print("[DEBUG] Installing/Loading vector extension...")
        conn.execute("INSTALL vector; LOAD vector;")
    except Exception as e:
        print(f"[WARN] Vector extension load ignored (likely already loaded): {e}")

    try:
        # Check if table exists and has data
        print("[DEBUG] Checking if Company table exists...")
        res = conn.execute("MATCH (c:Company) RETURN count(c)")
        if res.has_next():
            count = res.get_next()[0]
            print(f"[DEBUG] Table 'Company' found with {count} rows.")
            if count == 0:
                print("[DEBUG] Table is empty. Triggering data load...")
                load_data()
    except Exception as e:
        # Table likely doesn't exist, create schema and load data
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
    print("[DEBUG] Starting load_data()...")
    if not os.path.exists(CSV_PATH):
        print(f"[WARN] {CSV_PATH} not found.")
        return

    print(f"[DEBUG] Reading CSV from {CSV_PATH}...")
    try:
        # UPDATED: More robust CSV parsing
        df = pd.read_csv(CSV_PATH, on_bad_lines='warn', engine='python')
        print(f"[DEBUG] CSV loaded. Found {len(df)} rows.")
        
        # --- Deduplication Logic ---
        initial_count = len(df)
        
        # 1. Clean data for consistent matching
        df['Entity Name'] = df['Entity Name'].astype(str).str.strip()
        df['Website'] = df['Website'].astype(str).str.strip()
        df['Description'] = df['Description'].astype(str).str.strip()
        
        # 2. Sort by Description length (descending) to prioritize richer content
        df['desc_len'] = df['Description'].str.len()
        df.sort_values('desc_len', ascending=False, inplace=True)
        
        # 3. Deduplicate by Name (keep longest desc)
        df.drop_duplicates(subset=['Entity Name'], keep='first', inplace=True)
        
        # 4. Deduplicate by Website (keep longest desc), ignoring empty websites
        # Separate rows with valid websites vs empty
        # We assume lengths < 3 are likely invalid/empty for a URL
        mask_website = df['Website'].str.len() > 3
        df_websites = df[mask_website].copy()
        df_no_websites = df[~mask_website].copy()
        
        # Drop dupes in the valid website group
        df_websites.drop_duplicates(subset=['Website'], keep='first', inplace=True)
        
        # Combine back
        df = pd.concat([df_websites, df_no_websites])
        
        print(f"[DEBUG] Deduplication complete. Removed {initial_count - len(df)} duplicates. Remaining: {len(df)}")
        
    except Exception as e:
        print(f"[CRITICAL] Error reading/processing CSV: {e}")
        traceback.print_exc()
        return

    if len(df) == 0:
        print("[WARN] CSV is empty after processing. Skipping load.")
        return

    df.fillna('', inplace=True)
    
    required_cols = ['Entity Name', 'Location', 'Description', 'Website']
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        print(f"[ERROR] CSV is missing columns: {missing_cols}")
        print(f"[DEBUG] Found columns: {df.columns.tolist()}")
        return

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
        print(f"[DEBUG] Generated {len(embeddings)} embeddings with dimension {len(embeddings[0])}")
    except Exception as e:
        print(f"[ERROR] Embedding failed: {e}. Falling back to random for demo purposes.")
        traceback.print_exc()
        embeddings = np.random.rand(len(df), 768)

    print("[DEBUG] Computing 6D UMAP projection (3 Spatial + 3 Color)...")
    try:
        # Increase components to 6
        reducer = umap.UMAP(n_components=6, n_neighbors=15, min_dist=0.1, metric='cosine')
        scaled_embeddings = StandardScaler().fit_transform(embeddings)
        umap_result = reducer.fit_transform(scaled_embeddings)
        
        # Split into Spatial (X, Y, Z) and Color (R, G, B)
        umap_coords = umap_result[:, 0:3]
        umap_colors = umap_result[:, 3:6]
        
        # Normalize Color dimensions to [0, 1] range for RGB
        color_scaler = MinMaxScaler(feature_range=(0, 1))
        umap_colors = color_scaler.fit_transform(umap_colors)
        
        print("[DEBUG] UMAP projection complete.")
    except Exception as e:
        print(f"[ERROR] UMAP failed: {e}")
        traceback.print_exc()
        return
    
    print("[DEBUG] Inserting into Kuzu DB...")
    
    conn = get_conn()
    success_count = 0
    
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
                    name: $name, 
                    location: $location, 
                    description: $description_text, 
                    website: $web, 
                    embedding: $emb, 
                    umap_x: $ux, umap_y: $uy, umap_z: $uz, 
                    umap_r: $ur, umap_g: $ug, umap_b: $ub, 
                    status: $status, 
                    tags: $tags
                })""",
                params
            )
            success_count += 1
        except Exception as insert_err:
            print(f"[ERROR] Failed to insert row {idx}: {insert_err}")
            
    print(f"[INFO] Data load complete. Successfully inserted {success_count} nodes.")

# Run initialization
init_db()

@app.route('/')
def index():
    print("[DEBUG] Serving index.html")
    return render_template('index.html')

@app.route('/api/companies', methods=['GET'])
def get_companies():
    print("[DEBUG] Endpoint /api/companies called")
    conn = get_conn()
    try:
        print("[DEBUG] Executing MATCH query...")
        result = conn.execute("MATCH (c:Company) RETURN c.id, c.name, c.umap_x, c.umap_y, c.umap_z, c.umap_r, c.umap_g, c.umap_b, c.status, c.location, c.tags")
        nodes = []
        while result.has_next():
            row = result.get_next()
            def safe_float(val):
                try:
                    f = float(val)
                    return 0.0 if np.isnan(f) else f
                except:
                    return 0.0

            nodes.append({
                "id": row[0], 
                "name": row[1], 
                "x": safe_float(row[2]), 
                "y": safe_float(row[3]), 
                "z": safe_float(row[4]),
                "r": safe_float(row[5]),
                "g": safe_float(row[6]),
                "b": safe_float(row[7]),
                "status": row[8], 
                "location": row[9], 
                "tags": row[10] if row[10] else []
            })
        print(f"[DEBUG] /api/companies returning {len(nodes)} companies.")
        return jsonify({"nodes": nodes})
    except Exception as e:
        print(f"[ERROR] get_companies failed: {e}")
        traceback.print_exc()
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
    except Exception as e:
        print(f"[ERROR] get_details failed: {e}")
        traceback.print_exc()
    return jsonify({"error": "Not found"}), 404

@app.route('/api/search', methods=['POST'])
def search_companies():
    try:
        data = request.json
        target_id = data.get('target_id')
        query_text = data.get('query')
        limit = data.get('limit', 10)
        
        print(f"[DEBUG] Search request - target_id={target_id}, query='{query_text}'")
        
        conn = get_conn()
        target_vec = None

        if target_id is not None:
            try:
                emb_res = conn.execute(f"MATCH (c:Company) WHERE c.id = {target_id} RETURN c.embedding")
                if emb_res.has_next():
                    target_vec = np.array(emb_res.get_next()[0])
            except Exception as e:
                return jsonify({"error": str(e)}), 500
                
        elif query_text:
            try:
                output = embed.text(
                    texts=[query_text], 
                    model='nomic-embed-text-v1.5', 
                    task_type='search_query', 
                    inference_mode="local", 
                    device="cuda"
                )
                target_vec = np.array(output['embeddings'][0])
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        if target_vec is None:
            return jsonify({"results": []})

        try:
            res = conn.execute("MATCH (c:Company) RETURN c.id, c.name, c.description, c.status, c.location, c.tags, c.embedding")
            results = []
            norm_target = np.linalg.norm(target_vec)
            
            while res.has_next():
                row = res.get_next()
                cid, name, desc, status, loc, tags, emb = row
                
                if target_id and cid == target_id: continue
                
                vec = np.array(emb)
                if norm_target == 0 or np.linalg.norm(vec) == 0:
                    sim = 0
                else:
                    sim = np.dot(target_vec, vec) / (norm_target * np.linalg.norm(vec))
                
                results.append({
                    "id": cid, "name": name, "description": desc,
                    "status": status, "location": loc, "tags": tags if tags else [],
                    "score": float(sim)
                })
                
            results.sort(key=lambda x: x['score'], reverse=True)
            print(f"[DEBUG] Search returned {len(results)} results.")
            return jsonify({"results": results[:limit]})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/update', methods=['POST'])
def update_company():
    try:
        data = request.json
        node_id = data.get('id')
        status = data.get('status')
        tags = data.get('tags')
        
        if node_id is None: return jsonify({"error": "Missing ID"}), 400
        
        conn = get_conn()
        if status:
            conn.execute(f"MATCH (c:Company) WHERE c.id = {node_id} SET c.status = '{status}'")
        if tags is not None:
            tag_str = "[" + ", ".join([f"'{t}'" for t in tags]) + "]"
            conn.execute(f"MATCH (c:Company) WHERE c.id = {node_id} SET c.tags = {tag_str}")
        return jsonify({"success": True})
    except Exception as e:
        print(f"[ERROR] update_company failed: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("[System] Starting Flask Server...")
    app.run(debug=True, port=5000, use_reloader=False)