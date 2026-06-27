import { Editor, rootCtx, defaultValueCtx } from '@milkdown/core';
import { commonmark } from '@milkdown/preset-commonmark';
import { nord } from '@milkdown/theme-nord';
import { replaceAll } from '@milkdown/utils';
import { listener, listenerCtx } from '@milkdown/plugin-listener';
import { gfm } from '@milkdown/preset-gfm';
import { history } from '@milkdown/plugin-history';
import { clipboard } from '@milkdown/plugin-clipboard';
import { prism } from '@milkdown/plugin-prism';
import { tooltip } from '@milkdown/plugin-tooltip';
import { slash } from '@milkdown/plugin-slash';

class BillboardApp {
    constructor() {
        this.el = document.getElementById('billboard');
        this.content = document.getElementById('milkdown-container');
        this.title = document.getElementById('billboard-title');
        this.input = document.getElementById('chat-input');
        this.badgesContainer = document.getElementById('badges-container');
        this.sendBtn = document.getElementById('send-btn');
        this.popup = document.getElementById('reference-popup');
        this.popupResults = document.getElementById('popup-results');
        
        this.currentNodeId = null;
        this.isLocked = false;
        this.isDragging = false;
        this.isDetached = false;
        
        this.contextLinks = new Set(); // For retrieval references
        this.documentText = ""; // Maintain full markdown document state
        this.editor = null;
        this.saveTimeout = null;

        this.initMilkdown();
        this.initDrag();
        this.initInput();
        
        document.getElementById('billboard-close').onclick = () => {
            if (window.app) window.app.unlockNode();
        };

        this.el.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            if (this.isDetached) {
                this.returnToTether();
            } else {
                if (window.app) window.app.unlockNode();
            }
        });
    }

    async initMilkdown() {
        this.editor = await Editor.make()
            .config((ctx) => {
                ctx.set(rootCtx, this.content);
                ctx.set(defaultValueCtx, "");
                ctx.get(listenerCtx).markdownUpdated((ctx, markdown, prevMarkdown) => {
                    if (markdown !== prevMarkdown && this.currentNodeId) {
                        this.documentText = markdown;
                        this.debouncedSave();
                    }
                });
            })
            .use(nord)
            .use(commonmark)
            .use(gfm)
            .use(history)
            .use(clipboard)
            .use(prism)
            .use(tooltip)
            .use(slash)
            .use(listener)
            .create();
    }

    debouncedSave() {
        if (this.saveTimeout) clearTimeout(this.saveTimeout);
        this.saveTimeout = setTimeout(async () => {
            if (!this.currentNodeId) return;
            try {
                await fetch('/api/nodes/update', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        node_id: this.currentNodeId,
                        content: this.documentText
                    })
                });
                const data = await res.json();
                if (data.success && window.app) {
                    window.app.syncDynamicUpdates(data);
                }
            } catch (e) {
                console.error("Save failed:", e);
            }
        }, 1000);
    }

    isVisible() {
        return this.el.style.display === 'flex' || this.el.style.display === 'block';
    }

    showForNode(id, locked = false) {
        this.currentNodeId = id;
        this.isLocked = locked;
        this.isDetached = false; // Reset detachment when focusing new node
        this.el.style.display = 'flex';
        
        if (locked) {
            document.getElementById('billboard-pin').classList.add('pinned');
            this.flyToView();
        } else {
            document.getElementById('billboard-pin').classList.remove('pinned');
        }
        
        this.fetchNodeData(id);
    }

    hide() {
        this.el.style.display = 'none';
        this.isLocked = false;
        this.currentNodeId = null;
    }

    setPosition(x, y) {
        if (!this.isDragging && !this.isDetached) {
            // Keep within bounds
            const rect = this.el.getBoundingClientRect();
            x = Math.max(20, Math.min(x, window.innerWidth - rect.width - 20));
            y = Math.max(20, Math.min(y, window.innerHeight - rect.height - 20));
            this.el.style.left = x + 'px';
            this.el.style.top = y + 'px';
        }
    }

    flyToView() {
        this.isDetached = true;
        this.el.style.transition = 'top 0.4s cubic-bezier(0.2, 0, 0, 1), left 0.4s cubic-bezier(0.2, 0, 0, 1)';
        this.el.style.left = '5vw';
        this.el.style.top = '10vh';
        
        setTimeout(() => {
            this.el.style.transition = 'none';
        }, 400);
    }
    
    returnToTether() {
        this.isDetached = false;
        this.el.style.transition = 'top 0.4s cubic-bezier(0.2, 0, 0, 1), left 0.4s cubic-bezier(0.2, 0, 0, 1)';
        
        if (window.app) window.app.updateBillboardPosition();
        
        setTimeout(() => {
            this.el.style.transition = 'none';
        }, 400);
    }

    async fetchNodeData(id) {
        try {
            const res = await fetch(`/api/details/${id}`);
            const data = await res.json();
            
            this.title.textContent = data.title || 'Chat Session';
            this.documentText = data.content || '';
            
            if (this.editor) {
                this.editor.action(replaceAll(this.documentText));
                
                if (data.scroll_target) {
                    setTimeout(() => {
                        const walker = document.createTreeWalker(this.content, NodeFilter.SHOW_TEXT, null, false);
                        let node;
                        // use a partial substring to handle minor markdown mismatches
                        const targetText = data.scroll_target.replace(/[#*_-]/g, '').trim().substring(0, 30);
                        while(node = walker.nextNode()) {
                            if (node.nodeValue.includes(targetText) && targetText.length > 5) {
                                const el = node.parentElement;
                                el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                el.style.transition = 'background 0.5s ease-out';
                                el.style.background = 'rgba(88, 166, 255, 0.3)';
                                setTimeout(() => el.style.background = 'transparent', 2000);
                                break;
                            }
                        }
                    }, 100);
                }
            }
        } catch (e) {
            console.error(e);
        }
    }

    // --- Interaction Logic ---
    initInput() {
        this.sendBtn.onclick = () => this.sendMessage();
        this.input.onkeydown = (e) => {
            if (e.key === 'Enter') this.sendMessage();
            else this.handleSpecialChars(e);
        };
    }

    async handleSpecialChars(e) {
        if (e.key === '\\') {
            // Retrieval
            this.popup.style.display = 'flex';
            this.popup.querySelector('.popup-title').textContent = 'Retrieve Nodes';
        } else if (this.popup.style.display === 'flex') {
            // Filtering
            setTimeout(() => {
                const match = this.input.value.match(/\\([^]*)$/);
                if (match) this.fetchSuggestions(match[1], true);
            }, 50);
        }
    }

    async fetchSuggestions(query, isRetrieval=false) {
        if (isRetrieval) {
            const res = await fetch('/api/search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query})
            });
            const data = await res.json();
            this.renderPopup(data.nodes || [], true);
        }
    }

    renderPopup(items, isRetrieval) {
        this.popupResults.innerHTML = '';
        items.forEach(item => {
            const el = document.createElement('div');
            el.className = 'popup-item';
            const title = item.title || (item.node_type === 'chunk' ? item.type : item.role);
            const desc = (item.content || '').substring(0, 50) + '...';
            el.innerHTML = `<div class="popup-item-title">${title}</div><div class="popup-item-desc">${desc}</div>`;
            el.onclick = () => {
                if (isRetrieval) {
                    this.contextLinks.add(item.id);
                    
                    // Create badge
                    const badge = document.createElement('span');
                    badge.className = 'hl-retrieval';
                    badge.style.cursor = 'pointer';
                    badge.innerHTML = `${title} <i class="fas fa-times" style="margin-left:4px; opacity:0.7;"></i>`;
                    badge.onclick = () => {
                        this.contextLinks.delete(item.id);
                        badge.remove();
                    };
                    this.badgesContainer.appendChild(badge);
                }
                
                // Replace query in input
                const val = this.input.value;
                const replaceRegex = /\\([^]*)$/;
                this.input.value = val.replace(replaceRegex, '');
                this.popup.style.display = 'none';
                this.input.focus();
            };
            this.popupResults.appendChild(el);
        });
    }

    async sendMessage() {
        const text = this.input.value.trim();
        if (!text) return;

        this.input.value = '';
        this.popup.style.display = 'none';
        this.badgesContainer.innerHTML = '';

        const ctxIds = Array.from(this.contextLinks).join(',');
        this.contextLinks.clear();
        
        const payload = {
            message: text,
            session_id: this.currentNodeId || '', // Pass base node!
            context_ids: ctxIds
        };
        
        let aiStreamText = "";
        const originalDocText = this.documentText; // Preserve existing session text

        try {
            const res = await fetch('/api/chat/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value, {stream: true});
                const events = chunk.split('\n\n');
                
                for (const ev of events) {
                    if (ev.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(ev.slice(6));
                            if (data.error) {
                                console.error(data.error);
                                break;
                            }
                            
                            if (data.type === 'token') {
                                aiStreamText += data.content;
                                this.documentText = originalDocText + (originalDocText ? '\n\n' : '') + aiStreamText;
                                if(this.editor) {
                                    this.editor.action(replaceAll(this.documentText));
                                }
                            } else if (data.type === 'graph_update') {
                                if (window.app) {
                                    if (data.global_node) {
                                        window.app.syncDynamicUpdates({
                                            global_node: data.global_node,
                                            chunks: data.nodes // In chat_stream they are passed in `nodes` array
                                        });
                                    } else if (data.nodes) {
                                        data.nodes.forEach(n => window.app.addStreamingNode(n));
                                    }
                                }
                                if (data.diffused_content) {
                                    this.documentText = data.diffused_content;
                                    if(this.editor) {
                                        this.editor.action(replaceAll(this.documentText));
                                    }
                                }
                            }
                        } catch(e) {
                            console.error("Failed to parse SSE event", e, ev);
                        }
                    }
                }
            }
        } catch (e) {
            console.error("Connection Error:", e);
        }
    }

    // --- Drag Logic ---
    initDrag() {
        const header = this.el.querySelector('.billboard-header');
        let startX, startY, initialX, initialY;
        
        header.onmousedown = (e) => {
            if (e.target.tagName === 'I') return; // Don't drag if clicking buttons
            if (!this.isLocked) return; // Only drag if locked
            
            this.isDragging = true;
            this.isDetached = true; // Prevents projector.js from overriding position
            startX = e.clientX;
            startY = e.clientY;
            
            const rect = this.el.getBoundingClientRect();
            initialX = rect.left;
            initialY = rect.top;
            
            document.onmousemove = drag;
            document.onmouseup = stopDrag;
        };
        
        const drag = (e) => {
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            this.el.style.left = (initialX + dx) + 'px';
            this.el.style.top = (initialY + dy) + 'px';
        };
        
        const stopDrag = () => {
            this.isDragging = false;
            document.onmousemove = null;
            document.onmouseup = null;
        };
    }
}

window.addEventListener('DOMContentLoaded', () => {
    window.billboardApp = new BillboardApp();
});
