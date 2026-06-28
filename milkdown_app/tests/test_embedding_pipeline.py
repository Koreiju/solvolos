import pytest
import numpy as np

def test_umap_small_manifold_fallback():
    """
    TDD-EMB-01: If raw_vectors is size < 15, sequence MUST adjust n_neighbors.
    Failing TDD asserts UMAP crash on small manifold samples.
    """
    
    # Mocking a tiny knowledge graph state (e.g. fresh database)
    small_vectors = np.random.rand(5, 768)
    
    try:
        from milkdown_app.app import project_embeddings
        
        # This will crash if UMAP's default n_neighbors (usually 15) is not clamped
        # based on the size of the input vectors.
        coords, colors = project_embeddings(small_vectors)
        
        assert coords.shape == (5, 3), "Coordinates output shape mismatch"
        assert colors.shape == (5, 3), "Colors output shape mismatch"
    except ImportError:
        pytest.fail("project_embeddings not yet implemented in milkdown_app.app")
    except Exception as e:
        pytest.fail(f"UMAP projection crashed on small manifold: {str(e)}")
