/**
 * Onto2AI Model Manager - Main Application Logic
 */

let currentClassName = null;
let currentVizMode = 'graph';

document.addEventListener('DOMContentLoaded', () => {
    // Initialize
    initGraph();
    setupTabs();
    setupVizTabs();
    setupSearch();
    setupChat();
    setupQuery();
    setupToolbar();
    setupSplitters();
    setupStagingSections();
    setupLLM();
    setupTheme();
    loadClasses();
    loadRelationships();
    loadIndividuals();
    loadDatatypes();
    loadClassHierarchy();
});

/**
 * Theme Toggle functionality
 */
function setupTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;

    // Theme is applied early in index.html to prevent flickering.
    // We just sync the GoJS theme if it's currently light.
    const isLight = document.documentElement.classList.contains('light-mode');
    if (isLight && typeof window.updateGraphTheme === 'function') {
        window.updateGraphTheme(true);
    }

    themeToggle.addEventListener('click', () => {
        const currentlyLight = document.documentElement.classList.toggle('light-mode');
        localStorage.setItem('theme', currentlyLight ? 'light' : 'dark');

        // Sync GoJS diagram if it exists
        if (typeof window.updateGraphTheme === 'function') {
            window.updateGraphTheme(currentlyLight);
        }
    });
}

/**
 * LLM Switching functionality
 */
async function setupLLM() {
    const selector = document.getElementById('llm-selector');
    if (!selector) return;

    // Fetch initial status
    try {
        const response = await fetch('/api/llm');
        if (response.ok) {
            const data = await response.json();

            // Populate selector
            selector.innerHTML = data.available_llms.map(model => {
                // Prettify name if it's a common one, otherwise use as-is
                let label = model;
                if (model === 'gemini-2.0-flash-exp') label = 'Gemini 2.0 Flash';
                if (model === 'gemini-3-flash-preview-001') label = 'Gemini 3 Flash Preview';
                if (model === 'gpt-4o-2024-05-13') label = 'GPT-4o';

                return `<option value="${model}" ${model === data.current_llm ? 'selected' : ''}>${label}</option>`;
            }).join('');
        }
    } catch (e) {
        console.error('Error fetching LLM status:', e);
    }

    // Handle change
    selector.addEventListener('change', async () => {
        const newLLM = selector.value;
        const previousValue = selector.value; // In case of failure

        try {
            const response = await fetch('/api/llm', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ llm_name: newLLM })
            });

            if (response.ok) {
                const data = await response.json();
                console.log(`LLM switched to ${data.current_llm}`);
                addChatMessage(`🔄 Switched to **${newLLM}** model.`, 'system');
            } else {
                selector.value = previousValue;
                throw new Error('Failed to update LLM');
            }
        } catch (e) {
            console.error('Error updating LLM:', e);
            addChatMessage(`❌ Error switching LLM: ${e.message}`, 'system');
        }
    });
}

/**
 * Splitter resize functionality
 */
function setupSplitters() {
    const leftPanel = document.getElementById('left-panel');
    const rightPanel = document.getElementById('right-panel');
    const leftSplitter = document.getElementById('left-splitter');
    const rightSplitter = document.getElementById('right-splitter');

    let isResizing = false;
    let currentSplitter = null;

    function startResize(e, splitter) {
        isResizing = true;
        currentSplitter = splitter;
        document.body.classList.add('resizing');
        splitter.classList.add('dragging');
        e.preventDefault();
    }

    function doResize(e) {
        if (!isResizing) return;

        const containerRect = document.querySelector('.main-content').getBoundingClientRect();

        if (currentSplitter === leftSplitter) {
            // Resize left panel
            let newWidth = e.clientX - containerRect.left;
            newWidth = Math.max(180, Math.min(500, newWidth));
            leftPanel.style.width = newWidth + 'px';
        } else if (currentSplitter === rightSplitter) {
            // Resize right panel
            let newWidth = containerRect.right - e.clientX;
            newWidth = Math.max(200, Math.min(500, newWidth));
            rightPanel.style.width = newWidth + 'px';
        }

        // Trigger GoJS diagram resize
        if (typeof myDiagram !== 'undefined' && myDiagram) {
            myDiagram.requestUpdate();
        }
    }

    function stopResize() {
        if (isResizing) {
            isResizing = false;
            document.body.classList.remove('resizing');
            if (currentSplitter) {
                currentSplitter.classList.remove('dragging');
            }
            currentSplitter = null;
        }
    }

    // Event listeners
    leftSplitter.addEventListener('mousedown', (e) => startResize(e, leftSplitter));
    rightSplitter.addEventListener('mousedown', (e) => startResize(e, rightSplitter));
    document.addEventListener('mousemove', doResize);
    document.addEventListener('mouseup', stopResize);
}

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
    const countBadge = document.getElementById('classes-count');

    try {
        const response = await fetch('/api/classes');
        if (!response.ok) throw new Error('Failed to load classes');

        const classes = await response.json();
        if (countBadge) countBadge.textContent = classes.length;

        listContainer.innerHTML = classes.map((cls, index) => `
            <div class="class-item"
                 data-label="${escapeHtml(cls.label)}"
                 style="animation-delay: ${index * 30}ms">
                <span class="class-icon">◆</span>
                ${escapeHtml(cls.label)}
            </div>
        `).join('');

        // Use event delegation for class item clicks
        listContainer.addEventListener('click', (event) => {
            const item = event.target.closest('.class-item');
            if (item) {
                // Update active state across both lists
                document.querySelectorAll('.class-item, .rel-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');

                currentClassName = item.dataset.label;

                // Load based on current viz mode
                if (currentVizMode === 'graph') {
                    loadGraphData(currentClassName);
                } else {
                    loadUmlData(currentClassName, currentVizMode);
                }
            }
        });

    } catch (error) {
        console.error('Error loading classes:', error);
        listContainer.innerHTML = '<div class="placeholder">Failed to load classes. Is the server running?</div>';
    }
}

/**
 * Load and display relationship list
 */
async function loadRelationships() {
    const listContainer = document.getElementById('relationship-list');
    const countBadge = document.getElementById('relationships-count');

    try {
        const response = await fetch('/api/relationships');
        if (!response.ok) throw new Error('Failed to load relationships');

        const rels = await response.json();
        if (countBadge) countBadge.textContent = rels.length;

        listContainer.innerHTML = rels.map((rel, index) => `
            <div class="rel-item"
                 data-source="${escapeHtml(rel.source_class)}"
                 data-type="${escapeHtml(rel.relationship_type)}"
                 data-target="${escapeHtml(rel.target_class)}"
                 style="animation-delay: ${index * 20}ms">
                <span class="rel-source">${escapeHtml(rel.source_class)}</span>
                <span class="rel-arrow">→</span>
                <span class="rel-type">${escapeHtml(rel.relationship_label || rel.relationship_type)}</span>
                <span class="rel-arrow">→</span>
                <span class="rel-target">${escapeHtml(rel.target_class)}</span>
                ${rel.requirement === 'Mandatory' ? '<span class="rel-badge mandatory">req</span>' : ''}
            </div>
        `).join('');

        // Click handler: focus on the source class
        listContainer.addEventListener('click', (event) => {
            const item = event.target.closest('.rel-item');
            if (item) {
                document.querySelectorAll('.class-item, .rel-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');

                currentClassName = item.dataset.source;

                if (currentVizMode === 'graph') {
                    loadGraphData(currentClassName);
                } else {
                    loadUmlData(currentClassName, currentVizMode);
                }
            }
        });

    } catch (error) {
        console.error('Error loading relationships:', error);
        listContainer.innerHTML = '<div class="placeholder">Failed to load relationships.</div>';
    }
}

/**
 * Setup collapsible staging sections
 */
function setupStagingSections() {
    document.querySelectorAll('.staging-section-header').forEach(header => {
        header.addEventListener('click', () => {
            const body = header.nextElementSibling;
            const toggle = header.querySelector('.section-toggle');
            const isCollapsed = body.classList.toggle('collapsed');
            toggle.textContent = isCollapsed ? '▶' : '▼';
        });
    });
}

/**
 * Load and display named individuals grouped by rdf:type
 */
async function loadIndividuals() {
    const listContainer = document.getElementById('individual-list');
    const countBadge = document.getElementById('individuals-count');

    try {
        const response = await fetch('/api/individuals');
        if (!response.ok) throw new Error('Failed to load individuals');

        const groups = await response.json();
        const totalCount = groups.reduce((sum, g) => sum + g.count, 0);
        if (countBadge) countBadge.textContent = totalCount;

        if (groups.length === 0) {
            listContainer.innerHTML = '<div class="placeholder">No named individuals found</div>';
            return;
        }

        listContainer.innerHTML = groups.map(group => `
            <div class="individual-group">
                <div class="individual-group-header" data-type="${escapeHtml(group.type_label)}">
                    <span class="group-toggle">▼</span>
                    <span class="group-type-label">${escapeHtml(group.type_label)}</span>
                    <span class="group-count">${group.count}</span>
                </div>
                <div class="individual-group-body">
                    ${group.members.map(m => `
                        <div class="individual-item" data-label="${escapeHtml(m.label)}" data-type="${escapeHtml(group.type_label)}" title="${escapeHtml(m.definition || '')}">
                            <span class="individual-icon">●</span>
                            ${escapeHtml(m.label)}
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');

        // Toggle group collapse
        listContainer.querySelectorAll('.individual-group-header').forEach(header => {
            header.addEventListener('click', (e) => {
                e.stopPropagation();
                const body = header.nextElementSibling;
                const toggle = header.querySelector('.group-toggle');
                const isCollapsed = body.classList.toggle('collapsed');
                toggle.textContent = isCollapsed ? '▶' : '▼';
            });
        });

        // Click handler: clicking an individual focuses graph on its type class
        listContainer.addEventListener('click', (event) => {
            const item = event.target.closest('.individual-item');
            if (item) {
                document.querySelectorAll('.class-item, .rel-item, .individual-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');

                currentClassName = item.dataset.type;
                if (currentVizMode === 'graph') {
                    loadGraphData(currentClassName);
                } else {
                    loadUmlData(currentClassName, currentVizMode);
                }
            }
        });

    } catch (error) {
        console.error('Error loading individuals:', error);
        listContainer.innerHTML = '<div class="placeholder">Failed to load individuals.</div>';
    }
}

/**
 * Load and display datatypes
 */
async function loadDatatypes() {
    const listContainer = document.getElementById('datatype-list');
    const countBadge = document.getElementById('datatypes-count');

    try {
        const response = await fetch('/api/datatypes');
        if (!response.ok) throw new Error('Failed to load datatypes');

        const datatypes = await response.json();
        if (countBadge) countBadge.textContent = datatypes.length;

        if (datatypes.length === 0) {
            listContainer.innerHTML = '<div class="placeholder">No datatypes staged</div>';
            return;
        }

        listContainer.innerHTML = datatypes.map((dt, index) => `
            <div class="datatype-item" data-label="${escapeHtml(dt.label)}" title="${escapeHtml(dt.definition || dt.uri || '')}" style="animation-delay: ${index * 30}ms">
                <span class="datatype-icon">◇</span>
                ${escapeHtml(dt.label)}
            </div>
        `).join('');

    } catch (error) {
        console.error('Error loading datatypes:', error);
        listContainer.innerHTML = '<div class="placeholder">Failed to load datatypes.</div>';
    }
}

/**
 * Load and display class hierarchy tree
 */
async function loadClassHierarchy() {
    const listContainer = document.getElementById('hierarchy-list');
    const countBadge = document.getElementById('hierarchy-count');

    try {
        const response = await fetch('/api/class-hierarchy');
        if (!response.ok) throw new Error('Failed to load class hierarchy');

        const data = await response.json();
        if (countBadge) countBadge.textContent = data.total_edges;

        if (!data.tree || data.tree.length === 0) {
            listContainer.innerHTML = '<div class="placeholder">No class hierarchy found</div>';
            return;
        }

        function renderNode(node, depth) {
            const hasChildren = node.children && node.children.length > 0;
            const indent = depth * 16;
            const icon = hasChildren ? '▼' : '•';
            const iconClass = hasChildren ? 'hierarchy-toggle' : 'hierarchy-leaf';

            let html = `
                <div class="hierarchy-node" data-label="${escapeHtml(node.label)}" data-depth="${depth}" title="${escapeHtml(node.definition || '')}">
                    <div class="hierarchy-node-row" style="padding-left: ${indent}px">
                        <span class="${iconClass}">${icon}</span>
                        <span class="hierarchy-label">${escapeHtml(node.label)}</span>
                    </div>`;

            if (hasChildren) {
                html += `<div class="hierarchy-children">`;
                for (const child of node.children) {
                    html += renderNode(child, depth + 1);
                }
                html += `</div>`;
            }

            html += `</div>`;
            return html;
        }

        listContainer.innerHTML = data.tree.map(root => renderNode(root, 0)).join('');

        // Toggle collapse for parent nodes
        listContainer.querySelectorAll('.hierarchy-toggle').forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                e.stopPropagation();
                const node = toggle.closest('.hierarchy-node');
                const children = node.querySelector('.hierarchy-children');
                if (children) {
                    const isCollapsed = children.classList.toggle('collapsed');
                    toggle.textContent = isCollapsed ? '▶' : '▼';
                }
            });
        });

        // Click handler: clicking a hierarchy node focuses graph on that class
        listContainer.addEventListener('click', (event) => {
            const row = event.target.closest('.hierarchy-node-row');
            if (row && !event.target.classList.contains('hierarchy-toggle')) {
                const node = row.closest('.hierarchy-node');
                const label = node.dataset.label;

                document.querySelectorAll('.class-item, .rel-item, .individual-item, .hierarchy-node-row').forEach(i => i.classList.remove('active'));
                row.classList.add('active');

                currentClassName = label;
                if (currentVizMode === 'graph') {
                    loadGraphData(currentClassName);
                } else {
                    loadUmlData(currentClassName, currentVizMode);
                }
            }
        });

    } catch (error) {
        console.error('Error loading class hierarchy:', error);
        listContainer.innerHTML = '<div class="placeholder">Failed to load hierarchy.</div>';
    }
}

/**
 * Visualization Tab switching logic (Graph vs UML vs Pydantic)
 */
function setupVizTabs() {
    const tabBtns = document.querySelectorAll('.viz-tab-btn');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const mode = btn.dataset.viz;
            if (mode === currentVizMode) return;

            // Update UI
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            currentVizMode = mode;

            // Refresh visualization if a class is currently selected
            if (currentClassName) {
                if (currentVizMode === 'graph') {
                    loadGraphData(currentClassName);
                } else {
                    loadUmlData(currentClassName, currentVizMode);
                }
            }
        });
    });
}

/**
 * Search functionality
 */
function setupSearch() {
    // Class filter
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const items = document.querySelectorAll('.class-item');
        items.forEach(item => {
            const label = item.dataset.label.toLowerCase();
            item.style.display = label.includes(query) ? 'flex' : 'none';
        });
    });

    // Relationship filter
    const relSearchInput = document.getElementById('rel-search-input');
    if (relSearchInput) {
        relSearchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const items = document.querySelectorAll('.rel-item');
            items.forEach(item => {
                const source = (item.dataset.source || '').toLowerCase();
                const type = (item.dataset.type || '').toLowerCase();
                const target = (item.dataset.target || '').toLowerCase();
                const match = source.includes(query) || type.includes(query) || target.includes(query);
                item.style.display = match ? 'flex' : 'none';
            });
        });
    }
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
                const contentEl = loadingEl.querySelector('.message-content');
                contentEl.innerHTML = formatMessageContent(data.response, 'assistant');

                // Re-apply syntax highlighting to any new code blocks
                if (typeof hljs !== 'undefined') {
                    contentEl.querySelectorAll('pre code').forEach((block) => {
                        hljs.highlightElement(block);
                    });
                }
            }

            // Check if response includes graph data and display it
            if (data.graph_data && data.graph_data.nodes && data.graph_data.nodes.length > 0) {
                loadGraphFromData(data.graph_data);

                // Add a note that graph was displayed
                addChatMessage('📊 Graph visualization updated in the center panel.', 'system');
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
 * Format message content based on role (Markdown/HTML for assistant)
 */
function formatMessageContent(content, role) {
    if (role === 'user') {
        return `<p>${escapeHtml(content)}</p>`;
    }

    if (role === 'system') {
        return content;
    }

    // Role is assistant - try HTML or Markdown
    const hasHtmlTags = /<[a-z][\s\S]*>/i.test(content);

    if (hasHtmlTags) {
        return content; // Direct HTML
    }

    try {
        const m = typeof marked === 'object' && marked.marked ? marked.marked : marked;
        if (typeof m === 'object' && typeof m.parse === 'function') {
            return m.parse(content);
        } else if (typeof m === 'function') {
            return m(content);
        }
    } catch (e) {
        console.error('Markdown parsing error:', e);
    }

    return content.replace(/\n/g, '<br>');
}

/**
 * Add a chat message to the container
 */
function addChatMessage(content, role) {
    const container = document.getElementById('chat-messages');
    const id = `msg-${Date.now()}`;

    const formattedContent = formatMessageContent(content, role);

    const msgHtml = `
        <div class="chat-message ${role}" id="${id}">
            <div class="message-content">${formattedContent}</div>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', msgHtml);
    container.scrollTop = container.scrollHeight;

    // Apply highlighting to code blocks if highlight.js is present
    if (role === 'assistant' && typeof hljs !== 'undefined') {
        const msgEl = document.getElementById(id);
        msgEl.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    }

    return id;
}

// Configure marked.js for custom highlighting and styling
function configureMarked() {
    const m = typeof marked === 'object' && marked.marked ? marked.marked : marked;
    if (typeof m === 'object' && typeof m.setOptions === 'function') {
        m.setOptions({
            highlight: function (code, lang) {
                if (typeof hljs !== 'undefined') {
                    if (lang && hljs.getLanguage(lang)) {
                        return hljs.highlight(code, { language: lang }).value;
                    }
                    return hljs.highlightAuto(code).value;
                }
                return code;
            },
            breaks: true,
            gfm: true
        });
    }
}
configureMarked();


/**
 * Cypher query functionality
 */
function setupQuery() {
    const runBtn = document.getElementById('run-query');
    const queryInput = document.getElementById('cypher-input');
    const resultsContainer = document.getElementById('query-results');
    const propertiesContent = document.getElementById('properties-content');

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

            // Check result type
            if (data.result_type === 'graph' && data.graph_data && data.graph_data.nodes.length > 0) {
                // Display graph in middle panel
                loadGraphFromData(data.graph_data);

                resultsContainer.innerHTML = `
                    <div style="margin-bottom: 8px; color: var(--success);">
                        📊 Graph displayed in center panel (${data.graph_data.nodes.length} nodes, ${data.graph_data.links.length} links)
                    </div>
                    <div style="color: var(--text-muted); font-size: 0.8rem;">
                        ${data.count} result row(s)
                    </div>
                `;
            } else {
                // Display table in right panel
                if (data.results.length > 0 && data.table_columns) {
                    displayTableResults(data.results, data.table_columns, propertiesContent);

                    resultsContainer.innerHTML = `
                        <div style="margin-bottom: 8px; color: var(--success);">
                            📋 Table displayed in Properties panel
                        </div>
                        <div style="color: var(--text-muted); font-size: 0.8rem;">
                            ${data.count} result row(s), ${data.table_columns.length} column(s)
                        </div>
                    `;
                } else {
                    resultsContainer.innerHTML = `
                        <div style="margin-bottom: 8px; color: var(--text-muted);">
                            ${data.count} result(s)
                        </div>
                        <pre>${escapeHtml(JSON.stringify(data.results, null, 2))}</pre>
                    `;
                }
            }

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
 * Display tabular results in a panel
 */
function displayTableResults(results, columns, container) {
    if (!results || results.length === 0) {
        container.innerHTML = '<div class="placeholder">No results</div>';
        return;
    }

    // Build table HTML
    let tableHtml = `
        <div class="query-table-container">
            <table class="query-results-table">
                <thead>
                    <tr>
                        ${columns.map(col => `<th>${escapeHtml(col)}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
    `;

    for (const row of results) {
        tableHtml += '<tr>';
        for (const col of columns) {
            let value = row[col];
            if (value === null || value === undefined) {
                value = '-';
            } else if (typeof value === 'object') {
                value = JSON.stringify(value);
            }

            const strValue = String(value);
            const isHtml = /<[a-z][\s\S]*>/i.test(strValue);

            // Truncate long values if not HTML
            const displayValue = (!isHtml && strValue.length > 100)
                ? strValue.substring(0, 100) + '...'
                : strValue;

            if (isHtml) {
                tableHtml += `<td title="HTML Content">${displayValue}</td>`;
            } else {
                tableHtml += `<td title="${escapeHtml(strValue)}">${escapeHtml(displayValue)}</td>`;
            }
        }
        tableHtml += '</tr>';
    }

    tableHtml += `
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = tableHtml;
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
