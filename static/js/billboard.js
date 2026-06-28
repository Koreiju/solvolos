import { Editor, rootCtx, defaultValueCtx, editorViewCtx } from '@milkdown/core';
import { commonmark } from '@milkdown/preset-commonmark';
import { nord } from '@milkdown/theme-nord';
import { listener, listenerCtx } from '@milkdown/plugin-listener';
import { replaceAll } from '@milkdown/utils';
import { gfm } from '@milkdown/preset-gfm';
import { history } from '@milkdown/plugin-history';
import { clipboard } from '@milkdown/plugin-clipboard';
import { prism } from '@milkdown/plugin-prism';

export class SSEProcessor {
    constructor() {
        this.buffer = "";
    }

    parse(chunk) {
        this.buffer += chunk;
        const results = [];
        
        while (this.buffer.length > 0) {
            let start = this.buffer.indexOf('{');
            if (start === -1) break;
            
            let braceCount = 0;
            let end = -1;
            let inString = false;
            let escapeNext = false;
            
            for (let i = start; i < this.buffer.length; i++) {
                const char = this.buffer[i];
                if (escapeNext) { escapeNext = false; continue; }
                if (char === '\\') { escapeNext = true; continue; }
                if (char === '"') { inString = !inString; continue; }
                
                if (!inString) {
                    if (char === '{') braceCount++;
                    else if (char === '}') braceCount--;
                    
                    if (braceCount === 0) {
                        end = i;
                        break;
                    }
                }
            }
            
            if (end !== -1) {
                const jsonStr = this.buffer.substring(start, end + 1);
                try {
                    results.push(JSON.parse(jsonStr));
                    this.buffer = this.buffer.substring(end + 1);
                } catch (e) { break; }
            } else { break; }
        }
        return results;
    }
}

export class ASTInjectionQueue {
    constructor() {
        this.queue = [];
        this.isFlushing = false;
    }
    
    enqueue(chunk, editorNode) {
        this.queue.push(chunk);
        this.tryFlush(editorNode);
    }
    
    tryFlush(editorNode) {
        if (this.isFlushing) return;
        this.isFlushing = true;
        while (this.queue.length > 0) {
            const chunk = this.queue.shift();
            if (editorNode) {
                const el = document.createElement('div');
                el.className = 'chunk-node';
                el.textContent = chunk.text || "dummy";
                editorNode.appendChild(el);
            }
        }
        this.isFlushing = false;
    }
}

export class HoverCrystalBall {
    constructor() {
        this.debounceTimer = null;
        this.currentPanel = null;
        this.fetchCount = 0;
    }
    
    handleHover(resultId, x, y) {
        if (this.debounceTimer) clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.fetchCount++;
            if (typeof document !== 'undefined') {
                const panel = document.createElement('div');
                panel.className = 'hover-panel secondary-billboard';
                panel.style.position = 'absolute';
                panel.style.left = (x || 0) + 'px';
                panel.style.top = (y || 0) + 'px';
                panel.style.zIndex = '1000';
                panel.textContent = 'Result: ' + resultId;
                
                panel.addEventListener('click', () => {
                    panel.classList.add('pinned');
                });
                document.body.appendChild(panel);
                this.currentPanel = panel;
            }
        }, 150);
    }
}

export class BillboardApp {
    constructor() {
        console.log("BillboardApp initialized.");
        this.sseProcessor = new SSEProcessor();
        this.injectionQueue = new ASTInjectionQueue();
        this.crystalBall = new HoverCrystalBall();
        
        this.editors = new Map();
        
        if (typeof document !== 'undefined') {
            document.addEventListener('keyup', (e) => {
                if (e.target && e.target.closest('.milkdown')) {
                    if (e.key === '/') {
                        this.crystalBall.handleHover('slash-search', 100, 100);
                    }
                }
            });
        }
    }
    
    async spawnPinnedEditor(nodeId, x, y) {
        if (typeof document === 'undefined') return;
        
        const container = document.createElement('div');
        container.className = 'billboard-container';
        container.dataset.nodeId = nodeId;
        container.style.left = `${x}px`;
        container.style.top = `${y}px`;
        
        const milkdownContainer = document.createElement('div');
        milkdownContainer.className = 'milkdown';
        
        const chatPanel = document.createElement('div');
        chatPanel.className = 'chat-panel';
        chatPanel.contentEditable = true;
        chatPanel.style.minHeight = '3em';
        
        const popup = document.createElement('div');
        popup.className = 'reference-popup';
        container.appendChild(popup);

        chatPanel.addEventListener('keydown', async (e) => {
            if (e.key === '\\') {
                popup.style.display = 'flex';
                popup.innerHTML = '<div class="popup-title">Retrieve Nodes</div><div class="popup-results"></div>';
            } else if (popup.style.display === 'flex') {
                if (e.key === 'Escape') {
                    popup.style.display = 'none';
                    return;
                }
                setTimeout(async () => {
                    const match = chatPanel.innerText.match(/\\([^]*)$/);
                    if (match) {
                        const query = match[1].trim();
                        if (query.length > 0) {
                            try {
                                const res = await fetch('/api/search?q=' + encodeURIComponent(query));
                                const data = await res.json();
                                const resultsDiv = popup.querySelector('.popup-results');
                                if (resultsDiv && data.results) {
                                    resultsDiv.innerHTML = '';
                                    data.results.slice(0, 5).forEach(r => {
                                        const item = document.createElement('div');
                                        item.className = 'popup-item';
                                        item.textContent = r.text || r.id;
                                        item.onclick = () => {
                                            const badge = document.createElement('span');
                                            badge.className = 'hl-retrieval';
                                            badge.textContent = r.id;
                                            badge.contentEditable = false;
                                            
                                            chatPanel.innerHTML = chatPanel.innerHTML.replace(/\\([^]*)$/, '');
                                            chatPanel.appendChild(badge);
                                            chatPanel.innerHTML += '&nbsp;';
                                            
                                            popup.style.display = 'none';
                                            
                                            const selection = window.getSelection();
                                            const range = document.createRange();
                                            range.selectNodeContents(chatPanel);
                                            range.collapse(false);
                                            selection.removeAllRanges();
                                            selection.addRange(range);
                                        };
                                        resultsDiv.appendChild(item);
                                    });
                                }
                            } catch (err) { console.error(err); }
                        }
                    }
                }, 50);
            }
            if (e.key === 'Enter' && !e.shiftKey && popup.style.display !== 'flex') {
                e.preventDefault();
                const msg = chatPanel.innerText;
                chatPanel.innerText = '';
                
                try {
                    const res = await fetch('/api/chat/stream', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ id: nodeId, message: msg })
                    });
                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    
                    let done = false;
                    while (!done) {
                        const { value, done: d } = await reader.read();
                        done = d;
                        if (value) {
                            const chunk = decoder.decode(value, {stream: true});
                            const parsedChunks = this.sseProcessor.parse(chunk);
                            for (const c of parsedChunks) {
                                if (c.text) {
                                    const nodeState = this.editors.get(nodeId);
                                    if (nodeState) {
                                        nodeState.text += c.text;
                                        nodeState.editor.action(replaceAll(nodeState.text));
                                    }
                                }
                            }
                        }
                    }
                } catch (err) { console.error(err); }
            }
        });
        
        container.appendChild(milkdownContainer);
        container.appendChild(chatPanel);
        document.getElementById('ui-layer').appendChild(container);
        
        const editor = await Editor.make()
            .config((ctx) => {
                ctx.set(rootCtx, milkdownContainer);
                ctx.set(defaultValueCtx, "");
            })
            .use(nord)
            .use(commonmark)
            .use(gfm)
            .use(history)
            .use(clipboard)
            .use(prism)
            .use(listener)
            .create();
            
        editor.action((ctx) => {
            const lst = ctx.get(listenerCtx);
            lst.markdownUpdated((ctx, markdown, prevMarkdown) => {
                if (markdown !== prevMarkdown) {
                    this.debouncedSave(nodeId, markdown);
                }
            });
        });
        
        this.editors.set(nodeId, { editor, container, text: "" });
        
        // Let projector know we have a node pinned at this screen coordinate
        if (window.app) {
            window.app.lockedNodes.set(nodeId, { isLocked: true, domX: x, domY: y });
        }
        
        this.setupDragging(container, nodeId);
    }
    
    setupDragging(container, nodeId) {
        let isDragging = false;
        let startX, startY, initialLeft, initialTop;
        
        container.addEventListener('mousedown', (e) => {
            if (e.target.closest('.milkdown') || e.target.closest('.chat-panel')) return;
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            initialLeft = parseInt(container.style.left || 0);
            initialTop = parseInt(container.style.top || 0);
        });
        
        window.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            container.style.left = `${initialLeft + dx}px`;
            container.style.top = `${initialTop + dy}px`;
            
            if (window.app) {
                window.app.lockedNodes.set(nodeId, { 
                    isLocked: true, 
                    domX: initialLeft + dx, 
                    domY: initialTop + dy 
                });
            }
        });
        
        window.addEventListener('mouseup', () => {
            isDragging = false;
        });
        
        container.addEventListener('dblclick', (e) => {
            if (container.classList.contains('square-3d')) {
                e.stopPropagation();
                this.flyBackTo2D(nodeId);
            }
        });
    }
    
    flyBackTo2D(nodeId) {
        const data = this.editors.get(nodeId);
        if (data && window.app) {
            data.container.classList.remove('square-3d');
            data.container.style.position = 'absolute';
            
            const x = window.innerWidth / 2 - 200;
            const y = window.innerHeight / 2 - 200;
            data.container.style.left = `${x}px`;
            data.container.style.top = `${y}px`;
            
            window.app.convertFrom3D(nodeId, data.container);
            window.app.lockedNodes.set(nodeId, { isLocked: true, domX: x, domY: y });
        }
    }
    
    flyBackTo3D(nodeId) {
        const data = this.editors.get(nodeId);
        if (data && window.app) {
            const x = parseInt(data.container.style.left || 0);
            const y = parseInt(data.container.style.top || 0);
            
            window.app.lockedNodes.delete(nodeId);
            data.container.style.position = 'static'; // Hand over to WebGL
            data.container.style.left = '0px';
            data.container.style.top = '0px';
            data.container.classList.add('square-3d');
            
            window.app.convertTo3D(nodeId, data.container, x, y);
        }
    }
    
    debouncedSave(nodeId, markdown) {
        if (this.saveTimeout) clearTimeout(this.saveTimeout);
        this.saveTimeout = setTimeout(async () => {
            try {
                await fetch('/api/sync', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ id: nodeId, text: markdown })
                });
            } catch (e) {
                console.error("Save failed:", e);
            }
        }, 1000);
    }
}
