import os
import threading
import numpy as np
import joblib
from gpt4all import GPT4All
from nomic import embed
import umap
from sklearn.preprocessing import StandardScaler, MinMaxScaler

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UMAP_MODEL_PATH = os.path.join(APP_ROOT, 'umap_reducer.joblib')
SCALER_MODEL_PATH = os.path.join(APP_ROOT, 'scaler.joblib')

llm = None
umap_reducer = None
scaler = None
embed_lock = threading.Lock()
llm_lock = threading.Lock()

def init_ml():
    global llm, umap_reducer, scaler
    print("[System] Initializing GPT4All Model: Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf")
    try:
        # Load Hermes 2 DPO
        llm = GPT4All("Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf", device="gpu", verbose=False)
        print("[System] LLM Initialized successfully.")
    except Exception as e:
        print(f"[ERROR] LLM Initialization failed: {e}")

    if os.path.exists(UMAP_MODEL_PATH) and os.path.exists(SCALER_MODEL_PATH):
        try:
            umap_reducer = joblib.load(UMAP_MODEL_PATH)
            scaler = joblib.load(SCALER_MODEL_PATH)
            print("[System] Loaded UMAP and Scaler.")
        except Exception as e:
            print(f"[WARN] Failed to load ML models: {e}")

    if umap_reducer is None or scaler is None:
        print("[System] Initializing fresh UMAP and Scaler.")
        umap_reducer = umap.UMAP(n_components=6, n_neighbors=15, min_dist=0.1, metric='cosine')
        scaler = StandardScaler()
        dummy_data = np.random.rand(20, 768)
        scaler.fit(dummy_data)
        umap_reducer.fit(scaler.transform(dummy_data))
        joblib.dump(scaler, SCALER_MODEL_PATH)
        joblib.dump(umap_reducer, UMAP_MODEL_PATH)

def embed_text(text):
    if not text:
        return np.zeros(768).tolist()
    try:
        with embed_lock:
            # We use nomic local embedding which requires downloading model once.
            res = embed.text(texts=[text], model='nomic-embed-text-v1.5', task_type='search_document', inference_mode="local", device="cpu")
            return res['embeddings'][0]
    except Exception as e:
        print(f"[ERROR] Embedding failed: {e}")
        return np.random.rand(768).tolist()

def project_embedding(emb_list):
    """Expects a 1D list of length 768, returns (x, y, z), (r, g, b)"""
    if not emb_list or len(emb_list) == 0:
        return (0.0, 0.0, 0.0), (0.5, 0.5, 0.5)
    
    emb_scaled = scaler.transform([emb_list])
    proj = umap_reducer.transform(emb_scaled)
    coords = proj[0, 0:3]
    colors_raw = proj[:, 3:6]
    color_scaler = MinMaxScaler(feature_range=(0, 1))
    colors_raw = np.vstack([colors_raw, [0,0,0], [1,1,1]]) # Dummy bounds for scaler
    color_scaler.fit(colors_raw)
    colors = color_scaler.transform([proj[0, 3:6]])
    
    return (float(coords[0]), float(coords[1]), float(coords[2])), (float(colors[0][0]), float(colors[0][1]), float(colors[0][2]))

def generate_stream(prompt):
    if not llm:
        yield "LLM Not Loaded"
        return
        
    system_prompt = "You are a helpful AI assistant. Answer accurately."
    full_prompt = f"### System:\n{system_prompt}\n\n### User:\n{prompt}\n\n### Response:\n"
    
    with llm_lock:
        for token in llm.generate(full_prompt, streaming=True, max_tokens=150):
            yield token
