# Concerns
*Last updated: 2026-06-27*

## Technical Debt & Issues
- **Global JS Namespaces**: Relying on `window.app` and `window.billboardApp` creates tight coupling and race conditions if scripts load out of sequence or if multiple instances spawn.
- **Model Blocking**: Python Flask handles LLM execution in the main thread (or simple thread workers). During generation, other endpoints may suffer from lockups. Streaming responses mitigate UX lag but server throughput is severely bounded.
- **Database Scalability**: Recreating the entire graph representation from Kuzu to JSON for Three.js (`/api/nodes`) every time the user requests an update is O(N) and will freeze the browser for graphs larger than a few thousand nodes. We need viewport-based spatial culling or incremental graph hydration payloads.

## Security
- The system is completely local. No auth layers or API key protections are configured, meaning this cannot be deployed to a public web server without complete rewrite of access controls.
