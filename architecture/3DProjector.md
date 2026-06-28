# 3D Projector

This module manages the physical Three.js coordinate mapping, topology rendering, and normalization physics located in `projector.js`.

## Object Model

```mermaid
classDiagram
    class ProjectorApp {
        +THREE.Scene scene
        +THREE.PerspectiveCamera camera
        +THREE.WebGLRenderer renderer
        +Map globalNodes
        +Map chunkNodes
        +List edges
        +init()
        +initBackground()
        +loadGraph()
        +addStreamingNode(nodeData)
        +syncDynamicUpdates(data)
        +createCylinderEdge(p1, p2, edgeType, srcId, tgtId)
        +highlightNode(id, isLocked)
        +unhighlightNode(id)
        +animate()
    }
    
    class BlackSlatePanel {
        +THREE.Mesh slate
        +THREE.Mesh text
        +Vector3 spatialCoords
        +Vector3 hsvColors
        +updateTextHighlightRotation()
    }
    
    class EdgeRenderer {
        +updateCylinderEndpoints(node1, node2)
        +project2DTo3D(domElement) Vector3
    }
    
    ProjectorApp --> BlackSlatePanel : Renders instead of primitive spheres
    ProjectorApp --> EdgeRenderer : Manages 3D-3D, 3D-2D, and 2D-2D cylindrical edge updates
    note for ProjectorApp "Raycasting and mouse events modeled in InteractionLayer.md"
```

## Algorithmic Pseudocode (from `projector.js`)

```javascript
// From projector.js: animate()
function applyNormalizationPhysics(chunkPanels) {
    // Prevent erratic jumping when new nodes are streamed in
    
    for (let i = 0; i < chunkPanels.length; i++) {
        let panel = chunkPanels[i];
        
        // Continuously rotate HSV highlight colors on the text mesh
        panel.updateTextHighlightRotation();

        if (!panel.userData.targetPos || !panel.userData.velocity) continue;
        
        let t = panel.userData.targetPos;
        let v = panel.userData.velocity;
        
        // 1. Spring force towards Kuzu-calculated target coordinates
        v.x += (t.x - panel.position.x) * 0.05;
        v.y += (t.y - panel.position.y) * 0.05;
        v.z += (t.z - panel.position.z) * 0.05;
        
        // 2. Repel from sibling chunks sharing the same parent
        for (let j = 0; j < chunkPanels.length; j++) {
            if (i === j) continue;
            let other = chunkPanels[j];
            if (panel.userData.parent_id === other.userData.parent_id) {
                let dx = panel.position.x - other.position.x;
                let dy = panel.position.y - other.position.y;
                let dz = panel.position.z - other.position.z;
                let distSq = dx*dx + dy*dy + dz*dz;
                
                if (distSq > 0.01 && distSq < 2.25) { // Inside repulsion radius
                    let dist = Math.sqrt(distSq);
                    let force = (1.5 - dist) / dist; 
                    v.x += dx * force * 0.05;
                    v.y += dy * force * 0.05;
                    v.z += dz * force * 0.05;
                }
            }
        }
        
        // 3. Apply friction, clamp max velocity (TDD-PHY-05), & update position
        v.multiplyScalar(0.85);
        v.clampLength(0, 0.5); // Prevent UMAP manifold explosion
        panel.position.add(v);
    }
}
```

## Function Design & TDD Assertions

```mermaid
sequenceDiagram
    participant App as ProjectorApp
    participant Node as ChunkNode
    participant Engine as PhysicsEngine

    App->>Node: stream in new chunk
    App->>Engine: animate() loop starts
    Engine->>Node: apply target vector spring
    Engine->>Node: calculate sibling repulsion
    
    note right of Engine: TDD-PHY-01: If distSq < 2.25, sequence MUST apply repulsion.<br/>Failing TDD asserts no collisions exist in final vector map.
    
    Engine->>Node: apply friction and update
    Engine->>Node: rotate text HSV highlight by UMAP array
    
    note right of Engine: TDD-PHY-03: Physics engine MUST verify the 6D UMAP continuously rotates the text-highlight colors on the BlackSlatePanels.<br/>Failing TDD asserts static color rendering or sphere primitives exist.
    
    App->>App: window.onresize
    App->>App: updateBillboardPosition()
    
    note right of App: TDD-PHY-02: If window is resized while locked, 3D camera projection vector MUST instantly recalculate.<br/>Failing TDD asserts 2D DOM drifts from fixed 3D spatial node constraint.
    
    App->>App: Billboard detaching and tweening
    App->>App: SSE Chunk Resize Event fires
    
    note right of App: TDD-PHY-04: If an SSE DOM resize occurs while a billboard is tweening back to its 3D tether, the `updateBillboardPosition` MUST smoothly interpolate the new DOM height without stuttering the camera vector.
```
