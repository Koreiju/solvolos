# Phase 8: Fly-to-View Mechanics - Context

**Gathered:** 2026-06-27
**Status:** Ready for planning
**Mode:** Auto-generated (Autonomous Mode)

<domain>
## Phase Boundary

**Goal:** Implement left-click animation to a draggable 2D plane and right-click tether unsticking (REQ-2.0.3, REQ-2.0.4).
</domain>

<decisions>
## Implementation Decisions

### Agent Discretion
- **Fly-to-View**: When a node is left-clicked (locked), the `billboardApp.showForNode` will invoke a new `flyToView()` mechanic. This will inject a temporary CSS transition on `top/left`, detach the billboard from the 3D tether tracking (`isDetached = true`), and animate it to a readable anchored position (e.g., `5vw`, `10vh`).
- **Unstick & Close**: We will intercept the right-click (`contextmenu`) event on the billboard element. If it's currently detached (flown to view or dragged), right-clicking triggers `returnToTether()`, re-enabling 3D tracking with a smooth return animation. If it's already tethered, right-clicking completely closes the panel.
</decisions>
