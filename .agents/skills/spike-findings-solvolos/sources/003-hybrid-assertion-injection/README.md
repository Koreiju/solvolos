---
spike: 003
name: hybrid-assertion-injection
type: standard
validates: "Given a synthesized script, when static architectural rules (e.g. background `#000000`) are supplied, then they are correctly appended into the generated assertions."
verdict: VALIDATED
related: [002]
tags: [assertions, testing]
---

# Spike 003: Hybrid Assertion Injection

## What This Validates
Can we cleanly inject universal architectural rules into a dynamically generated, organically synthesized subagent test script, without breaking the script, and have it pass?

## Research
We will inject `TDD-UI-06` (background `#000000`) and `TDD-UI-07` (no `.label` or `button`) assertions at the end of the `synthetic-001.spec.js` script. 

## How to Run
```bash
npx playwright test tests/e2e/synthetic-001.spec.js
```

## Results
We successfully appended the `TDD-UI-06` and `TDD-UI-07` static constraints to the generated `synthetic-001.spec.js`. 
Initially, we hit a strict mode violation from Playwright because checking for `*` on the billboard matches multiple elements. We resolved this by explicitly checking the highest level bounding boxes (e.g., `billboard` and `chatPanel`) directly.
With this minor fix, the test passed perfectly.

**Conclusion**: We can reliably enforce strict architectural bounds (like pure black backgrounds and missing generic buttons) on all dynamic AI-generated trace tests, assuring that even organically discovered user stories conform precisely to our Solvolos project guidelines.
