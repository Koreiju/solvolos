# Phase 3: Dual Intellisense UI - Context

**Gathered:** 2026-06-27
**Status:** Ready for planning
**Mode:** Auto-generated (Autonomous Mode)

<domain>
## Phase Boundary

**Goal:** Implement only `\` semantic vector searching with `🔮` visual badges (REQ-1.2.1).
</domain>

<decisions>
## Implementation Decisions

### Agent Discretion
- **UI Mechanism**: Since we cannot render HTML badges directly inside a standard `<input type="text">`, we will convert the chat input area into a standard Tag-Input pattern. We will add a `#badges-container` `div` next to the input.
- **Trigger**: The intellisense popup will be restricted to trigger only on `\` as per the Phase 3 goal, dropping the `/` trigger.
- **Selection**: Selecting an item from the popup will remove the query string from the input box, add the item's ID to the `contextLinks` set, and visually append a DOM badge (`<span class="badge">🔮 Title</span>`) into the `#badges-container`.
</decisions>
