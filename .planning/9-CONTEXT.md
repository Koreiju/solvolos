# Phase 9: Knowledge Graph Aesthetics - Context

**Gathered:** 2026-06-27
**Status:** Ready for planning
**Mode:** Auto-generated (Autonomous Mode)

<domain>
## Phase Boundary

**Goal:** Scale global nodes 2x and render glowing cylinders for all KuzuDB edges (`REFERENCES`, `FOLLOWS`, `REPLIES_TO`) (REQ-2.0.5).
</domain>

<decisions>
## Implementation Decisions

### Agent Discretion
- **Node Scaling**: We will scale `GlobalNode` Icosahedron radius from `0.6` to `1.2` in `projector.js` (both in `loadGraph` and `addStreamingNode`).
- **Edge Rendering**: We will replace the flat `THREE.Line` with `THREE.CylinderGeometry`. We will use a `THREE.MeshPhongMaterial` with dynamic emissive coloring based on edge type:
  - `REFERENCES`: Yellow
  - `FOLLOWS`: Blue
  - `REPLIES_TO`: Green
  - `PART_OF`: Dim Gray (for chunks)
- **Backend Query Update**: We will update `app.py`'s `/api/nodes` endpoint to dynamically match and return `REFERENCES`, `FOLLOWS`, and `REPLIES_TO` edge types from KuzuDB instead of just hardcoded `REFERENCES`.
</decisions>
