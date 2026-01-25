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
                click: (e, node) => onNodeClick(node)
            },
            $(go.Shape, "RoundedRectangle", {
                fill: "#4f46e5",
                stroke: "#818cf8",
                strokeWidth: 2,
                portId: "",
                fromLinkable: true,
                toLinkable: true
            },
                new go.Binding("fill", "isSelected", (sel) => sel ? "#f59e0b" : "#4f46e5").ofObject()),
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
                click: (e, node) => onNodeClick(node)
            },
            $(go.Shape, "RoundedRectangle", {
                fill: "#4f46e5",
                stroke: "#818cf8",
                strokeWidth: 2
            }),
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

        // Fit to view after layout
        setTimeout(() => {
            myDiagram.zoomToFit();
        }, 500);

    } catch (error) {
        console.error('Error loading graph:', error);
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
 * Display node properties in the right panel
 */
function showNodeProperties(data) {
    const container = document.getElementById('properties-content');

    container.innerHTML = `
        <div class="property-section">
            <h3>Class Information</h3>
            <div class="property-item">
                <div class="property-label">Label</div>
                <div class="property-value">${escapeHtml(data.label)}</div>
            </div>
            <div class="property-item">
                <div class="property-label">URI</div>
                <div class="property-value">
                    <a href="${escapeHtml(data.uri)}" target="_blank">${escapeHtml(data.uri)}</a>
                </div>
            </div>
            ${data.definition ? `
            <div class="property-item">
                <div class="property-label">Definition</div>
                <div class="property-value">${escapeHtml(data.definition)}</div>
            </div>
            ` : ''}
            <div class="property-item">
                <div class="property-label">Type</div>
                <div class="property-value">${data.category === 'datatype' ? 'Datatype' : 'Class'}</div>
            </div>
        </div>
    `;
}

/**
 * Display link/relationship properties in the right panel
 */
function showLinkProperties(data) {
    const container = document.getElementById('properties-content');

    container.innerHTML = `
        <div class="property-section">
            <h3>Relationship</h3>
            <div class="property-item">
                <div class="property-label">Type</div>
                <div class="property-value">${escapeHtml(data.relationship)}</div>
            </div>
            <div class="property-item">
                <div class="property-label">From</div>
                <div class="property-value">${escapeHtml(data.from)}</div>
            </div>
            <div class="property-item">
                <div class="property-label">To</div>
                <div class="property-value">${escapeHtml(data.to)}</div>
            </div>
            ${data.uri ? `
            <div class="property-item">
                <div class="property-label">URI</div>
                <div class="property-value">
                    <a href="${escapeHtml(data.uri)}" target="_blank">${escapeHtml(data.uri)}</a>
                </div>
            </div>
            ` : ''}
            ${data.definition ? `
            <div class="property-item">
                <div class="property-label">Definition</div>
                <div class="property-value">${escapeHtml(data.definition)}</div>
            </div>
            ` : ''}
            ${data.cardinality ? `
            <div class="property-item">
                <div class="property-label">Cardinality</div>
                <div class="property-value">${escapeHtml(data.cardinality)}</div>
            </div>
            ` : ''}
            ${data.requirement ? `
            <div class="property-item">
                <div class="property-label">Requirement</div>
                <div class="property-value">${escapeHtml(data.requirement)}</div>
            </div>
            ` : ''}
        </div>
    `;
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

// Export functions for global access
window.initGraph = initGraph;
window.loadGraphData = loadGraphData;
window.zoomIn = zoomIn;
window.zoomOut = zoomOut;
window.fitView = fitView;
window.refreshLayout = refreshLayout;
