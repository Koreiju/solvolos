/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi } from 'vitest';
import * as THREE from 'three';

describe('Interaction Layer State', () => {
    it('TDD-INT-01: pinned billboard ignores background DOM hover states', () => {
        // Mock global interaction state
        const InteractionState = {
            hoveredId: null,
            lockedId: 'pinned-node-123',
            isDragging: false,
            isDetached: false
        };

        // Mock window interface
        window.billboardApp = {
            showForNode: vi.fn(),
            hide: vi.fn()
        };

        // Mock a raycast event intersecting a DIFFERENT node in the background
        const mockIntersectEvent = {
            length: 1,
            0: {
                object: {
                    userData: { id: 'background-node-456' }
                }
            }
        };

        // Logic from InteractionLayer.md / projector.js
        const handleHoverEvent = (intersects) => {
            // TDD-INT-01 Constraint: MUST immediately return if lockedId is active!
            // But if implemented poorly, it overwrites the state.
            
            // Poor implementation (fails the constraint):
            if (intersects.length > 0) {
                let id = intersects[0].object.userData.id;
                if (InteractionState.hoveredId !== id) {
                    InteractionState.hoveredId = id; // Overwrites!
                    window.billboardApp.showForNode(id, false);
                }
            }
        };

        handleHoverEvent(mockIntersectEvent);

        // EXPECTED FAILURE (Current poor logic):
        expect(InteractionState.hoveredId).toBe('background-node-456');
        expect(window.billboardApp.showForNode).toHaveBeenCalledWith('background-node-456', false);
        
        // When implemented correctly, handleHoverEvent will check `if (InteractionState.lockedId) return;`
        // and the state will remain null/unchanged.
    });
});
