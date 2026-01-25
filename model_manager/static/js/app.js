/**
 * Onto2AI Model Manager - Main Application Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize
    initGraph();
    setupTabs();
    setupSearch();
    setupChat();
    setupQuery();
    setupToolbar();
    loadClasses();
});

/**
 * Tab switching functionality
 */
function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;

            // Update buttons
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update content
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `${tabId}-tab`) {
                    content.classList.add('active');
                }
            });
        });
    });
}

/**
 * Load and display class list
 */
async function loadClasses() {
    const listContainer = document.getElementById('class-list');

    try {
        const response = await fetch('/api/classes');
        if (!response.ok) throw new Error('Failed to load classes');

        const classes = await response.json();

        listContainer.innerHTML = classes.map((cls, index) => `
            <div class="class-item" 
                 data-label="${escapeHtml(cls.label)}"
                 style="animation-delay: ${index * 30}ms">
                ${escapeHtml(cls.label)}
            </div>
        `).join('');

        // Add click handlers
        listContainer.querySelectorAll('.class-item').forEach(item => {
            item.addEventListener('click', () => {
                // Update active state
                listContainer.querySelectorAll('.class-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');

                // Load graph
                loadGraphData(item.dataset.label);
            });
        });

    } catch (error) {
        console.error('Error loading classes:', error);
        listContainer.innerHTML = '<div class="placeholder">Failed to load classes. Is the server running?</div>';
    }
}

/**
 * Search functionality
 */
function setupSearch() {
    const searchInput = document.getElementById('search-input');

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const items = document.querySelectorAll('.class-item');

        items.forEach(item => {
            const label = item.dataset.label.toLowerCase();
            item.style.display = label.includes(query) ? 'block' : 'none';
        });
    });
}

/**
 * Chat functionality
 */
function setupChat() {
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send');
    const messagesContainer = document.getElementById('chat-messages');

    const sendMessage = async () => {
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message
        addChatMessage(message, 'user');
        chatInput.value = '';

        // Show loading
        const loadingId = addChatMessage('Thinking...', 'assistant');

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });

            if (!response.ok) throw new Error('Chat request failed');

            const data = await response.json();

            // Replace loading with response
            const loadingEl = document.getElementById(loadingId);
            if (loadingEl) {
                loadingEl.querySelector('.message-content').textContent = data.response;
            }

        } catch (error) {
            console.error('Chat error:', error);
            const loadingEl = document.getElementById(loadingId);
            if (loadingEl) {
                loadingEl.querySelector('.message-content').textContent =
                    'Sorry, I encountered an error. Please try again.';
            }
        }
    };

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
}

/**
 * Add a chat message to the container
 */
function addChatMessage(content, role) {
    const container = document.getElementById('chat-messages');
    const id = `msg-${Date.now()}`;

    const msgHtml = `
        <div class="chat-message ${role}" id="${id}">
            <div class="message-content">${escapeHtml(content)}</div>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', msgHtml);
    container.scrollTop = container.scrollHeight;

    return id;
}

/**
 * Cypher query functionality
 */
function setupQuery() {
    const runBtn = document.getElementById('run-query');
    const queryInput = document.getElementById('cypher-input');
    const resultsContainer = document.getElementById('query-results');

    runBtn.addEventListener('click', async () => {
        const query = queryInput.value.trim();
        if (!query) return;

        resultsContainer.innerHTML = '<div class="loading">Running query...</div>';

        try {
            const response = await fetch('/api/cypher', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Query failed');
            }

            resultsContainer.innerHTML = `
                <div style="margin-bottom: 8px; color: var(--text-muted);">
                    ${data.count} result(s)
                </div>
                <pre>${escapeHtml(JSON.stringify(data.results, null, 2))}</pre>
            `;

        } catch (error) {
            console.error('Query error:', error);
            resultsContainer.innerHTML = `
                <div style="color: var(--danger);">
                    Error: ${escapeHtml(error.message)}
                </div>
            `;
        }
    });
}

/**
 * Toolbar button handlers
 */
function setupToolbar() {
    document.getElementById('zoom-in').addEventListener('click', zoomIn);
    document.getElementById('zoom-out').addEventListener('click', zoomOut);
    document.getElementById('fit-view').addEventListener('click', fitView);
    document.getElementById('refresh-layout').addEventListener('click', refreshLayout);
}

/**
 * Helper: Escape HTML to prevent XSS
 */
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return String(unsafe)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
