import sys
import os
import numpy as np

# Ensure solvolos root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Mock GPT4All so we don't load the massive LLM into VRAM just to test UMAP
import gpt4all
class MockGPT4All:
    def __init__(self, *args, **kwargs):
        pass
    def generate(self, *args, **kwargs):
        yield "mock"
gpt4all.GPT4All = MockGPT4All

import ml

def main():
    print("Testing Semantic UMAP Projection...")
    
    # Initialize ML (This should load/initialize UMAP and scaler)
    ml.init_ml()
    
    print("\nGenerating 50 mock semantic chunk vectors (768 dimensions)...")
    mock_vectors = np.random.rand(50, 768).tolist()
    
    projected_coords = []
    projected_colors = []
    
    print("Projecting vectors via UMAP...")
    for idx, vec in enumerate(mock_vectors):
        coords, colors = ml.project_embedding(vec)
        
        # Verify formats
        assert len(coords) == 3, f"Expected 3 spatial coordinates, got {len(coords)}"
        assert len(colors) == 3, f"Expected 3 color channels, got {len(colors)}"
        
        # Verify color bounds (0 to 1)
        for c in colors:
            assert 0.0 <= c <= 1.0, f"Color {c} is out of bounds [0.0, 1.0]"
            
        projected_coords.append(coords)
        projected_colors.append(colors)
        
        if idx % 10 == 0:
            print(f"Projected {idx+1}/50...")

    print("\nSUCCESS: All 50 chunk vectors were successfully projected into 3D space with valid RGB colors.")
    print("Sample outputs:")
    for i in range(3):
        print(f"  Vector {i}: Coords={projected_coords[i]} RGB={projected_colors[i]}")

if __name__ == "__main__":
    main()
