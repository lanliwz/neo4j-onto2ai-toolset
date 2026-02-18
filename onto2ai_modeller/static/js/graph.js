/**
 * GoJS Graph Visualization for Onto2AI Modeller
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

    // Initial theme check
    const isLight = document.documentElement.classList.contains('light-mode');
    myDiagram.model.modelData.isLight = isLight;
    myDiagram.div.style.background = isLight ? "#f8fafc" : "#0f0f1a";

    // Node template for classes (Professional Rectangular Header Style)
    myDiagram.nodeTemplateMap.add("class",
        $(go.Node, "Auto",
            {
                selectionAdorned: true,
                cursor: "pointer",
                click: (e, node) => onNodeClick(node),
                doubleClick: (e, node) => onNodeDoubleClick(node)
            },
            $(go.Shape, "Rectangle", {
                fill: "#1a1a2e",
                stroke: "#4f46e5",
                strokeWidth: 2
            },
                new go.Binding("fill", "isCenter", (isCenter) => isCenter ? "#1e1b4b" : "#1a1a2e"),
                new go.Binding("fill", "isLight", (light) => light ? "#ffffff" : "#1a1a2e").ofModel(),
                new go.Binding("stroke", "isLight", (light, obj) => {
                    if (obj.part.data.isCenter) return light ? "#7c3aed" : "#7c3aed";
                    return light ? "#cbd5e1" : "#4f46e5";
                }).ofModel(),
                new go.Binding("stroke", "isSelected", (sel) => sel ? "#f59e0b" : "#4f46e5").ofObject()),
            $(go.Panel, "Vertical",
                { stretch: go.GraphObject.Fill, margin: 1 },
                // Header
                $(go.Panel, "Auto",
                    { stretch: go.GraphObject.Horizontal },
                    $(go.Shape, "Rectangle", { fill: "#4f46e5", stroke: null },
                        new go.Binding("fill", "isCenter", (isCenter) => isCenter ? "#7c3aed" : "#4f46e5")),
                    $(go.Panel, "Vertical",
                        $(go.TextBlock, {
                            font: "bold 13px Inter, sans-serif",
                            stroke: "white",
                            margin: 8,
                            alignment: go.Spot.Center
                        }, new go.Binding("text", "label"))
                    )
                ),
                // Definition Preview
                $(go.Panel, "Auto",
                    {
                        stretch: go.GraphObject.Horizontal,
                        margin: new go.Margin(0, 8, 8, 8),
                        visible: false
                    },
                    new go.Binding("visible", "definition", (d) => !!d),
                    $(go.TextBlock, {
                        font: "11px Inter, sans-serif",
                        stroke: "#94a3b8",
                        maxSize: new go.Size(160, NaN),
                        wrap: go.TextBlock.WrapFit,
                        alignment: go.Spot.Left
                    },
                        new go.Binding("stroke", "isLight", (light) => light ? "#475569" : "#94a3b8").ofModel(),
                        new go.Binding("text", "definition", (d) => d ? truncate(d, 60) : ""))
                )
            )
        )
    );

    // Node template for datatypes (Unified Rectangular Style)
    myDiagram.nodeTemplateMap.add("datatype",
        $(go.Node, "Auto",
            {
                selectionAdorned: true,
                cursor: "pointer",
                click: (e, node) => onNodeClick(node)
            },
            $(go.Shape, "Rectangle", {
                fill: "#1a1a2e",
                stroke: "#10b981",
                strokeWidth: 2
            },
                new go.Binding("fill", "isLight", (light) => light ? "#ffffff" : "#1a1a2e").ofModel(),
                new go.Binding("stroke", "isSelected", (sel) => sel ? "#f59e0b" : "#10b981").ofObject()),
            $(go.Panel, "Vertical",
                { stretch: go.GraphObject.Fill, margin: 1 },
                // Header
                $(go.Panel, "Auto",
                    { stretch: go.GraphObject.Horizontal },
                    $(go.Shape, "Rectangle", { fill: "#10b981", stroke: null }),
                    $(go.Panel, "Vertical",
                        $(go.TextBlock, {
                            font: "bold 12px Inter, sans-serif",
                            stroke: "white",
                            margin: 6,
                            alignment: go.Spot.Center
                        }, new go.Binding("text", "label"))
                    )
                ),
                // Stereotype Label
                $(go.TextBlock, {
                    font: "italic 10px Inter, sans-serif",
                    stroke: "#10b981",
                    margin: new go.Margin(4, 8, 4, 8),
                    alignment: go.Spot.Center
                }, "«datatype»")
            )
        )
    );

    // Node template for named individuals (Unified Capsule-Header Style)
    myDiagram.nodeTemplateMap.add("individual",
        $(go.Node, "Auto",
            {
                selectionAdorned: true,
                cursor: "pointer",
                click: (e, node) => onNodeClick(node)
            },
            $(go.Shape, "Rectangle", {
                fill: "#1a1a2e",
                stroke: "#0d9488",
                strokeWidth: 2
            },
                new go.Binding("fill", "isLight", (light) => light ? "#ffffff" : "#1a1a2e").ofModel(),
                new go.Binding("stroke", "isSelected", (sel) => sel ? "#f59e0b" : "#0d9488").ofObject()),
            $(go.Panel, "Vertical",
                { stretch: go.GraphObject.Fill, margin: 1 },
                // Header
                $(go.Panel, "Auto",
                    { stretch: go.GraphObject.Horizontal },
                    $(go.Shape, "Rectangle", { fill: "#0d9488", stroke: null }),
                    $(go.Panel, "Vertical",
                        $(go.TextBlock, {
                            font: "bold 12px Inter, sans-serif",
                            stroke: "white",
                            margin: 6,
                            alignment: go.Spot.Center
                        }, new go.Binding("text", "label"))
                    )
                ),
                // Stereotype Label
                $(go.TextBlock, {
                    font: "italic 10px Inter, sans-serif",
                    stroke: "#0d9488",
                    margin: new go.Margin(4, 8, 4, 8),
                    alignment: go.Spot.Center
                }, "«individual»")
            )
        )
    );

    // UML Style Template
    const umlPropertyTemplate = $(go.Panel, "Horizontal",
        $(go.TextBlock, {
            font: "11px Inter, sans-serif",
            margin: new go.Margin(0, 5, 0, 0)
        },
            new go.Binding("text", "name", (n) => `+ ${n}`),
            new go.Binding("stroke", "kind", (k, obj) => {
                const isLight = obj.diagram.model.modelData.isLight;
                if (k === "association") return isLight ? "#4338ca" : "#818cf8";
                return isLight ? "#065f46" : "#34d399";
            }).ofModel()),
        $(go.TextBlock, {
            font: "11px Inter, sans-serif",
            stroke: "#94a3b8"
        },
            new go.Binding("stroke", "isLight", (light) => light ? "#475569" : "#94a3b8").ofModel(),
            new go.Binding("text", "type", (t) => `: ${t}`))
    );

    myDiagram.nodeTemplateMap.add("uml",
        $(go.Node, "Auto",
            {
                selectionAdorned: true,
                cursor: "pointer",
                click: (e, node) => onNodeClick(node),
                doubleClick: (e, node) => onNodeDoubleClick(node)
            },
            $(go.Shape, "Rectangle", {
                fill: "#1a1a2e",
                stroke: "#4f46e5",
                strokeWidth: 2
            },
                new go.Binding("fill", "isCenter", (isCenter) => isCenter ? "#1e1b4b" : "#1a1a2e"),
                new go.Binding("fill", "isLight", (light) => light ? "#ffffff" : "#1a1a2e").ofModel(),
                new go.Binding("stroke", "isLight", (light, obj) => {
                    if (obj.part.data.isCenter) return light ? "#7c3aed" : "#7c3aed";
                    return light ? "#cbd5e1" : "#4f46e5";
                }).ofModel()),
            $(go.Panel, "Vertical",
                { stretch: go.GraphObject.Fill, margin: 1 },
                // Header
                $(go.Panel, "Auto",
                    { stretch: go.GraphObject.Horizontal },
                    $(go.Shape, "Rectangle", { fill: "#4f46e5", stroke: null },
                        new go.Binding("fill", "isCenter", (isCenter) => isCenter ? "#7c3aed" : "#4f46e5")),
                    $(go.Panel, "Vertical",
                        $(go.TextBlock, {
                            font: "italic 10px Inter, sans-serif",
                            stroke: "white",
                            margin: new go.Margin(4, 8, 0, 8),
                            alignment: go.Spot.Center,
                            visible: false
                        },
                            new go.Binding("visible", "is_enum"),
                            new go.Binding("text", "", () => "«enumeration»")),
                        $(go.TextBlock, {
                            font: "bold 13px Inter, sans-serif",
                            stroke: "white",
                            margin: 8,
                            alignment: go.Spot.Center
                        }, new go.Binding("text", "label"))
                    )
                ),
                // Attributes
                $(go.Panel, "Vertical",
                    {
                        stretch: go.GraphObject.Horizontal,
                        defaultAlignment: go.Spot.Left,
                        background: "rgba(0,0,0,0.3)",
                        padding: 8,
                        itemTemplate: umlPropertyTemplate
                    },
                    new go.Binding("background", "isLight", (light) => light ? "#f1f5f9" : "rgba(0,0,0,0.3)").ofModel(),
                    new go.Binding("itemArray", "attributes")
                )
            )
        )
    );

    // Pydantic Style Template (Code-like)
    const pydanticPropertyTemplate = $(go.Panel, "Horizontal",
        $(go.TextBlock, {
            font: "italic 11px 'Fira Code', monospace",
            margin: new go.Margin(0, 4, 0, 0)
        },
            new go.Binding("text", "name"),
            new go.Binding("stroke", "", (data, obj) => {
                const isLight = obj.diagram.model.modelData.isLight;
                if (data.kind === "association") return isLight ? "#4338ca" : "#818cf8";
                return isLight ? "#1e293b" : "#f1f5f9";
            })),
        $(go.TextBlock, {
            font: "11px 'Fira Code', monospace",
            stroke: "#a78bfa"
        },
            new go.Binding("stroke", "isLight", (light) => light ? "#6d28d9" : "#a78bfa").ofModel(),
            new go.Binding("text", "type", (t) => `: Optional[${t}] = None`))
    );

    myDiagram.nodeTemplateMap.add("pydantic",
        $(go.Node, "Auto",
            {
                selectionAdorned: true,
                cursor: "pointer",
                click: (e, node) => onNodeClick(node)
            },
            $(go.Shape, "Rectangle", {
                fill: "#0d1117",
                stroke: "#30363d",
                strokeWidth: 1
            },
                new go.Binding("fill", "isLight", (light) => light ? "#ffffff" : "#0d1117").ofModel(),
                new go.Binding("stroke", "isLight", (light) => light ? "#cbd5e1" : "#30363d").ofModel(),
                new go.Binding("stroke", "isSelected", (sel, obj) => {
                    if (sel) return "#f59e0b";
                    const isLight = obj.diagram.model.modelData.isLight;
                    return isLight ? "#cbd5e1" : "#30363d";
                }).ofObject()),
            $(go.Panel, "Vertical",
                { stretch: go.GraphObject.Fill, margin: 1 },
                // Class definition line
                $(go.Panel, "Auto",
                    { stretch: go.GraphObject.Horizontal },
                    $(go.Shape, "Rectangle", { fill: "#1e293b", stroke: null }),
                    $(go.Panel, "Vertical",
                        $(go.TextBlock, {
                            font: "italic 9px 'Fira Code', monospace",
                            stroke: "rgba(255,255,255,0.5)",
                            margin: new go.Margin(4, 8, 0, 8),
                            alignment: go.Spot.Center,
                            visible: false
                        },
                            new go.Binding("visible", "is_enum"),
                            new go.Binding("text", "", () => "@enumeration")),
                        $(go.TextBlock, {
                            font: "bold 12px 'Fira Code', monospace",
                            stroke: "#38bdf8",
                            margin: 8,
                            alignment: go.Spot.Center
                        }, new go.Binding("text", "label", (l) => {
                            const snake = l.toLowerCase().replace(/ /g, "_");
                            return snake.charAt(0).toUpperCase() + snake.slice(1).replace(/_([a-z])/g, (g) => g[1].toUpperCase());
                        }))
                    )
                ),
                // Docstring
                $(go.Panel, "Auto",
                    { stretch: go.GraphObject.Horizontal, margin: new go.Margin(0, 16, 8, 16) },
                    $(go.TextBlock, {
                        font: "italic 11px 'Fira Code', monospace",
                        stroke: "#8b949e",
                        maxSize: new go.Size(200, NaN),
                        wrap: go.TextBlock.WrapFit
                    },
                        new go.Binding("stroke", "isLight", (light) => light ? "#4b5563" : "#8b949e").ofModel(),
                        new go.Binding("text", "definition", (d) => d ? `\"\"\"\n${d}\n\"\"\"` : ""))
                ),
                // Fields
                $(go.Panel, "Vertical",
                    {
                        stretch: go.GraphObject.Horizontal,
                        defaultAlignment: go.Spot.Left,
                        padding: new go.Margin(4, 16, 8, 16),
                        itemTemplate: pydanticPropertyTemplate,
                        alignment: go.Spot.Left
                    },
                    new go.Binding("itemArray", "attributes")
                )
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
                    const isLight = obj.diagram.model.modelData.isLight;
                    if (isLight) return isCenter ? "#1e1b4b" : "#ffffff";
                    return isCenter ? "#7c3aed" : "#4f46e5";
                }).ofModel(),
                new go.Binding("stroke", "isCenter", (isCenter, obj) => {
                    const isLight = obj.diagram.model.modelData.isLight;
                    return isLight ? "#cbd5e1" : "#818cf8";
                }).ofModel()),
            $(go.Panel, "Vertical",
                { margin: 12 },
                $(go.TextBlock, {
                    font: "bold 14px Inter, sans-serif",
                    stroke: "white"
                },
                    new go.Binding("stroke", "isLight", (light, obj) => {
                        const isCenter = obj.part.data.isCenter;
                        if (light && !isCenter) return "#1e293b";
                        return "white";
                    }).ofModel(),
                    new go.Binding("text", "label"))
            )
        );

    // Default link template (association)
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
                new go.Binding("stroke", "isLight", (light) => light ? "#94a3b8" : "#64748b").ofModel(),
                new go.Binding("stroke", "isSelected", (sel, obj) => {
                    if (sel) return "#f59e0b";
                    const light = obj.diagram.model.modelData.isLight;
                    return light ? "#94a3b8" : "#64748b";
                }).ofObject()),
            $(go.Shape, {
                toArrow: "Triangle",
                fill: "#64748b",
                stroke: null,
                scale: 1.2
            },
                new go.Binding("fill", "isLight", (light) => light ? "#94a3b8" : "#64748b").ofModel(),
                new go.Binding("fill", "isSelected", (sel, obj) => {
                    if (sel) return "#f59e0b";
                    const light = obj.diagram.model.modelData.isLight;
                    return light ? "#94a3b8" : "#64748b";
                }).ofObject()),
            $(go.Panel, "Auto",
                $(go.Shape, "RoundedRectangle", {
                    fill: "rgba(15, 15, 26, 0.9)",
                    stroke: null
                }, new go.Binding("fill", "isLight", (light) => light ? "rgba(255, 255, 255, 0.9)" : "rgba(15, 15, 26, 0.9)").ofModel()),
                $(go.TextBlock, {
                    font: "11px Inter, sans-serif",
                    stroke: "#94a3b8",
                    margin: 4
                },
                    new go.Binding("stroke", "isLight", (light) => light ? "#475569" : "#94a3b8").ofModel(),
                    new go.Binding("text", "relationship"))
            )
        );

    // Inheritance link template (UML generalization: open triangle, dashed)
    myDiagram.linkTemplateMap.add("inheritance",
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
                stroke: "#a78bfa",
                strokeDashArray: [6, 3]
            },
                new go.Binding("stroke", "isSelected", (sel) => sel ? "#f59e0b" : "#a78bfa").ofObject()),
            $(go.Shape, {
                toArrow: "Triangle",
                fill: "white",
                stroke: "#a78bfa",
                strokeWidth: 1.5,
                scale: 1.4
            },
                new go.Binding("stroke", "isSelected", (sel) => sel ? "#f59e0b" : "#a78bfa").ofObject(),
                new go.Binding("fill", "isSelected", (sel) => sel ? "#f59e0b" : "white").ofObject()),
            $(go.Panel, "Auto",
                $(go.Shape, "RoundedRectangle", {
                    fill: "rgba(15, 15, 26, 0.9)",
                    stroke: null
                }, new go.Binding("fill", "isLight", (light) => light ? "rgba(255, 255, 255, 0.9)" : "rgba(15, 15, 26, 0.9)").ofModel()),
                $(go.TextBlock, {
                    font: "italic 10px Inter, sans-serif",
                    stroke: "#a78bfa",
                    margin: 3
                },
                    new go.Binding("stroke", "isLight", (light) => light ? "#6d28d9" : "#a78bfa").ofModel(),
                    "extends")
            )
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
        const model = new go.GraphLinksModel(data.nodes, data.links);

        // Preserve theme state
        const isLight = document.documentElement.classList.contains('light-mode');
        model.modelData.isLight = isLight;

        myDiagram.model = model;

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
        const model = new go.GraphLinksModel(data.nodes, data.links);

        // Preserve theme state
        const isLight = document.documentElement.classList.contains('light-mode');
        model.modelData.isLight = isLight;

        myDiagram.model = model;

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
            <h3 class="${data.category === 'datatype' ? 'text-emerald-400' : data.category === 'individual' ? 'text-teal-400' : 'text-indigo-400'}">
                ${data.category === 'datatype' ? 'Datatype' : data.category === 'individual' ? 'Individual' : 'Class'}: ${escapeHtml(data.label)}
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
    const model = new go.GraphLinksModel(data.nodes, data.links || []);

    // Preserve theme state
    const isLight = document.documentElement.classList.contains('light-mode');
    model.modelData.isLight = isLight;

    myDiagram.model = model;

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

/**
 * Change visualization mode (graph, uml, pydantic)
 */
function changeVizMode(mode) {
    if (!myDiagram) return;

    // Change category of all class nodes in the current model
    myDiagram.model.commit(m => {
        m.nodeDataArray.forEach(node => {
            if (node.category === 'class' || node.category === 'uml' || node.category === 'pydantic') {
                m.setCategoryForNodeData(node, mode === 'graph' ? 'class' : mode);
            }
        });
    }, "change viz mode");

    // Re-layout
    myDiagram.layoutDiagram(true);
}

/**
 * Load UML or Pydantic data (flattened)
 */
async function loadUmlData(className, mode) {
    try {
        const response = await fetch(`/api/uml-data/${encodeURIComponent(className)}`);
        if (!response.ok) throw new Error('Failed to load UML data');

        const data = await response.json();

        // Apply specialized category to all nodes except datatypes
        const nodes = data.nodes.map(n => ({
            ...n,
            category: mode // 'uml' or 'pydantic'
        }));

        // Set the model with link category support for inheritance arrows
        const model = new go.GraphLinksModel(nodes, data.links);
        model.linkCategoryProperty = "category";

        // Preserve theme state
        const isLight = document.documentElement.classList.contains('light-mode');
        model.modelData.isLight = isLight;

        myDiagram.model = model;

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
        console.error('Error loading UML/Pydantic data:', error);
    }
}

/**
 * Update the GoJS diagram theme
 */
function updateGraphTheme(isLight) {
    if (!myDiagram) return;

    myDiagram.commit(d => {
        d.model.modelData.isLight = isLight;
        d.div.style.background = isLight ? "#f8fafc" : "#0f0f1a";
    }, "change theme");
}

// Export functions for global access
window.initGraph = initGraph;
window.loadGraphData = loadGraphData;
window.loadUmlData = loadUmlData;
window.loadGraphFromData = loadGraphFromData;
window.changeVizMode = changeVizMode;
window.updateGraphTheme = updateGraphTheme;
window.zoomIn = zoomIn;
window.zoomOut = zoomOut;
window.fitView = fitView;
window.refreshLayout = refreshLayout;
