console.log("[Projector] Script loaded");

class ProjectorApp {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        
        this.globalNodes = new Map();
        this.chunkNodes = new Map();
        this.edges = [];
        
        this.hoveredId = null;
        this.lockedId = null; // clicked node
        
        this.init();
        this.loadGraph();
    }

    init() {
        const container = document.getElementById('projector-panel');
        const canvas = document.getElementById('projector-canvas');

        this.scene = new THREE.Scene();
        this.scene.fog = new THREE.FogExp2(0x0f1115, 0.002);

        this.camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 1000);
        this.camera.position.set(0, 5, 20);

        this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);

        const ambient = new THREE.AmbientLight(0xffffff, 0.7);
        const directional = new THREE.DirectionalLight(0xffffff, 0.8);
        directional.position.set(10, 20, 10);
        this.scene.add(ambient, directional);

        this.controls = new THREE.OrbitControls(this.camera, canvas);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;

        window.addEventListener('resize', () => this.onResize());
        
        // Background video
        this.initBackground();

        // Interactions
        canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
        canvas.addEventListener('click', (e) => this.onClick(e));
        canvas.addEventListener('dblclick', (e) => this.onDoubleClick(e));
        canvas.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            this.unlockNode();
        });

        this.animate();
    }

    initBackground() {
        const video = document.createElement('video');
        video.src = '/static/waterfall.mp4';
        video.loop = true;
        video.muted = true;
        video.playsInline = true;
        video.play().catch(e => console.warn(e));

        const texture = new THREE.VideoTexture(video);
        texture.minFilter = THREE.LinearFilter;
        texture.magFilter = THREE.LinearFilter;

        const geometry = new THREE.PlaneGeometry(1, 1);
        const material = new THREE.MeshBasicMaterial({ map: texture, depthWrite: false });
        this.backgroundMesh = new THREE.Mesh(geometry, material);
        this.backgroundMesh.position.z = -500;
        this.backgroundMesh.renderOrder = -1;
        this.camera.add(this.backgroundMesh);
        this.scene.add(this.camera);
        this.updateBackgroundScale();
    }

    updateBackgroundScale() {
        if (!this.camera || !this.backgroundMesh) return;
        const vFOV = THREE.Math.degToRad(this.camera.fov);
        const height = 2 * Math.tan(vFOV / 2) * 500;
        const width = height * this.camera.aspect;
        this.backgroundMesh.scale.set(width, height, 1);
    }

    onResize() {
        const container = document.getElementById('projector-panel');
        if (this.camera && this.renderer) {
            this.camera.aspect = container.clientWidth / container.clientHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(container.clientWidth, container.clientHeight);
            this.updateBackgroundScale();
        }
    }

    async loadGraph() {
        try {
            const res = await fetch('/api/nodes');
            const data = await res.json();
            
            // Clear existing
            this.globalNodes.forEach(m => this.scene.remove(m));
            this.chunkNodes.forEach(m => this.scene.remove(m));
            this.edges.forEach(m => this.scene.remove(m));
            this.globalNodes.clear();
            this.chunkNodes.clear();
            this.edges = [];

            const globalGeo = new THREE.IcosahedronGeometry(1.2, 1);
            const chunkGeo = new THREE.SphereGeometry(0.2, 16, 16);

            data.nodes.forEach(node => {
                const color = new THREE.Color(node.r, node.g, node.b);
                const mat = new THREE.MeshPhongMaterial({ color, emissive: 0x000000, transparent: true, opacity: 0.9 });
                
                const mesh = new THREE.Mesh(node.node_type === 'global' ? globalGeo : chunkGeo, mat);
                mesh.position.set(node.x * 10, node.y * 10, node.z * 10);
                mesh.userData = { ...node, originalColor: color.clone(), targetPos: new THREE.Vector3(node.x * 10, node.y * 10, node.z * 10), velocity: new THREE.Vector3() };

                this.scene.add(mesh);
                if (node.node_type === 'global') this.globalNodes.set(node.id, mesh);
                else this.chunkNodes.set(node.id, mesh);
            });

            // Draw edges
            data.edges.forEach(edge => {
                const srcMesh = this.globalNodes.get(edge.source) || this.chunkNodes.get(edge.source);
                const tgtMesh = this.globalNodes.get(edge.target) || this.chunkNodes.get(edge.target);
                if (srcMesh && tgtMesh) {
                    const mesh = this.createCylinderEdge(srcMesh.position, tgtMesh.position, edge.type, edge.source, edge.target);
                    this.scene.add(mesh);
                    this.edges.push(mesh);
                }
            });

        } catch (e) {
            console.error("Failed to load graph", e);
        }
    }

    addStreamingNode(nodeData) {
        // Used by billboard to inject new nodes live
        const isGlobal = nodeData.node_type === 'global';
        const geo = isGlobal ? new THREE.IcosahedronGeometry(1.2, 1) : new THREE.SphereGeometry(0.2, 16, 16);
        const color = new THREE.Color(nodeData.color[0], nodeData.color[1], nodeData.color[2]);
        const mat = new THREE.MeshPhongMaterial({ color, emissive: 0x222222, transparent: true, opacity: 1 });
        const mesh = new THREE.Mesh(geo, mat);
        
        const targetX = nodeData.pos[0] * 10;
        const targetY = nodeData.pos[1] * 10;
        const targetZ = nodeData.pos[2] * 10;
        
        mesh.userData = { ...nodeData, originalColor: color.clone(), targetPos: new THREE.Vector3(targetX, targetY, targetZ), velocity: new THREE.Vector3() };
        
        if (!isGlobal && nodeData.parent_id && this.globalNodes.has(nodeData.parent_id)) {
            const parent = this.globalNodes.get(nodeData.parent_id);
            mesh.position.copy(parent.position);
            mesh.position.x += (Math.random() - 0.5);
            mesh.position.y += (Math.random() - 0.5);
            mesh.position.z += (Math.random() - 0.5);
        } else {
            mesh.position.set(targetX, targetY, targetZ);
        }
        
        this.scene.add(mesh);
        
        if (isGlobal) {
            this.globalNodes.set(nodeData.id, mesh);
        } else {
            this.chunkNodes.set(nodeData.id, mesh);
            if (nodeData.parent_id) {
                const parent = this.globalNodes.get(nodeData.parent_id);
                if (parent) {
                    const edgeMesh = this.createCylinderEdge(mesh.position, parent.position, 'PART_OF', nodeData.id, nodeData.parent_id);
                    this.scene.add(edgeMesh);
                    this.edges.push(edgeMesh);
                }
            }
        }
    }

    syncDynamicUpdates(data) {
        if (data.global_node) {
            const gMesh = this.globalNodes.get(data.global_node.id);
            if (gMesh) {
                gMesh.userData.targetPos.set(data.global_node.x * 10, data.global_node.y * 10, data.global_node.z * 10);
            }
        }
        
        if (data.chunks) {
            // Remove old chunks belonging to this parent
            const chunksToRemove = [];
            this.chunkNodes.forEach((mesh, id) => {
                if (mesh.userData.parent_id === data.global_node.id) {
                    chunksToRemove.push(id);
                }
            });
            chunksToRemove.forEach(id => {
                const mesh = this.chunkNodes.get(id);
                this.scene.remove(mesh);
                this.chunkNodes.delete(id);
            });
            
            // Remove edges
            this.edges = this.edges.filter(edge => {
                if (edge.userData.tgtId === data.global_node.id && edge.userData.edgeType === 'PART_OF') {
                    this.scene.remove(edge);
                    return false;
                }
                return true;
            });
            
            // Spawn new chunks
            data.chunks.forEach(c => {
                this.addStreamingNode({
                    id: c.id,
                    node_type: 'chunk',
                    pos: [c.x, c.y, c.z],
                    color: [c.r, c.g, c.b],
                    parent_id: c.parent_id
                });
            });
        }
    }

    createCylinderEdge(p1, p2, edgeType, srcId, tgtId) {
        const distance = p1.distanceTo(p2);
        const geo = new THREE.CylinderGeometry(0.05, 0.05, distance, 8);
        
        let color = 0xffffff;
        if (edgeType === 'REFERENCES') color = 0xffd33d;
        else if (edgeType === 'FOLLOWS') color = 0x58a6ff;
        else if (edgeType === 'REPLIES_TO') color = 0x3fb950;
        else if (edgeType === 'PART_OF') color = 0x8b949e;
        
        const mat = new THREE.MeshPhongMaterial({ 
            color: color, 
            emissive: color,
            emissiveIntensity: edgeType === 'PART_OF' ? 0.2 : 0.8,
            transparent: true, 
            opacity: edgeType === 'PART_OF' ? 0.2 : 0.6 
        });
        
        const mesh = new THREE.Mesh(geo, mat);
        mesh.userData = { srcId, tgtId, edgeType, origDist: distance };
        mesh.position.copy(p1).lerp(p2, 0.5);
        
        const axis = new THREE.Vector3().subVectors(p2, p1).normalize();
        mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), axis);
        
        return mesh;
    }

    getIntersects(event) {
        const rect = this.renderer.domElement.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        this.raycaster.setFromCamera(this.mouse, this.camera);
        
        const objects = [...this.globalNodes.values(), ...this.chunkNodes.values()];
        return this.raycaster.intersectObjects(objects);
    }

    onMouseMove(event) {
        if (this.lockedId) {
            // Update billboard position continuously if tracking locked node
            this.updateBillboardPosition();
            return; 
        }

        const intersects = this.getIntersects(event);
        if (intersects.length > 0) {
            document.body.style.cursor = 'pointer';
            const id = intersects[0].object.userData.id;
            
            if (this.hoveredId !== id) {
                if (this.hoveredId) this.unhighlightNode(this.hoveredId);
                this.hoveredId = id;
                this.highlightNode(id);
                
                if (window.billboardApp) {
                    window.billboardApp.showForNode(id, false);
                }
            }
        } else {
            document.body.style.cursor = 'default';
            if (this.hoveredId) {
                this.unhighlightNode(this.hoveredId);
                this.hoveredId = null;
                if (window.billboardApp && !this.lockedId) {
                    window.billboardApp.hide();
                }
            }
        }
        
        this.updateBillboardPosition();
    }

    onClick(event) {
        const intersects = this.getIntersects(event);
        if (intersects.length > 0) {
            const id = intersects[0].object.userData.id;
            this.lockedId = id;
            this.highlightNode(id, true);
            if (window.billboardApp) {
                window.billboardApp.showForNode(id, true);
            }
        }
    }

    async onDoubleClick(event) {
        // Prevent action if clicking an existing node
        const intersects = this.getIntersects(event);
        if (intersects.length > 0) return;

        // Find 3D coordinate on the plane z=0
        const rect = this.renderer.domElement.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
        const target = new THREE.Vector3();
        if (!this.raycaster.ray.intersectPlane(plane, target)) return;

        // Calculate backend coordinates (divided by 10 based on multiplier in addStreamingNode)
        const bx = target.x / 10;
        const by = target.y / 10;
        const bz = target.z / 10;

        try {
            const res = await fetch('/api/nodes/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ x: bx, y: by, z: bz })
            });
            const data = await res.json();
            
            const nodeData = {
                id: data.id,
                node_type: data.node_type,
                color: [data.r, data.g, data.b],
                pos: [data.x, data.y, data.z]
            };
            
            this.addStreamingNode(nodeData);
            
            // Auto-focus and lock onto the new node
            this.lockedId = data.id;
            this.highlightNode(data.id, true);
            if (window.billboardApp) {
                window.billboardApp.showForNode(data.id, true);
            }
        } catch (e) {
            console.error("Failed to create empty node:", e);
        }
    }

    unlockNode() {
        if (this.lockedId) {
            this.unhighlightNode(this.lockedId);
            this.lockedId = null;
            if (window.billboardApp) window.billboardApp.hide();
        }
    }

    highlightNode(id, isLocked = false) {
        let mesh = this.globalNodes.get(id) || this.chunkNodes.get(id);
        if (!mesh) return;
        
        mesh.material.emissive.copy(mesh.userData.originalColor).multiplyScalar(0.5);
        
        // If it's a global node, highlight its chunks visually
        if (mesh.userData.node_type === 'global') {
            this.chunkNodes.forEach(c => {
                // Not perfectly modeled without full graph context in frontend, 
                // but we can query or just pulse nearby edges
            });
        }
    }

    unhighlightNode(id) {
        if (id === this.lockedId) return; // Keep locked highlighted
        let mesh = this.globalNodes.get(id) || this.chunkNodes.get(id);
        if (mesh) mesh.material.emissive.setHex(0x000000);
    }

    updateBillboardPosition() {
        const targetId = this.lockedId || this.hoveredId;
        if (!targetId || !window.billboardApp) return;
        
        let mesh = this.globalNodes.get(targetId) || this.chunkNodes.get(targetId);
        if (mesh && window.billboardApp.isVisible() && !window.billboardApp.isDragging) {
            const pos = mesh.position.clone();
            pos.project(this.camera);
            
            const x = (pos.x * 0.5 + 0.5) * window.innerWidth;
            const y = -(pos.y * 0.5 - 0.5) * window.innerHeight;
            
            // Offset a bit
            window.billboardApp.setPosition(x + 30, y - 100);
        }
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        
        // Physics step
        const chunks = Array.from(this.chunkNodes.values());
        for (let i = 0; i < chunks.length; i++) {
            const mesh = chunks[i];
            if (!mesh.userData.targetPos || !mesh.userData.velocity) continue;
            const t = mesh.userData.targetPos;
            const v = mesh.userData.velocity;
            
            // Spring to target
            v.x += (t.x - mesh.position.x) * 0.05;
            v.y += (t.y - mesh.position.y) * 0.05;
            v.z += (t.z - mesh.position.z) * 0.05;
            
            // Repel from siblings
            for (let j = 0; j < chunks.length; j++) {
                if (i === j) continue;
                const other = chunks[j];
                if (mesh.userData.parent_id && mesh.userData.parent_id === other.userData.parent_id) {
                    const dx = mesh.position.x - other.position.x;
                    const dy = mesh.position.y - other.position.y;
                    const dz = mesh.position.z - other.position.z;
                    const distSq = dx*dx + dy*dy + dz*dz;
                    
                    if (distSq > 0.01 && distSq < 2.25) { // 1.5 squared
                        const dist = Math.sqrt(distSq);
                        const force = (1.5 - dist) / dist; // Simple linear repulsion inside radius
                        v.x += dx * force * 0.05;
                        v.y += dy * force * 0.05;
                        v.z += dz * force * 0.05;
                    }
                }
            }
            
            // Friction & Move
            v.multiplyScalar(0.85);
            mesh.position.add(v);
        }
        
        // Update Edges
        this.edges.forEach(edge => {
            if (!edge.userData.srcId || !edge.userData.tgtId) return;
            const src = this.globalNodes.get(edge.userData.srcId) || this.chunkNodes.get(edge.userData.srcId);
            const tgt = this.globalNodes.get(edge.userData.tgtId) || this.chunkNodes.get(edge.userData.tgtId);
            if (src && tgt) {
                const p1 = src.position;
                const p2 = tgt.position;
                
                // Position at midpoint
                edge.position.copy(p1).lerp(p2, 0.5);
                
                // Scale Y
                const dist = p1.distanceTo(p2);
                if (edge.userData.origDist > 0) {
                    edge.scale.y = dist / edge.userData.origDist;
                }
                
                // Orient
                const axis = new THREE.Vector3().subVectors(p2, p1).normalize();
                edge.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), axis);
            }
        });

        if (this.controls) this.controls.update();
        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
        
        // Keep billboard attached during camera rotations
        if (this.lockedId) this.updateBillboardPosition();
    }
}

window.addEventListener('DOMContentLoaded', () => {
    window.app = new ProjectorApp();
});
