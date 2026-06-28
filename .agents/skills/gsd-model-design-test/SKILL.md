---
name: gsd-model-design-test
description: >
  Applies a model-design-test approach to code architectures and algorithms in UML and pseudocode.
  Predicates the full gsd-autonomous run by transforming design features into modeled architectural requirements.
---

# gsd-model-design-test

## Overview
This skill formalizes the design and architectural phase of a `gsd-autonomous` or development run. Before writing actual code, this skill mandates the creation of strict architectural models in UML (Mermaid) and algorithmic pseudocode based on the project's design features and `.planning` requirements. It transforms abstract requirements into a concrete modeling layer that subsequent development phases can test against.

## Dependencies
- `gsd-autonomous` (runs after this skill to implement the designed models).
- `gsd-plan-phase` (this skill enhances or precedes the planning phase).

## Quick Start
```bash
# Ask the agent to use this skill
"Run gsd-model-design-test on the new Diffuse Semantic Rendering feature"
```

## Workflow

### 1. Ingest Design Features
- Read `.planning/REQUIREMENTS.md`, `.planning/PROJECT.md`, and any feature-specific artifacts (like `UI-SPEC.md` or `AI-SPEC.md`).
- Identify the core architectural components affected by the new feature or phase.

### 2. Generate UML Models
- Using the `architecture/` directory as a frame of reference, create or update the relevant `<DIAGRAM>.md` files.
- You **MUST** generate both **Object Diagrams** (for architectural modeling) and **Sequence Diagrams** (for function design).
- You **MUST** use Mermaid (`mermaid`) blocks for these models.
- Include explicit points and notes within these UML diagrams that mention test cases which coincide between the user stories and the object model, particularly those that may arise through processing along the sequence diagrams.
- **MAIN.md**: Must contain a strictly formatted document containing:
  1. The high-level **Object Model**.
  2. **User Activities**.
  3. **User Stories**.
  4. A detailed **natural language description** of the expected experience in the 3D GUI, strictly relating to the interface itself.
- **Module Diagrams**: Provide detailed UML diagrams for the specific components being changed.
- If contradictions exist between existing architecture and new requirements, use GitHub `> [!WARNING]` blocks in the models to surface them, or attempt to resolve them using constraints found in `PROJECT.md`.

### 3. Identify Hidden Module-Level Constraints (Mental Walkthrough)
- Iterate over the current `architecture/MAIN.md` and module-specific architectural documentation.
- Mentally walk through the complete code solutions in their full form (e.g., API boundaries, object models, library/package usage, and frontend-backend compatibility).
- Reflect on the "play-loop" of how these modules interact across boundaries (e.g., UI interaction states vs incoming network streams, database write-locks across concurrent agents).
- Identify "hidden test cases" that arise from these module-level intersections (race conditions, state overlaps, buffering needs, projection drifts) that might not be captured in high-level UATs.
- Formally capture these hidden test cases as explicit TDD bounds into the architecture sequence diagrams.

### 4. Generate Pseudocode
- For complex algorithmic changes (like context engine token budgeting or 3D coordinate normalization physics), write explicit pseudocode inside the module `<DIAGRAM>.md` or in the specific `PLAN.md`.
- **Constraint**: Only use UML and pseudocode. Do not write full language-specific implementations during this phase.

### 5. Transform to Planning Artifacts
- The sequence diagrams and object models must be used alongside the natural language interactions (from MAIN.md) to explicitly clarify **all possible test cases**.
- These test cases **MUST** be designed to fail in the initial Test-Driven Development (TDD) phase.
- Refactor `ROADMAP.md` and update any other `.planning/` GSD docs to explicitly build out these designed-to-fail test cases.
- Ensure the plan inherently mandates test-driven validation (e.g., Playwright automation, AI agent verification) of these architectural bounds.

## Common Mistakes
- **Writing full code instead of pseudocode:** This phase is strictly for design and architectural modeling. Keep it abstract.
- **Skipping the MAIN.md updates:** Ensure the high-level system view remains the primary frame of reference by updating `MAIN.md` first before deep-diving into specific module diagrams.
- **Ignoring existing architecture:** Always view the existing `architecture/` files before proposing new topologies.
