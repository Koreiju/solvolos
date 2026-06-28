# Phase 4 Physics & UI UAT

## Frontend TDD Constraints

- [ ] pending: **UAT-PHY-01**: Dispatch two chunks at the exact same vector coordinate (0,0,0); Physics engine MUST apply exact spring repulsion preventing collision inside the 2.25 squared radius to avoid NaN (Maps to `TDD-PHY-01` in `physics.test.js`).
- [ ] pending: **UAT-INT-01**: Trigger a raycast intersection event while `lockedId` is active; Interaction layer MUST ignore hover states to prevent state overwriting (Maps to `TDD-INT-01` in `interaction.test.js`).
- [ ] pending: **UAT-PHY-02**: Trigger a browser resize event while a billboard is pinned; 3D Projector MUST instantly recalculate projection matrix to prevent visual drift (Maps to `TDD-PHY-02`).
- [ ] pending: **UAT-PHY-03**: Physics engine MUST verify the 6D UMAP (3 spatial, 3 HSV) continuously rotates the text-highlight colors at the exact speed defined in the legacy tracker (Maps to `TDD-PHY-03`).
- [ ] pending: **UAT-INT-02**: Simulate an active cursor focus event while an AI SSE chunk arrives; Milkdown editor MUST buffer the AST injection to prevent destroying user keystrokes (Maps to `TDD-INT-02`).
