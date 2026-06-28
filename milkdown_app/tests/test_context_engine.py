import pytest

def test_context_budget_truncation():
    """
    TDD-CTX-01: Force a 500-token semantic retrieval payload; 
    test MUST assert that the context grouper violently truncates 
    exactly at the 256-token limit boundary.
    """
    # Assuming app.py will have `enforce_token_budget(chunks, limit)`
    # This will fail until the function exists and correctly slices the budget.
    
    mock_chunks = [
        {"content": "word " * 100, "doc_title": "Doc1", "lineage": "# Title"}, # ~130 tokens
        {"content": "word " * 100, "doc_title": "Doc1", "lineage": "# Title"}, # ~130 tokens
        {"content": "word " * 100, "doc_title": "Doc2", "lineage": "# Title"}, # ~130 tokens
        {"content": "word " * 100, "doc_title": "Doc3", "lineage": "# Title"}, # ~130 tokens
    ]
    
    try:
        from milkdown_app.app import enforce_token_budget
        budgeted = enforce_token_budget(mock_chunks, limit=256)
        
        # Calculate resulting tokens
        total_tokens = sum([len(c["content"].split()) * 1.3 for c in budgeted])
        
        assert total_tokens <= 256, f"Context engine leaked tokens: {total_tokens} > 256"
        assert len(budgeted) < len(mock_chunks), "Context engine failed to truncate any chunks"
    except ImportError:
        pytest.fail("enforce_token_budget not yet implemented in milkdown_app.app")
