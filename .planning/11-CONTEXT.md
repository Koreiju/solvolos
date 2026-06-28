# Phase 11: Real-Time Vector Movement - Context

**Gathered:** 2026-06-27
**Status:** Ready for planning
**Mode:** Auto-generated (Autonomous Mode)

<domain>
## Phase Boundary

**Goal:** Interpolate 3D node coordinates dynamically as context sizes change, applying repelling physics between grouped chunks (REQ-2.0.6).
</domain>

<decisions>
## Implementation Decisions

### Agent Discretion
- **Frontend Physics Engine**: Instead of locking chunk meshes to exact UMAP coordinates sent by the backend, `projector.js` will store the backend coordinates as `targetPos`. In the `animate()` loop, we will use Euler integration to smoothly interpolate the chunk mesh toward its target, while simultaneously applying a repelling force between sibling chunks (chunks with the same `parent_id`).
- **Dynamic Floating**: This guarantees that when a dense cluster of chunks is generated around a single global node, they won't clip or overlap statically. They will physically push each other away in real-time until they reach an equilibrium orbit, producing the "Repelling Clusters" aesthetic requested in US-2.0.3.
</decisions>
