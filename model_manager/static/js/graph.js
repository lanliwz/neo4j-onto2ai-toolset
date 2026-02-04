/**
 * GoJS Graph Visualization for Onto2AI Model Manager
 */

let myDiagram = null;

/**
 * Initialize the GoJS diagram
 */
function initGraph() {
    const $ = go.GraphObject.make;

    myDiagram = $(go.Diagram, "graph-container", {
        initialContentAlignment: go.Spot.Center,
        "undoManager.isEnabled": true,
        layout: $(go.ForceDirectedLayout, {
            maxIterations: 200,
            defaultSpringLength: 100,
            defaultElectricalCharge: 150
        }),
        "animationManager.isEnabled": true,
        "toolManager.hoverDelay": 100
    });

    // Node template for classes
    myDiagram.nodeTemplateMap.add("class",
        $(go.Node, "Auto",
            {
                selectionAdorned: true,
                cursor: "pointer",
                click: (e, node) => onNodeClick(node),
                doubleClick: (e, node) => onNodeDoubleClick(node)
            },
            $(go.Shape, "RoundedRectangle", {
                fill: "#4f46e5",
                stroke: "#818cf8",
                strokeWidth: 2,
                portId: "",
                fromLinkable: true,
                toLinkable: true
            },
                new go.Binding("fill", "isCenter", (isCenter, obj) => {
                    if (obj.part.isSelected) return "#f59e0b";
                    return isCenter ? "#7c3aed" : "#4f46e5";
                }),
                new go.Binding("stroke", "isCenter", (isCenter) => isCenter ? "#a78bfa" : "#818cf8")),
            $(go.Panel, "Vertical",
                { margin: 12 },
                $(go.TextBlock, {
                    font: "bold 14px Inter, sans-serif",
                    stroke: "white",
                    margin: new go.Margin(0, 0, 4, 0)
                },
                    new go.Binding("text", "label")),
                $(go.TextBlock, {
                    font: "11px Inter, sans-serif",
                    stroke: "rgba(255,255,255,0.7)",
                    maxSize: new go.Size(150, NaN),
                    wrap: go.TextBlock.WrapFit
                },
                    new go.Binding("text", "definition", (d) => d ? truncate(d, 50) : ""))
            )
        )
    );

    // Node template for datatypes
    myDiagram.nodeTemplateMap.add("datatype",
        $(go.Node, "Auto",
            {
                selectionAdorned: true,
                cursor: "pointer",
                click: (e, node) => onNodeClick(node)
            },
            $(go.Shape, "RoundedRectangle", {
                fill: "#10b981",
                stroke: "#34d399",
                strokeWidth: 2
            },
                new go.Binding("fill", "isSelected", (sel) => sel ? "#f59e0b" : "#10b981").ofObject()),
            $(go.Panel, "Vertical",
                { margin: 10 },
                $(go.TextBlock, {
                    font: "bold 12px Inter, sans-serif",
                    stroke: "white"
                },
                    new go.Binding("text", "label"))
            )
        )
    );

    // Default node template
    myDiagram.nodeTemplate =
        $(go.Node, "Auto",
            {
                selectionAdorned: true,
                cursor: "pointer",
                click: (e, node) => onNodeClick(node),
                doubleClick: (e, node) => onNodeDoubleClick(node)
            },
            $(go.Shape, "RoundedRectangle", {
                fill: "#4f46e5",
                stroke: "#818cf8",
                strokeWidth: 2
            },
                new go.Binding("fill", "isCenter", (isCenter, obj) => {
                    if (obj.part.isSelected) return "#f59e0b";
                    return isCenter ? "#7c3aed" : "#4f46e5";
                })),
            $(go.Panel, "Vertical",
                { margin: 12 },
                $(go.TextBlock, {
                    font: "bold 14px Inter, sans-serif",
                    stroke: "white"
                },
                    new go.Binding("text", "label"))
            )
        );

    // Link template
    myDiagram.linkTemplate =
        $(go.Link,
            {
                routing: go.Link.AvoidsNodes,
                curve: go.Link.Bezier,
                corner: 10,
                selectable: true,
                click: (e, link) => onLinkClick(link)
            },
            $(go.Shape, {
                strokeWidth: 2,
                stroke: "#64748b"
            },
                new go.Binding("stroke", "isSelected", (sel) => sel ? "#f59e0b" : "#64748b").ofObject()),
            $(go.Shape, {
                toArrow: "Triangle",
                fill: "#64748b",
                stroke: null,
                scale: 1.2
            },
                new go.Binding("fill", "isSelected", (sel) => sel ? "#f59e0b" : "#64748b").ofObject()),
            $(go.Panel, "Auto",
                $(go.Shape, "RoundedRectangle", {
                    fill: "rgba(15, 15, 26, 0.9)",
                    stroke: null
                }),
                $(go.TextBlock, {
                    font: "11px Inter, sans-serif",
                    stroke: "#94a3b8",
                    margin: 4
                },
                    new go.Binding("text", "relationship"))
            )
        );

    // Selection changed event
    myDiagram.addDiagramListener("ChangedSelection", (e) => {
        const sel = e.diagram.selection.first();
        if (sel) {
            if (sel instanceof go.Node) {
                onNodeClick(sel);
            } else if (sel instanceof go.Link) {
                onLinkClick(sel);
            }
        }
    });
}

/**
 * Load graph data for a class
 */
async function loadGraphData(className) {
    try {
        const response = await fetch(`/api/graph-data/${encodeURIComponent(className)}`);
        if (!response.ok) throw new Error('Failed to load graph data');

        const data = await response.json();

        // Set the model
        myDiagram.model = new go.GraphLinksModel(data.nodes, data.links);

        // Hide placeholder
        document.getElementById('graph-placeholder').classList.add('hidden');

        // Display the query in the Query tab
        if (data.query) {
            updateQueryDisplay(data.query);
        }

        // Fit to view after layout
        setTimeout(() => {
            myDiagram.zoomToFit();
        }, 500);

    } catch (error) {
        console.error('Error loading graph:', error);
    }
}

/**
 * Update the Query tab with the last executed query
 */
function updateQueryDisplay(query) {
    const queryInput = document.getElementById('cypher-input');
    if (queryInput) {
        queryInput.value = query;
    }
}

/**
 * Handle node click - show properties
 */
function onNodeClick(node) {
    const data = node.data;
    showNodeProperties(data);
}

/**
 * Handle link click - show relationship properties
 */
function onLinkClick(link) {
    const data = link.data;
    showLinkProperties(data);
}

/**
 * Handle node double-click - load focused view with node and its direct connections
 */
async function onNodeDoubleClick(node) {
    const nodeLabel = node.data.label;
    if (!nodeLabel) return;

    try {
        const response = await fetch(`/api/node-focus/${encodeURIComponent(nodeLabel)}`);
        if (!response.ok) throw new Error('Failed to load node focus data');

        const data = await response.json();

        if (data.nodes.length === 0) {
            console.log('No focus data found for node:', nodeLabel);
            return;
        }

        // Set the model with focused data
        myDiagram.model = new go.GraphLinksModel(data.nodes, data.links);

        // Display the query in the Query tab
        if (data.query) {
            updateQueryDisplay(data.query);
        }

        // Fit to view after layout
        setTimeout(() => {
            myDiagram.zoomToFit();
        }, 500);

    } catch (error) {
        console.error('Error loading node focus:', error);
    }
}

/**
 * Display node properties in the right panel
 */
/**
 * Display node properties in the right panel
 */
function showNodeProperties(data) {
    const container = document.getElementById('properties-content');
    const props = data.properties || {};

    // Standard fields we want to show first
    let html = `
        <div class="property-section">
            <h3 class="${data.category === 'datatype' ? 'text-emerald-400' : 'text-indigo-400'}">
                ${data.category === 'datatype' ? 'Datatype' : 'Class'}: ${escapeHtml(data.label)}
            </h3>
    `;

    // Filtered properties (exclude already shown or technical)
    const technicalFields = ['key', 'category', 'isCenter', '__gohashid', 'materialized', 'rdfs__label', 'uri', 'skos__definition'];

    // Core fields
    html += `
        <div class="property-item">
            <div class="property-label">URI</div>
            <div class="property-value">
                <a href="${escapeHtml(data.uri)}" target="_blank" class="text-blue-400 hover:underline break-all">${escapeHtml(data.uri)}</a>
            </div>
        </div>
    `;

    if (data.definition) {
        html += `
            <div class="property-item">
                <div class="property-label">Definition</div>
                <div class="property-value">${escapeHtml(data.definition)}</div>
            </div>
        `;
    }

    // Dynamic fields from data.properties
    let dynamicFieldsHtml = '';
    for (const [key, value] of Object.entries(props)) {
        if (technicalFields.includes(key)) continue;

        dynamicFieldsHtml += `
            <div class="property-item">
                <div class="property-label">${escapeHtml(key)}</div>
                <div class="property-value">${escapeHtml(String(value))}</div>
            </div>
        `;
    }

    if (dynamicFieldsHtml) {
        html += `
            <div class="mt-4 pt-2 border-t border-slate-700">
                <h4 class="text-xs uppercase text-slate-500 font-bold mb-2">Metadata / Flattened Properties</h4>
                ${dynamicFieldsHtml}
            </div>
        `;
    }

    html += `</div>`;
    container.innerHTML = html;
}

/**
 * Display link/relationship properties in the right panel
 */
function showLinkProperties(data) {
    const container = document.getElementById('properties-content');
    const props = data.properties || {};

    let html = `
        <div class="property-section">
            <h3 class="text-amber-400">Relationship: ${escapeHtml(data.relationship)}</h3>
            <div class="property-item">
                <div class="property-label">From</div>
                <div class="property-value">${escapeHtml(data.from)}</div>
            </div>
            <div class="property-item">
                <div class="property-label">To</div>
                <div class="property-value">${escapeHtml(data.to)}</div>
            </div>
    `;

    const technicalFields = ['from', 'to', 'relationship', 'uri', 'skos__definition', 'materialized', 'materialized_path', '_rel_type', '__gohashid'];

    if (data.uri) {
        html += `
            <div class="property-item">
                <div class="property-label">URI</div>
                <div class="property-value">
                    <a href="${escapeHtml(data.uri)}" target="_blank" class="text-blue-400 hover:underline break-all">${escapeHtml(data.uri)}</a>
                </div>
            </div>
        `;
    }

    if (data.definition) {
        html += `
            <div class="property-item">
                <div class="property-label">Definition</div>
                <div class="property-value">${escapeHtml(data.definition)}</div>
            </div>
        `;
    }

    // Dynamic fields from data.properties
    let dynamicFieldsHtml = '';
    for (const [key, value] of Object.entries(props)) {
        if (technicalFields.includes(key)) continue;

        dynamicFieldsHtml += `
            <div class="property-item">
                <div class="property-label">${escapeHtml(key)}</div>
                <div class="property-value">${escapeHtml(String(value))}</div>
            </div>
        `;
    }

    if (dynamicFieldsHtml) {
        html += `
            <div class="mt-4 pt-2 border-t border-slate-700">
                <h4 class="text-xs uppercase text-slate-500 font-bold mb-2">Attributes</h4>
                ${dynamicFieldsHtml}
            </div>
        `;
    }

    html += `</div>`;
    container.innerHTML = html;
}

/**
 * Zoom controls
 */
function zoomIn() {
    if (myDiagram) myDiagram.commandHandler.increaseZoom();
}

function zoomOut() {
    if (myDiagram) myDiagram.commandHandler.decreaseZoom();
}

function fitView() {
    if (myDiagram) myDiagram.zoomToFit();
}

function refreshLayout() {
    if (myDiagram) {
        myDiagram.layoutDiagram(true);
    }
}

/**
 * Helper: Truncate text
 */
function truncate(str, length) {
    if (!str) return '';
    return str.length > length ? str.substring(0, length) + '...' : str;
}

/**
 * Helper: Escape HTML
 */
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

/**
 * Load graph from data object (used by chat responses)
 */
function loadGraphFromData(data) {
    if (!data || !data.nodes || data.nodes.length === 0) {
        console.log('No graph data to display');
        return;
    }

    // Set the model
    myDiagram.model = new go.GraphLinksModel(data.nodes, data.links || []);

    // Hide placeholder
    document.getElementById('graph-placeholder').classList.add('hidden');

    // Display the query in the Query tab if present
    if (data.query) {
        updateQueryDisplay(data.query);
    }

    // Fit to view after layout
    setTimeout(() => {
        myDiagram.zoomToFit();
    }, 500);
}

// Export functions for global access
window.initGraph = initGraph;
window.loadGraphData = loadGraphData;
window.loadGraphFromData = loadGraphFromData;
window.zoomIn = zoomIn;
window.zoomOut = zoomOut;
window.fitView = fitView;
window.refreshLayout = refreshLayout;
