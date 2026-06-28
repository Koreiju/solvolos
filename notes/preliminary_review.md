# Preliminary Review of Previous WIPs

## 1. Tracker Project (`legacy_wips/tracker`)
This project serves as the trusted source for the 3D embeddings projector.
### Capabilities
- **Three.js Projector (`projector.js`)**: Implements an interactive 3D particle and node visualization. It handles rendering nodes as spheres, configuring connections between chat nodes as cylinders, and updating colors, animations (spatial and color velocities).
- **Interactivity**: Includes robust raycasting logic for hover, selection, and dragging nodes. Also includes tag-based filtering and search glow effects. 
- **Billboard Integration**: Interacts with a 2D HTML element (`#billboard`) bound to 3D positions to show details (name, description, location, website) and quick actions (tags, yes/no status buttons).
### Alignment with New App Notes
- The 3D projector is fundamentally sound and ready for reuse. The concept of mapping 2D elements to 3D node positions (like the current billboard) perfectly aligns with the new requirement of building a Milkdown billboard out of the 3D nodes.
- The background and aesthetics are already styled with high quality, ensuring the visual experience remains smooth.
- **Actionable Takeaway**: We will extract the `CompanyProjector` (renamed appropriately) and adapt the `showBillboard` functionality to hook into a new Milkdown-based 2D overlay rather than the old HTML templates.

## 2. Tracker Copy (`legacy_wips/tracker - Copy`)
This project contains the incomplete chat sidebar work.
### Capabilities
- **Chat Interface (`chat_interface.js`)**: Basic state management for chat sessions, creating sessions, renaming, switching between chats, and reading/writing to a chat history panel.
- **AI Streaming**: Uses Server-Sent Events (SSE) to stream AI responses in real-time (`/api/chat/stream`). 
- **3D Bridge**: Connects to the global `window.app` (the 3D projector) to add user and AI nodes directly into the 3D scene when messages are sent. Links nodes sequentially in a conversation chain.
### Alignment with New App Notes
- We will strip the 2D "sidebar" aspect completely as mandated. However, the core logic for handling SSE streams, generating unique session IDs, appending conversational nodes sequentially, and pinging the projector to build 3D links is highly reusable. 
- **Actionable Takeaway**: We will utilize the streaming and session logic from this script, but wire its output streams directly into the new Milkdown rendered billboards rather than a fixed sidebar. The retrieval and linking (`@` and `/`) will be introduced directly into this modified chat handler.
