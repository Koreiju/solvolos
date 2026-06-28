from flask import Flask, render_template, jsonify, request
from db import get_connection, init_schema, insert_chunk_safely, get_subtree_details
import math
import threading

class ContextCacheManager:
    _caches = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_cache(cls, session_id):
        with cls._lock:
            if session_id not in cls._caches:
                cls._caches[session_id] = {}
            return cls._caches[session_id]
            
    @classmethod
    def persist_local_kv(cls, session_id, key, value):
        with cls._lock:
            if session_id not in cls._caches:
                cls._caches[session_id] = {}
            cls._caches[session_id][key] = value

class DocumentGrouper:
    @staticmethod
    def enforce_token_budget(chunks, limit=256):
        doc_groups = {}
        current_tokens = 0
        final_chunks = []
        for c in chunks:
            # Simple token estimation: 1.3 tokens per word
            tokens = len(c.get("content", "").split()) * 1.3
            if current_tokens + tokens > limit:
                break
            
            title = c.get("doc_title", "Unknown")
            if title not in doc_groups: 
                doc_groups[title] = []
            
            doc_groups[title].append(c)
            final_chunks.append(c)
            current_tokens += tokens
            
        return doc_groups

def build_prompt_with_context(message, chunks):
    doc_groups = DocumentGrouper.enforce_token_budget(chunks, limit=256)
    
    context_text = ""
    for title, chunks_list in doc_groups.items():
        context_text += f"\n--- From Document: {title} ---\n"
        for c in chunks_list:
            lineage = c.get("lineage")
            if lineage: 
                context_text += f"{lineage}\n"
            context_text += f"{c.get('content', '')}\n"
            
    return context_text

def calculate_diffuse_layout(all_session_chunks):
    type_groups = {}
    for sc in all_session_chunks:
        ctype = sc.get("type", "unknown")
        if ctype not in type_groups: 
            type_groups[ctype] = []
        type_groups[ctype].append(sc)
        
    for ctype, items in type_groups.items():
        if not items: continue
        
        if all("emb" in item and item["emb"] for item in items):
            emb_len = len(items[0]["emb"])
            centroid = [0.0] * emb_len
            for item in items:
                for i in range(emb_len):
                    centroid[i] += item["emb"][i]
            centroid = [x / len(items) for x in centroid]
            
            def norm(vec):
                return math.sqrt(sum(x*x for x in vec))
            
            norm_centroid = norm(centroid)
            
            for item in items:
                norm_item = norm(item["emb"])
                if norm_centroid == 0 or norm_item == 0:
                    item["score"] = 0
                else:
                    dot = sum(c*v for c, v in zip(centroid, item["emb"]))
                    item["score"] = dot / (norm_centroid * norm_item)
        else:
            for item in items:
                item["score"] = 0
                
    type_order = ['heading', 'paragraph', 'list', 'code', 'table']
    sorted_types = sorted(type_groups.keys(), key=lambda k: type_order.index(k) if k in type_order else 99)
    
    diffuse_layout = {}
    diffused_parts = []
    
    for ctype in sorted_types:
        items = type_groups[ctype]
        items.sort(key=lambda x: x.get("score", 0), reverse=True)
        diffuse_layout[ctype] = [item["id"] for item in items]
        
        for item in items:
            diffused_parts.append(item.get("content", ""))
            
    diffused_content = "\n\n".join(diffused_parts)
    return diffused_content, diffuse_layout

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health():
    try:
        conn = get_connection()
        return jsonify({"status": "ok", "db_connected": True})
    except Exception as e:
        return jsonify({"status": "error", "db_connected": False, "error": str(e)}), 500

@app.route('/api/sync', methods=['POST'])
def sync():
    payload = request.json
    chunk_id = payload.get("id")
    text = payload.get("text")
    insert_chunk_safely(chunk_id, text)
    return jsonify({"status": "success", "id": chunk_id})

@app.route('/api/details/<global_id>', methods=['GET'])
def details(global_id):
    try:
        data = get_subtree_details(global_id)
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"results": []})
    try:
        from db import get_connection
        conn = get_connection()
        result = conn.execute(
            "MATCH (c:ChunkNode) WHERE c.text CONTAINS $q RETURN c.id, c.text LIMIT 10",
            {"q": query}
        )
        results = []
        while result.has_next():
            row = result.get_next()
            results.append({"id": row[0], "text": row[1]})
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"results": []})

import time
import json
from flask import Response

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    payload = request.json
    node_id = payload.get("id")
    message = payload.get("message")
    
    def generate():
        import ml
        

        for token in ml.generate_stream(message):
            yield json.dumps({"text": token}) + "\n"
            
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    # Initialize DB schema on startup
    init_schema()
    import ml
    ml.init_ml()
    app.run(port=5000, debug=True, use_reloader=False)
