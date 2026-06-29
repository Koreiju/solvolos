---
spike: 007
name: milkdown-ast-resilience
type: standard
validates: "Given a Playwright synthetic test, When the chat panel is force-fed broken markdown, Then the Milkdown AST streaming parser gracefully handles it."
verdict: VALIDATED
tags: [milkdown, resilience]
---

# Spike 007: milkdown-ast-resilience

## What This Validates
Since our app uses Milkdown via an AST replacement (`replaceAll`) for streaming LLM chat, we need to ensure the ProseMirror/Milkdown editor does not crash if the stream accidentally yields half-finished codeblocks, mismatched brackets, or weird chunking bugs.

## How to Run
```bash
npx playwright test tests/e2e/milkdown-resilience.spec.js
```

## Results
Spike validated successfully. The Milkdown editor does not crash when parsing severely broken markdown (unclosed codeblocks, unbalanced asterisks, missing link braces) streamed token-by-token. 

**Gotchas Discovered:**
- By design, Milkdown's `replaceAll` action re-parses the AST gracefully handling malformed syntax by treating it as raw text until it successfully closes. 
- The `.chat-panel` locator must be used to input text as it binds the `Enter` key event for `fetch`. The `.ProseMirror` element is read-only displaying the rendered AST stream.
