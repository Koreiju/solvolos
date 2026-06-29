# Hybrid Assertion Strategy for AI Tests

**Date:** 2026-06-28
**Context:** Exploring how to generate automated E2E tests from AI exploratory testing in the Solvolos App.

## Concept

When using an AI subagent to explore a complex application organically, generating deterministic assertions is challenging due to the dynamic nature of the DOM (e.g., Milkdown AST updates, 3D CSS3DObject transformations). 

To resolve this, we adopt a **Hybrid Assertion Strategy** combining two discrete tiers of assertions within generated Playwright scripts:

### 1. Static Architectural Constraints (Non-Negotiable)
These are injected unconditionally into every generated test suite. The AI does not infer these; it simply inherits them from the `architecture/MAIN.md` boundaries.
- **Example:** Ensure no `<button>` or `.label` elements are spawned (`TDD-UI-07`).
- **Example:** Background color of billboard classes must be strictly `#000000` (`TDD-UI-06`).
- **Value:** Prevents AI regressions on universal design/system constraints regardless of the specific user story it tests.

### 2. Dynamic DOM-Inferred Assertions (Organic)
These are generated dynamically by the AI based on snapshots of the DOM state during its play-through.
- **Example:** After the AI clicks a retrieval item, it observes the token `🔮` appear in `.chat-panel`. It immediately generates `expect(chatPanel).toContainText('🔮')`.
- **Value:** Contextually validates the specific user story and interaction loop the AI is executing, ensuring the logic tree executes fully.

## Next Steps
This note serves as the foundation for the "AI-Driven Playwright Codegen Engine" seed.
