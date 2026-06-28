import re

def parse_markdown_to_chunks(md_text):
    chunks = []
    lines = md_text.split('\n')
    
    current_chunk_type = None
    current_lines = []
    
    def push_chunk():
        nonlocal current_chunk_type, current_lines
        if current_lines:
            content = '\n'.join(current_lines).strip()
            if content:
                if not current_chunk_type:
                    if content.startswith('#'):
                        current_chunk_type = 'heading'
                    elif content.startswith('- ') or content.startswith('* ') or re.match(r'^\d+\.\s', content):
                        current_chunk_type = 'list'
                    elif '|' in content and '-' in content:
                        current_chunk_type = 'table'
                    else:
                        current_chunk_type = 'paragraph'
                
                chunks.append({"type": current_chunk_type, "content": content})
            
            current_lines = []
            current_chunk_type = None

    in_code_block = False
    
    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('```'):
            if in_code_block:
                current_lines.append(line)
                current_chunk_type = 'code'
                push_chunk()
                in_code_block = False
            else:
                push_chunk()
                in_code_block = True
                current_lines.append(line)
            continue
            
        if in_code_block:
            current_lines.append(line)
            continue
            
        if not stripped:
            push_chunk()
            continue
            
        current_lines.append(line)
        
    push_chunk()
    return chunks

test_md = """# This is a header

This is a paragraph with a
newline inside.

```python
def foo():
    print("hello")

    print("blank line above!")
```

| col1 | col2 |
|---|---|
| val1 | val2 |

- list item 1
- list item 2
"""

for c in parse_markdown_to_chunks(test_md):
    print(c["type"], repr(c["content"]))
