import pytest
import json
import numpy as np
from milkdown_app.app import app, parse_markdown_to_chunks, project_embeddings

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_parse_markdown_to_chunks():
    md_text = "# Header 1\nSome paragraph text.\n## Header 2\n- List item 1\n- List item 2"
    chunks = parse_markdown_to_chunks(md_text)
    
    assert len(chunks) == 4, "Expected 4 chunks (H1, Paragraph, H2, List)"
    
    assert chunks[0]["type"] == "heading"
    assert chunks[0]["content"] == "# Header 1"
    
    assert chunks[1]["type"] == "paragraph"
    assert chunks[1]["content"] == "Some paragraph text."
    assert chunks[1]["lineage"] == "# Header 1"
    
    assert chunks[2]["type"] == "heading"
    assert chunks[2]["content"] == "## Header 2"
    
    assert chunks[3]["type"] == "list"
    assert chunks[3]["content"] == "- List item 1\n- List item 2"
    assert chunks[3]["lineage"] == "# Header 1\n## Header 2"

def test_sse_chat_stream_contract(client, monkeypatch):
    # Mock the LLM stream to yield a few predictable tokens
    def mock_generate(*args, **kwargs):
        yield "Hello "
        yield "world!"
        
    class MockLLM:
        def generate(self, *args, **kwargs):
            return mock_generate(*args, **kwargs)
            
    import milkdown_app.app as myapp
    myapp.llm = MockLLM()
    
    response = client.post('/api/chat/stream', json={"message": "hello", "node_id": "test_node"})
    
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    assert response.content_type.startswith("text/event-stream"), "Expected text/event-stream content type"
    
    content = response.get_data(as_text=True)
    assert "data: " in content
    
    # Check if a chunk type event was emitted
    assert '"type": "token"' in content or '"type": "graph_update"' in content
