class ChatInterface {
    constructor() {
        this.sessionId = this.generateId();
        this.isGenerating = false;
        this.lastNodeId = null; 

        this.initElements();
        this.initListeners();
        this.loadSessions();
        this.createSession(this.sessionId);
    }

    generateId() {
        return `session_${Date.now()}`;
    }

    initElements() {
        this.input = document.getElementById('message-input');
        this.sendBtn = document.getElementById('send-button');
        this.messagesContainer = document.getElementById('chat-messages');
        this.sessionList = document.getElementById('session-list');
        this.newChatBtn = document.getElementById('new-chat-btn');
        this.historyPanel = document.getElementById('history-panel');
        this.toggleHistoryBtn = document.getElementById('toggle-history');
        this.chatTitle = document.getElementById('current-chat-title');
        this.renameBtn = document.getElementById('rename-chat-btn');
    }

    initListeners() {
        if (this.sendBtn) {
            this.sendBtn.addEventListener('click', () => this.sendMessage());
        }
        
        if (this.input) {
            this.input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        if (this.newChatBtn) {
            this.newChatBtn.addEventListener('click', () => {
                this.sessionId = this.generateId();
                this.messagesContainer.innerHTML = '<div class="message system">New chat started.</div>';
                
                // Clear 3D visualization for new chat
                if (window.app && window.app.clearChatNodes) {
                    window.app.clearChatNodes();
                }
                this.lastNodeId = null;
                
                this.createSession(this.sessionId);
                if(this.chatTitle) this.chatTitle.textContent = "New Chat";
                this.loadSessions();
            });
        }

        if (this.toggleHistoryBtn && this.historyPanel) {
            this.toggleHistoryBtn.addEventListener('click', () => {
                this.historyPanel.classList.toggle('collapsed');
            });
        }
        
        if (this.renameBtn) {
            this.renameBtn.addEventListener('click', () => {
                const newName = prompt("Rename chat:", this.chatTitle.textContent);
                if (newName) {
                    this.renameSession(this.sessionId, newName);
                }
            });
        }
    }

    async createSession(id) {
        try {
            await fetch('/api/sessions', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ id: id, name: "New Chat" })
            });
            this.loadSessions();
        } catch (e) {
            console.error("Failed to create session:", e);
        }
    }
    
    async renameSession(id, name) {
        try {
            await fetch(`/api/sessions/${id}/rename`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ name: name })
            });
            if(this.chatTitle) this.chatTitle.textContent = name;
            this.loadSessions();
        } catch (e) {
            console.error("Failed to rename session:", e);
        }
    }

    async loadSessions() {
        try {
            const res = await fetch('/api/sessions');
            const sessions = await res.json();
            if (this.sessionList) {
                this.sessionList.innerHTML = '';
                sessions.forEach(sess => {
                    const el = document.createElement('div');
                    el.className = `session-item ${sess.id === this.sessionId ? 'active' : ''}`;
                    el.innerHTML = `<i class="fas fa-comment-alt"></i> ${sess.name || 'Untitled'}`;
                    el.onclick = () => this.switchSession(sess.id, sess.name);
                    this.sessionList.appendChild(el);
                });
            }
        } catch (e) {
            console.error("Failed to load sessions", e);
        }
    }

    switchSession(id, name) {
        this.sessionId = id;
        if(this.chatTitle) this.chatTitle.textContent = name;
        this.loadSessions(); 
        
        // Reset Visuals
        this.messagesContainer.innerHTML = '<div class="message system">History visualization loaded in 3D view.</div>';
        if (window.app && window.app.clearChatNodes) {
            window.app.clearChatNodes();
        }
        this.lastNodeId = null; 
    }

    async sendMessage() {
        const text = this.input.value.trim();
        if (!text || this.isGenerating) return;

        this.appendMessage('user', text);
        this.input.value = '';
        this.isGenerating = true;

        const aiMessageDiv = this.appendMessage('assistant', '...');
        let aiText = "";

        const eventSource = new EventSource(`/api/chat/stream?message=${encodeURIComponent(text)}&session_id=${this.sessionId}`);

        eventSource.onmessage = (e) => {
            const data = JSON.parse(e.data);
            
            if (data.chunk) {
                if (aiText === "") aiMessageDiv.textContent = ""; 
                aiText += data.chunk;
                aiMessageDiv.textContent = aiText;
                this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
            }
            
            if (data.nodes && window.app) {
                data.nodes.forEach(nodeData => {
                    window.app.addChatNode(nodeData);

                    // Connect user to last AI, or AI to last user
                    if (this.lastNodeId) {
                         window.app.connectChatNodes(this.lastNodeId, nodeData.id);
                    }
                    this.lastNodeId = nodeData.id;
                });
            }
            
            if (data.complete) {
                eventSource.close();
                this.isGenerating = false;
            }
            
            if (data.error) {
                eventSource.close();
                this.isGenerating = false;
                aiMessageDiv.textContent += " [Error: " + data.error + "]";
            }
        };
        
        eventSource.onerror = () => {
            eventSource.close();
            this.isGenerating = false;
        };
    }

    appendMessage(role, text) {
        const div = document.createElement('div');
        div.className = `message ${role}`;
        div.textContent = text;
        this.messagesContainer.appendChild(div);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        return div;
    }
}

window.addEventListener('DOMContentLoaded', () => {
    window.chat = new ChatInterface();
});