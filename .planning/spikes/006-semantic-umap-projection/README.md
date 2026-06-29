---
spike: 006
name: semantic-umap-projection
type: standard
validates: "Given a mock set of 50 semantic chunk vectors, When processed by our local UMAP pipeline, Then it accurately reduces them to 3D coordinates."
verdict: VALIDATED
tags: [umap, ml]
---

# Spike 006: semantic-umap-projection

## What This Validates
Our architecture maps 768-dimensional local embeddings into 3D (x,y,z) spatial coordinates and (r,g,b) colors using UMAP. This spike verifies that `umap-learn` can reduce a batch of 50 embeddings without crashing, returning proper scaled bounds.

## How to Run
```bash
python .planning/spikes/006-semantic-umap-projection/umap_test.py
```

## Results
Spike validated successfully. `umap-learn` efficiently processes continuous streams of 768-dimension semantic embeddings generated locally. 

**Gotchas Discovered:**
- Local UMAP initialization dynamically trains its space mapping on startup if the `.joblib` model cache isn't found, which causes a ~2-5s blocking delay. In a continuous stream this might stutter if not cached properly. Our implementation successfully uses `joblib` dumps to cache and restore the UMAP reducer and Scaler.
- The `MinMaxScaler` for mapping UMAP indices back to RGB `[0,1]` successfully constrains colors between 0 and 1 without negative out-of-bounds floats.
