import { describe, it, expect } from 'vitest';
import * as THREE from 'three';

describe('Topological Physics Engine', () => {
    it('TDD-PHY-01: applies exact spring repulsion at < 2.25 distSq', () => {
        // Mock two chunks exactly at the same target coordinates
        const chunk1 = new THREE.Mesh();
        chunk1.position.set(0, 0, 0);
        chunk1.userData = { targetPos: new THREE.Vector3(1, 1, 1), velocity: new THREE.Vector3(0,0,0), parent_id: 'session-1' };

        const chunk2 = new THREE.Mesh();
        chunk2.position.set(0, 0, 0);
        chunk2.userData = { targetPos: new THREE.Vector3(1, 1, 1), velocity: new THREE.Vector3(0,0,0), parent_id: 'session-1' };

        const chunks = [chunk1, chunk2];

        // Mock applyNormalizationPhysics logic
        const applyNormalizationPhysics = (chunks) => {
            // Spring force towards target
            chunks.forEach(mesh => {
                mesh.userData.velocity.x += (mesh.userData.targetPos.x - mesh.position.x) * 0.05;
                mesh.userData.velocity.y += (mesh.userData.targetPos.y - mesh.position.y) * 0.05;
                mesh.userData.velocity.z += (mesh.userData.targetPos.z - mesh.position.z) * 0.05;
            });
            
            // Sibling repulsion (This is what we are testing)
            // TDD-PHY-01 dictates a strict repulsion if distSq < 2.25
            for (let i = 0; i < chunks.length; i++) {
                for (let j = 0; j < chunks.length; j++) {
                    if (i === j) continue;
                    let dx = chunks[i].position.x - chunks[j].position.x;
                    let dy = chunks[i].position.y - chunks[j].position.y;
                    let dz = chunks[i].position.z - chunks[j].position.z;
                    let distSq = dx*dx + dy*dy + dz*dz;
                    
                    if (distSq < 2.25) {
                        // The naive implementation fails when dx=0, dy=0, dz=0 because force becomes NaN
                        let dist = Math.sqrt(distSq);
                        let force = (1.5 - dist) / dist; 
                        chunks[i].userData.velocity.x += dx * force * 0.05;
                        chunks[i].userData.velocity.y += dy * force * 0.05;
                        chunks[i].userData.velocity.z += dz * force * 0.05;
                    }
                }
            }

            chunks.forEach(mesh => {
                mesh.userData.velocity.multiplyScalar(0.85);
                mesh.position.add(mesh.userData.velocity);
            });
        };

        applyNormalizationPhysics(chunks);

        // EXPECTED FAILURE:
        // Because they start at 0,0,0 dist is 0. Force is Infinity/NaN. 
        // Velocity becomes NaN, position becomes NaN.
        expect(isNaN(chunk1.position.x)).toBe(true);
        expect(isNaN(chunk2.position.x)).toBe(true);
        
        // When implemented correctly, it should apply an explicit random nudge to resolve 0-distance collisions
        // and chunk1.position.x should be a valid number apart from chunk2.position.x
    });
});
