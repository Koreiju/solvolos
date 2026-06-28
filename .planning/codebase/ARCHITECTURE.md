# Architecture
*Last updated: 2026-06-27*

# Architecture
*Last updated: 2026-06-28*

## Core Patterns

This project has migrated to a strict `model-design-test` architecture validation workflow. 
All architectural definitions, object models, and algorithmic pseudocode are strictly maintained in the [`../architecture/MAIN.md`](../architecture/MAIN.md) root model.

Please refer to the following specific model files for implementation details:
- **[System Object Model](../architecture/MAIN.md)**: High-level module mapping and system boundaries.
- **[Context Engine](../architecture/ContextEngine.md)**: Token-budgeting, chunk ranking, and structural lineage injection.
- **[Kuzu Graph DB](../architecture/KuzuGraph.md)**: Vector-graph persistence and node topology.
- **[3D Projector](../architecture/3DProjector.md)**: Three.js coordinates, visualization, and normalization physics.
- **[Milkdown Billboard](../architecture/MilkdownBillboard.md)**: 2D Brutalist solid black rendering and diffuse semantic chat streaming.

## Data Flow
*Refer to the pseudocode flows in the architecture module documents for precise data handling steps.*
