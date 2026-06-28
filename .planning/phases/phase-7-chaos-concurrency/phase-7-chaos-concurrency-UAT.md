# Phase 7: Chaos Concurrency & Animation Verification - UAT Checklist

## Architecture Constraints

- [ ] pending: **UAT-ISO-03**: Integration tests MUST assert the backend sequences/queues concurrent inbound debounce updates from the same node ID, preventing Kuzu transaction locks during fast typing (Maps to `TDD-ISO-03`).
- [ ] pending: **UAT-PHY-04**: If an SSE DOM resize occurs while a billboard is tweening back to its 3D tether, the `updateBillboardPosition` MUST smoothly interpolate the new DOM height without stuttering the camera vector (Maps to `TDD-PHY-04`).
- [ ] pending: **UAT-PHY-05**: If a new embedding causes a global UMAP manifold recalculation, the physics engine MUST apply a maximum velocity dampener (`v.clampLength(max)`) to prevent nodes from exploding across the screen (Maps to `TDD-PHY-05`).
