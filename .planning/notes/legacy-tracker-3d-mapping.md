---
title: "Legacy Tracker 3D Design Mapping"
date: "2026-06-27"
context: "Analysis of legacy_wips/tracker/ui/static/js/projector.js for reintegration."
---

# Legacy Tracker 3D Spatial Mathematics

The legacy `tracker` implementation utilized a very different 3D rendering approach compared to our modern `projector.js`. If we aim to integrate its feel while maintaining our new chunk physics, we need to understand the underlying math.

## 1. Global Rotation Matrices
Instead of spring physics, the scene relies on constant, uniform Euler rotations applied to every node's base UMAP coordinate.
```javascript
const spatialMatrix = new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(
    time * this.spatialVelocity.x, 
    time * this.spatialVelocity.y, 
    time * this.spatialVelocity.z
));
const newPos = initData.position.clone().applyMatrix4(spatialMatrix);
```

## 2. Color Shifting
"Unreviewed" nodes dynamically cycle their RGB hues using an identical Euler rotation matrix applied to their normalized `[0,1]` color space.
```javascript
const centeredColor = initData.umapColor.clone().subScalar(0.5);
centeredColor.applyMatrix4(colorMatrix);
centeredColor.addScalar(0.5);
```

## 3. Scale and Environment
- **Scale**: UMAP coordinates are scaled by `5x` (instead of our current `10x`).
- **Camera**: Utilizes `THREE.OrbitControls` rather than custom fly-to-view CSS translations.
- **Background**: Achieves depth via a `THREE.VideoTexture` mapped to a plane geometry at `z = -500`, scaling dynamically to match the camera's FOV.
