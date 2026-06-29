import * as THREE from 'three';
import { CSS3DRenderer, CSS3DObject } from 'three/examples/jsm/renderers/CSS3DRenderer.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

export class PhysicsEngine {
    constructor() {
        this.nodes = [];
    }
    
    addNode(node) {
        this.nodes.push(node);
    }
    
    applyRepulsion() {
        const MIN_DIST = 1.5;
        const MIN_DIST_SQ = MIN_DIST * MIN_DIST; // 2.25
        
        for (let i = 0; i < this.nodes.length; i++) {
            for (let j = i + 1; j < this.nodes.length; j++) {
                const n1 = this.nodes[i];
                const n2 = this.nodes[j];
                
                let dx = n2.x - n1.x;
                let dy = n2.y - n1.y;
                let dz = n2.z - n1.z;
                
                let distSq = dx*dx + dy*dy + dz*dz;
                
                if (distSq < MIN_DIST_SQ) {
                    let dist = Math.sqrt(distSq);
                    if (dist === 0) {
                        dx = Math.random() * 0.1 + 0.01;
                        dy = Math.random() * 0.1 + 0.01;
                        dz = Math.random() * 0.1 + 0.01;
                        dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
                    }
                    
                    const overlap = MIN_DIST - dist;
                    const force = overlap / dist * 0.5;
                    
                    n1.x -= dx * force;
                    n1.y -= dy * force;
                    n1.z -= dz * force;
                    
                    n2.x += dx * force;
                    n2.y += dy * force;
                    n2.z += dz * force;
                }
            }
        }
    }
}

export class ProjectorApp {
    constructor() {
        console.log("ProjectorApp initialized.");
        this.physics = new PhysicsEngine();
        this.projectionMatrix = [1, 0, 0, 1];
        this.colorRotation = 0;
        
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.cssRenderer = null;
        this.controls = null;
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        this.objects = [];
        
        this.clock = new THREE.Clock();
        this.animationTime = 0;
        this.centroidTare = new THREE.Vector3(0, 0, 0);
        this.spatialVelocity = { x: 0.05, y: 0.1, z: 0.02 };
        this.colorVelocity = { x: 0.4, y: 0.6, z: 0.3 };
        this.initialNodeData = new Map();
        
        this.lockedNodes = new Map(); // Keep track of nodes pinned to 2D
        this.css3dObjects = new Map(); // Keep track of 3D objects
        
        if (typeof window !== 'undefined') {
            this.initThreeJS();
            window.addEventListener('resize', () => {
                this.updateProjection();
            });
            window.addEventListener('dblclick', (e) => this.onDoubleClick(e));
            window.addEventListener('contextmenu', (e) => this.onRightClick(e));
        }
        
        this.tick = this.tick.bind(this);
        if (typeof requestAnimationFrame !== 'undefined') {
            requestAnimationFrame(this.tick);
        }
    }
    
    initThreeJS() {
        const canvas = document.getElementById('webgl-canvas');
        if (!canvas) return; // For TDD contexts that lack the canvas
        
        this.scene = new THREE.Scene();
        this.scene.fog = new THREE.FogExp2(0x0f1115, 0.002);
        
        this.camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.camera.position.set(0, 5, 20);
        
        this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        
        // CSS3DRenderer for Milkdown panels in 3D
        this.cssRenderer = new CSS3DRenderer();
        this.cssRenderer.setSize(window.innerWidth, window.innerHeight);
        this.cssRenderer.domElement.style.position = 'absolute';
        this.cssRenderer.domElement.style.top = '0';
        this.cssRenderer.domElement.style.pointerEvents = 'none'; // Let clicks pass if not on a panel
        document.getElementById('ui-layer').appendChild(this.cssRenderer.domElement);
        
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
    }
    
    onDoubleClick(e) {
        // Prevent if we double-clicked inside a UI element
        if (e.target.closest('.milkdown, .billboard-container')) return;
        
        // Create a new empty node pinned to 2D space
        const nodeId = 'node_' + Date.now();
        if (window.billboardApp) {
            window.billboardApp.spawnPinnedEditor(nodeId, e.clientX, e.clientY);
        }
    }
    
    onRightClick(e) {
        // Find if we right clicked on a pinned billboard
        const container = e.target.closest('.billboard-container');
        if (container) {
            e.preventDefault();
            const nodeId = container.dataset.nodeId;
            if (window.billboardApp) {
                window.billboardApp.flyBackTo3D(nodeId);
            }
        }
    }
    
    convertTo3D(nodeId, element, x, y) {
        // Convert screen coordinates to 3D roughly
        const width = window.innerWidth;
        const height = window.innerHeight;
        const ndcX = (x / width) * 2 - 1;
        const ndcY = -(y / height) * 2 + 1;
        
        const obj = new CSS3DObject(element);
        
        // Restore initial spatial position if we have it, else use ndc
        if (this.initialNodeData.has(nodeId)) {
            const initPos = this.initialNodeData.get(nodeId).position;
            obj.position.copy(initPos);
        } else {
            obj.position.set(ndcX * 20, ndcY * 20, -10);
        }
        obj.scale.set(0.02, 0.02, 0.02);
        
        this.scene.add(obj);
        this.css3dObjects.set(nodeId, obj);
        this.lockedNodes.delete(nodeId);
    }
    
    convertFrom3D(nodeId, element) {
        const obj = this.css3dObjects.get(nodeId);
        if (obj) {
            this.scene.remove(obj);
            this.css3dObjects.delete(nodeId);
        }
        document.getElementById('ui-layer').appendChild(element);
        this.lockedNodes.set(nodeId, true);
        
        // Pin to pure white
        element.style.color = '#ffffff';
        const editors = element.querySelectorAll('.milkdown');
        editors.forEach(ed => {
            ed.style.color = '#ffffff';
        });
    }

    syncDynamicUpdates(data) {
        if (!data || !data.nodes) return;
        
        // Calculate Centroid Tare
        let cx = 0, cy = 0, cz = 0;
        let count = 0;
        data.nodes.forEach(n => {
            if (n.x !== undefined) {
                cx += n.x; cy += n.y; cz += n.z;
                count++;
            }
        });
        if (count > 0) {
            this.centroidTare.set(cx / count, cy / count, cz / count);
        }
        
        data.nodes.forEach(node => {
            if (node.x !== undefined) {
                const initialPos = new THREE.Vector3(
                    (node.x - this.centroidTare.x) * 5, 
                    (node.y - this.centroidTare.y) * 5, 
                    (node.z - this.centroidTare.z) * 5
                );
                const umapColor = new THREE.Vector3(node.r || 0.2, node.g || 0.5, node.b || 1.0);
                
                this.initialNodeData.set(node.id, {
                    position: initialPos,
                    umapColor: umapColor
                });
            }
        });
    }
    
    updateProjection() {
        if (this.camera && this.renderer && this.cssRenderer) {
            this.camera.aspect = window.innerWidth / window.innerHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(window.innerWidth, window.innerHeight);
            this.cssRenderer.setSize(window.innerWidth, window.innerHeight);
        }
    }
    
    calculateEdgeEndpoint(nodeState) {
        if (nodeState.isLocked) {
            let width = 1920;
            let height = 1080;
            if (typeof window !== 'undefined') {
                width = window.innerWidth;
                height = window.innerHeight;
            }
            
            const x = (nodeState.domX / width) * 2 - 1;
            const y = -(nodeState.domY / height) * 2 + 1;
            
            const cameraZ = 5; 
            return { x: x * cameraZ, y: y * cameraZ, z: 0 };
        }
        return { x: nodeState.x, y: nodeState.y, z: nodeState.z };
    }
    
    tick() {
        if (typeof document !== 'undefined') {
            document.documentElement.style.setProperty('--umap-hsv-rotation', `${this.colorRotation}deg`);
        }
        
        const delta = this.clock.getDelta();
        this.animationTime += delta;
        const time = this.animationTime;
        
        const spatialMatrix = new THREE.Matrix4();
        const spatialEuler = new THREE.Euler(
            time * this.spatialVelocity.x,
            time * this.spatialVelocity.y,
            time * this.spatialVelocity.z
        );
        spatialMatrix.makeRotationFromEuler(spatialEuler);

        const colorMatrix = new THREE.Matrix4();
        const colorEuler = new THREE.Euler(
            time * this.colorVelocity.x,
            time * this.colorVelocity.y,
            time * this.colorVelocity.z
        );
        colorMatrix.makeRotationFromEuler(colorEuler);
        
        for (const [nodeId, obj] of this.css3dObjects.entries()) {
            if (this.camera) {
                obj.quaternion.copy(this.camera.quaternion);
            }
            
            const initData = this.initialNodeData.get(nodeId);
            if (initData && !this.lockedNodes.has(nodeId)) {
                // Apply Spatial Rotation
                const newPos = initData.position.clone().applyMatrix4(spatialMatrix);
                obj.position.copy(newPos);
                
                // Apply Color Rotation (legacy math)
                const centeredColor = initData.umapColor.clone().subScalar(0.5);
                centeredColor.applyMatrix4(colorMatrix);
                centeredColor.addScalar(0.5);
                
                centeredColor.x = Math.max(0, Math.min(1, centeredColor.x));
                centeredColor.y = Math.max(0, Math.min(1, centeredColor.y));
                centeredColor.z = Math.max(0, Math.min(1, centeredColor.z));
                
                const newColor = new THREE.Color(centeredColor.x, centeredColor.y, centeredColor.z);
                const colorStr = '#' + newColor.getHexString();
                obj.element.style.color = colorStr;
                const editors = obj.element.querySelectorAll('.milkdown');
                editors.forEach(ed => {
                    ed.style.color = colorStr;
                });
            }
        }

        this.physics.applyRepulsion();
        if (this.controls) this.controls.update();
        
        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
            this.cssRenderer.render(this.scene, this.camera);
        }
        
        if (typeof requestAnimationFrame !== 'undefined') {
            requestAnimationFrame(this.tick);
        }
    }
}
