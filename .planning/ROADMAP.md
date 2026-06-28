# Milestone Roadmap (Refactored for model-design-test)

## Execution Protocol
All upcoming phases will be executed via `gsd-autonomous`. Before any code is written, the `gsd-model-design-test` skill **must** be invoked to validate the phase requirements against the object models in `architecture/MAIN.md`. All automated playwright tests and AI verification must pass against these architectural bounds.

**Important:** Please see `architecture/REQUIREMENTS.md` for the 11 verbatim statements of objective facts detailing the mandatory UX and system activity behavior.

---

## Phase 1: Baseline Full-Stack Scaffolding & CI Integration
- **Goal:** Initialize the raw repository structure, connect Flask to KuzuDB, serve a blank `index.html` with vanilla JS stubs, and establish the automated testing harness.
- **Pre-requisite:** Architecture and TDD boundaries defined.
- **Requirements Mapped:** Environment Setup.
- **Success Criteria:**
  1. Flask serves `index.html` and responds to `/api/health`.
  2. KuzuDB initializes a local file-based graph safely.
  3. Playwright and Pytest harnesses are configured and can pass a basic integration ping.
- **TDD Designed-To-Fail Cases:**
  - *TDD-BASE-01*: Playwright MUST successfully boot the local Flask server natively, load `index.html`, and assert a 200 OK status without throwing unhandled JS console errors.
  - *TDD-BASE-02*: Pytest MUST initialize a temporary KuzuDB instance on disk, write a dummy node, and cleanly tear down the file lock.

## Phase 2: Token-Budgeted Context Engine
- **Goal:** Implement and verify the explicit token limits and semantic chunk ranking.
- **Pre-requisite:** `gsd-model-design-test` validates against `architecture/ContextEngine.md`.
- **Requirements Mapped:** REQ-1.2.1, REQ-1.2.2, REQ-1.2.3, REQ-1.2.4
- **Success Criteria:**
  1. Semantic retrieval strictly stops at the defined token budget (e.g. 256).
  2. Selected chunks are grouped by parent documents with injected headers.
  3. Playwright/Agent automation verifies LLM payload size bounds.
- **TDD Designed-To-Fail Cases:** 
  - *TDD-CTX-01*: Force a 500-token semantic retrieval payload; test MUST assert that the context grouper violently truncates exactly at the 256-token limit boundary.
  - *TDD-KUZ-02*: Dispatch two asynchronous chunk-creation payloads simultaneously; test MUST assert Kuzu successfully records both nodes without throwing a write-lock or cursor concurrency error.

## Phase 3: Diffuse Semantic Rendering
- **Goal:** Render LLM streams non-chronologically into existing documents based on semantic similarity.
- **Pre-requisite:** `gsd-model-design-test` validates against `architecture/MilkdownBillboard.md`.
- **Requirements Mapped:** REQ-1.3.1, REQ-1.3.2
- **Success Criteria:**
  1. AI text dynamically interpolates into the `MilkdownEditor` based on matching `data-chunk-type`.
  2. Automation verifies that new `# headers` are clustered next to semantically identical `# headers`.
- **TDD Designed-To-Fail Cases:** 
  - *TDD-UI-01*: Playwright MUST verify double-clicking the background spawns a pinned 2D Milkdown editor with no 3D sphere primitive.
  - *TDD-UI-02*: Playwright MUST verify instant markdown AST rendering of nested lists/tables upon keystrokes.
  - *TDD-UI-03*: Playwright MUST verify the chat panel adaptively grows on focus and collapses to exactly 3 lines on blur.
  - *TDD-DIF-01*: Stream an AI markdown header that matches no existing chunk type in the AST; test MUST assert it defaults safely to the bottom of the document rather than throwing a parsing error.
  - *TDD-DIF-02*: Pass a deliberately fractured JSON string to the SSE processor; test MUST assert the parser buffers the string rather than crashing with a `SyntaxError`.

## Phase 4: Projective Physics & Topological Normalization
- **Goal:** Implement the physical fly-to-view UI mechanics and 3D coordinate interpolations.
- **Pre-requisite:** `gsd-model-design-test` validates against `architecture/3DProjector.md`.
- **Requirements Mapped:** REQ-2.0.1, REQ-2.0.2, REQ-2.0.3, REQ-2.1.1
- **Success Criteria:**
  1. Left-clicking a billboard brings it to fixed 1/6th screen view; right clicking returns it.
  2. New global nodes stream in with smooth physics interpolation, verified by coordinate polling tests.
- **TDD Designed-To-Fail Cases:** 
  - *TDD-PHY-01*: Dispatch a global node event placing two chunks in the exact same vector coordinate; test MUST assert the physics engine applies exact spring repulsion preventing collision inside the 2.25 squared radius.
  - *TDD-PHY-02*: Trigger a `resize` DOM event while `lockedId` is active; test MUST assert the 3D camera projection vector is instantly recalculated.
  - *TDD-PHY-03*: Physics engine MUST verify the 6D UMAP (3 spatial, 3 HSV) continuously rotates the text-highlight colors at the exact speed defined in the legacy tracker.
  - *TDD-INT-02*: Simulate an active cursor focus event while an SSE chunk arrives; test MUST assert the chunk is buffered into a queue rather than forcefully injected into the Milkdown AST.

## Phase 5: State Persistence & Multi-Context Isomorphism
- **Goal:** Implement the continuous feedback loop for frontend diff syncing, chunk deduplication, and SLM context caching across multiple agents.
- **Pre-requisite:** `gsd-model-design-test` validates against continuous persistence sequences.
- **Requirements Mapped:** US-4, US-5, REQ-3.0
- **Success Criteria:**
  1. Frontend chunk mapping deduplicates identical nodes.
  2. The continuous UI-backend loop (debounce payload -> quantizer -> Kuzu -> UMAP -> UI) correctly functions in real-time.
- **TDD Designed-To-Fail Cases:** 
  - *TDD-ISO-01*: Force a frontend AST diff payload targeting an existing chunk ID; test MUST assert a MERGE update rather than duplicate creation.
  - *TDD-ISO-02*: Integration tests MUST verify that recursive subtree fields of original markdown are strictly isomorphic before and after a secondary SLM response inline diff. (Zero duplicates or diffeomorphisms allowed).
  - *TDD-CTX-02*: Dispatch queries from two separate session IDs in parallel; test MUST assert the cache isolates them without contamination.

## Phase 6: Multi-Node Retrieval UI
- **Goal:** Implement the semantic link `/` operator, the hover crystal-ball rendering, and secondary billboard tethering.
- **Pre-requisite:** Phase 4 (Physics) and Phase 2 (Vector DB Retrieval).
- **Requirements Mapped:** US-2.
- **Success Criteria:**
  1. `/` operator spawns search popup in the Milkdown editor.
  2. Hovering a search result spawns a secondary 2D billboard.
  3. Clicking a search result pins the secondary billboard.
- **TDD Designed-To-Fail Cases:** 
  - *TDD-UI-04*: Playwright MUST verify the forward-slash (`/`) operator triggers the hover-linked secondary billboard, and clicking pins it.
  - *TDD-UI-05*: Playwright MUST verify that rapidly hovering over 10 semantic results in 1 second applies a 150ms debounce/abort controller, rendering only the final secondary panel and preventing DOM spam.

## Phase 7: Chaos Concurrency & Animation Verification
- **Goal:** Ensure all continuous play-loops function flawlessly under chaotic user interaction (fast typing, rapid right-clicking, overlapping agent streams).
- **TDD Designed-To-Fail Cases:** 
  - *TDD-ISO-03*: Integration tests MUST assert the backend sequences/queues concurrent inbound debounce updates from the same node ID, preventing Kuzu transaction locks during fast typing.
  - *TDD-PHY-04*: If an SSE DOM resize occurs while a billboard is tweening back to its 3D tether, the `updateBillboardPosition` MUST smoothly interpolate the new DOM height without stuttering the camera vector.
  - *TDD-PHY-05*: If a new embedding causes a global UMAP manifold recalculation, the physics engine MUST apply a maximum velocity dampener (`v.clampLength(max)`) to prevent nodes from exploding across the screen.

## Phase 8: UI Implementation & Polish
- **Goal:** Strip out legacy glassmorphic features and implement the brutalist solid black, zero border-radius aesthetic with dynamic UMAP HSV text color rotation and cross-dimensional cylinder edge linking.
- **Pre-requisite:** Phase 4 (Physics) and Phase 6 (Multi-Node Retrieval UI).
- **Requirements Mapped:** US-4, US-5.
- **Success Criteria:**
  1. Solid black panels (`#000000`) with hard sharp corners.
  2. No extra UI elements (no "X" close buttons or labels).
  3. Dynamic UMAP HSV rotation for text highlight in both 3D and 2D.
  4. Cross-dimensional edge linking (3D-3D, 3D-2D, 2D-2D).
- **TDD Designed-To-Fail Cases:** 
  - *TDD-UI-06*: Playwright tests MUST assert `border-radius: 0` and `background-color: #000000` on billboard classes.
  - *TDD-UI-07*: Playwright tests MUST assert no `<button>` or `.label` elements are spawned within the billboard component.
  - *TDD-PHY-06*: Edge cylinder endpoints MUST recalculate by un-projecting 2D DOM screen space back into the 3D frustum when a node transitions between `isLocked` (2D) and `isSpatial` (3D) states.
