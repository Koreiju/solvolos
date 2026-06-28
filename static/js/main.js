import { ProjectorApp } from './projector.js';
import { BillboardApp } from './billboard.js';

window.addEventListener('DOMContentLoaded', () => {
    // Initialize the main projector application
    window.app = new ProjectorApp();
    
    // Initialize the billboard interaction application
    window.billboardApp = new BillboardApp();
});
