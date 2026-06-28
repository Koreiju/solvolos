import pytest
from app import calculate_diffuse_layout

def test_diffuse_fallback_tdd_dif_01():
    """
    TDD-DIF-01: Stream an AI markdown header that matches no existing chunk type 
    in the AST; test MUST assert it defaults safely to the bottom of the document 
    rather than throwing a parsing error.
    """
    chunks = [
        {"id": "1", "type": "paragraph", "content": "Paragraph text", "emb": [0.1, 0.2]},
        {"id": "2", "type": "heading", "content": "# Header", "emb": [0.9, 0.1]},
        {"id": "3", "type": "bizarre-type", "content": "Unknown chunk", "emb": [0.5, 0.5]},
    ]
    
    # Run the diffuse layout calculator
    content, layout = calculate_diffuse_layout(chunks)
    
    # Assert 'bizarre-type' is in the layout
    assert "bizarre-type" in layout
    
    # Assert it appears at the very end of the sorted output (fallback to 99)
    # The order should be heading (0), paragraph (1), bizarre-type (99).
    # In the content string, "Unknown chunk" should be the last thing.
    assert content.endswith("Unknown chunk")
