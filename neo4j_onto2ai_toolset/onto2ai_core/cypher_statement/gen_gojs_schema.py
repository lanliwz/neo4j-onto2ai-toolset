crt_panel_type="""
CREATE (:Panel {type: 'Position'}),
       (:Panel:Node {type: 'Vertical'}),
       (:Panel:Node {type: 'Horizontal'}),
       (:Panel:Node {type: 'Auto'}),
       (:Panel {type: 'Spot'}),
       (:Panel {type: 'Table'}),
       (:Panel {type: 'Viewbox'}),
       (:Panel:Link {type: 'Link'}),
       (:Panel {type: 'TableRow'}),
       (:Panel {type: 'TableColumn'}),
       (:Panel {type: 'Grid'}),
       (:Panel {type: 'Graduated'});
"""
crt_panel_constraint="""
CREATE CONSTRAINT panel_type_immutable
FOR (p:Panel)
REQUIRE p.type IS UNIQUE;
"""

crt_shape_figure="""
CREATE (:Shape {figure: 'Rectangle'}),
       (:Shape {figure: 'RoundedRectangle'}),
       (:Shape {figure: 'Capsule'}),
       (:Shape {figure: 'Ellipse'}),
       (:Shape {figure: 'Diamond'}),
       (:Shape {figure: 'TriangleRight'}),
       (:Shape {figure: 'TriangleDown'}),
       (:Shape {figure: 'TriangleLeft'}),
       (:Shape {figure: 'TriangleUp'}),
       (:Shape {figure: 'MinusLine'}),
       (:Shape {figure: 'PlusLine'}),
       (:Shape {figure: 'XLine'});
"""
crt_data_property_node="""
//add gojs__DataProperty
MATCH (g:owl__Class {rdfs__label: 'graph object'})
WITH g, [
  {name: 'actionCancel', type: 'event'},
  {name: 'actionDown', type: 'event'},
  {name: 'actionMove', type: 'event'},
  {name: 'actionUp', type: 'event'},
  {name: 'actualBounds', type: 'object'},
  {name: 'alignment', type: 'string'},
  {name: 'alignmentFocus', type: 'string'},
  {name: 'angle', type: 'number'},
  {name: 'background', type: 'string'},
  {name: 'click', type: 'event'},
  {name: 'column', type: 'number'},
  {name: 'columnSpan', type: 'number'},
  {name: 'contextClick', type: 'event'},
  {name: 'contextMenu', type: 'object'},
  {name: 'cursor', type: 'string'},
  {name: 'desiredSize', type: 'object'},
  {name: 'diagram', type: 'object'},
  {name: 'doubleClick', type: 'event'},
  {name: 'enabledChanged', type: 'event'},
  {name: 'fromEndSegmentLength', type: 'number'},
  {name: 'fromLinkable', type: 'boolean'},
  {name: 'fromLinkableDuplicates', type: 'boolean'},
  {name: 'fromLinkableSelfNode', type: 'boolean'},
  {name: 'fromMaxLinks', type: 'number'},
  {name: 'fromShortLength', type: 'number'},
  {name: 'fromSpot', type: 'string'},
  {name: 'height', type: 'number'},
  {name: 'isActionable', type: 'boolean'},
  {name: 'isPanelMain', type: 'boolean'},
  {name: 'layer', type: 'object'},
  {name: 'margin', type: 'number'},
  {name: 'maxSize', type: 'object'},
  {name: 'measuredBounds', type: 'object'},
  {name: 'minSize', type: 'object'},
  {name: 'mouseDragEnter', type: 'event'},
  {name: 'mouseDragLeave', type: 'event'},
  {name: 'mouseDrop', type: 'event'},
  {name: 'mouseEnter', type: 'event'},
  {name: 'mouseHold', type: 'event'},
  {name: 'mouseHover', type: 'event'},
  {name: 'mouseLeave', type: 'event'},
  {name: 'mouseOver', type: 'event'},
  {name: 'name', type: 'string'},
  {name: 'naturalBounds', type: 'object'},
  {name: 'opacity', type: 'number'},
  {name: 'panel', type: 'object'},
  {name: 'part', type: 'object'},
  {name: 'pickable', type: 'boolean'},
  {name: 'portId', type: 'string'},
  {name: 'position', type: 'object'},
  {name: 'row', type: 'number'},
  {name: 'rowSpan', type: 'number'},
  {name: 'scale', type: 'number'},
  {name: 'segmentFraction', type: 'number'},
  {name: 'segmentIndex', type: 'number'},
  {name: 'segmentOffset', type: 'object'},
  {name: 'segmentOrientation', type: 'string'},
  {name: 'shadowVisible', type: 'boolean'},
  {name: 'stretch', type: 'string'},
  {name: 'toEndSegmentLength', type: 'number'},
  {name: 'toLinkable', type: 'boolean'},
  {name: 'toLinkableDuplicates', type: 'boolean'},
  {name: 'toLinkableSelfNode', type: 'boolean'},
  {name: 'toMaxLinks', type: 'number'},
  {name: 'toShortLength', type: 'number'},
  {name: 'toSpot', type: 'string'},
  {name: 'toolTip', type: 'object'},
  {name: 'visible', type: 'boolean'},
  {name: 'width', type: 'number'}
] AS properties
FOREACH (prop IN properties |
    MERGE (p:gojs_DataProperty {name: prop.name, type: prop.type})
    MERGE (g)-[:gojs__dataProperty]->(p)
);
"""
crt_data_property_panel="""
MATCH (g:owl__Class {rdfs__label: 'panel'})
WITH g, [
  {name: 'alignmentFocusName', type: 'string'},
  {name: 'columnCount', type: 'number'},
  {name: 'columnSizing', type: 'string'},
  {name: 'data', type: 'object'},
  {name: 'defaultAlignment', type: 'string'},
  {name: 'defaultColumnSeparatorDashArray', type: 'array'},
  {name: 'defaultColumnSeparatorStroke', type: 'string'},
  {name: 'defaultColumnSeparatorStrokeWidth', type: 'number'},
  {name: 'defaultRowSeparatorDashArray', type: 'array'},
  {name: 'defaultRowSeparatorStroke', type: 'string'},
  {name: 'defaultRowSeparatorStrokeWidth', type: 'number'},
  {name: 'defaultSeparatorPadding', type: 'number'},
  {name: 'defaultStretch', type: 'string'},
  {name: 'elements', type: 'array'},
  {name: 'graduatedMax', type: 'number'},
  {name: 'graduatedMin', type: 'number'},
  {name: 'graduatedRange', type: 'number'},
  {name: 'graduatedTickBase', type: 'number'},
  {name: 'graduatedTickUnit', type: 'number'},
  {name: 'gridCellSize', type: 'object'},
  {name: 'gridOrigin', type: 'object'},
  {name: 'isClipping', type: 'boolean'},
  {name: 'isEnabled', type: 'boolean'},
  {name: 'isOpposite', type: 'boolean'},
  {name: 'itemArray', type: 'array'},
  {name: 'itemCategoryProperty', type: 'string'},
  {name: 'itemIndex', type: 'number'},
  {name: 'itemTemplate', type: 'object'},
  {name: 'itemTemplateMap', type: 'object'},
  {name: 'leftIndex', type: 'number'},
  {name: 'padding', type: 'number'},
  {name: 'rowCount', type: 'number'},
  {name: 'rowSizing', type: 'string'},
  {name: 'topIndex', type: 'number'},
  {name: 'type', type: 'string'},
  {name: 'viewboxStretch', type: 'string'}
] AS properties
FOREACH (prop IN properties |
    MERGE (p:gojs_DataProperty {name: prop.name, type: prop.type})
    MERGE (g)-[:gojs__dataProperty]->(p)
);
"""
crt_data_property_part="""
MATCH (n:owl__Class {rdfs__label: 'part'})
FOREACH (prop IN [
  {name: 'actualBounds', type: 'Rect'},
  {name: 'contextMenu', type: 'Adornment'},
  {name: 'visible', type: 'boolean'},
  {name: 'position', type: 'Point'},
  {name: 'location', type: 'Point'},
  {name: 'layerName', type: 'string'},
  {name: 'zOrder', type: 'number'},
  {name: 'isSelected', type: 'boolean'},
  {name: 'selectable', type: 'boolean'},
  {name: 'movable', type: 'boolean'},
  {name: 'resizable', type: 'boolean'},
  {name: 'rotatable', type: 'boolean'},
  {name: 'deletable', type: 'boolean'},
  {name: 'copyable', type: 'boolean'},
  {name: 'shadowOffset', type: 'Point'},
  {name: 'shadowBlur', type: 'number'},
  {name: 'shadowColor', type: 'Brush'}
] |
  MERGE (p:gojs__DataProperty {name: prop.name, type: prop.type})
  MERGE (n)-[:gojs__dataProperty]->(p)
)
"""
crt_theme_dark="""
//To create a (:Theme {name: 'dark'}) node and link it to separate nodes 
//representing colors, fonts, numbers, and margins using camel case relationships
MERGE (t:Theme {name: 'dark'})

FOREACH (prop IN [
  {key: 'text', value: '#f5f5f5'},
  {key: 'comment', value: '#facc15'},
  {key: 'link', value: '#f5f5f5'},
  {key: 'group', value: '#a3a3a388'},
  {key: 'outline', value: '#a3a3a3'},
  {key: 'selection', value: '#38bdf8'},
  {key: 'div', value: '#171717'},
  {key: 'gridMinor', value: '#262626'},
  {key: 'gridMajor', value: '#404040'},
  {key: 'overviewBox', value: '#e879f9'},
  {key: 'tempLink', value: '#60a5fa'},
  {key: 'tempPort', value: '#e879f9'},
  {key: 'adornmentFill', value: '#38bdf8'},
  {key: 'adornmentStroke', value: '#2563eb'},
  {key: 'dragSelect', value: '#e879f9'}
] |
  MERGE (c:Color {name: prop.key, value: prop.value})
  MERGE (t)-[:hasColor]->(c)
)

FOREACH (prop IN [
  {key: 'normal', value: '10pt sans-serif'},
  {key: 'bold', value: 'bold 12pt sans-serif'}
] |
  MERGE (f:Font {name: prop.key, value: prop.value})
  MERGE (t)-[:hasFont]->(f)
)

FOREACH (prop IN [
  {key: 'group', value: 1},
  {key: 'selection', value: 3}
] |
  MERGE (n:NumberProperty {name: prop.key, value: prop.value})
  MERGE (t)-[:hasNumber]->(n)
)

MERGE (m:Margin {name: 'group', value: 5})
MERGE (t)-[:hasMargin]->(m)
"""
crt_theme_light="""
//To create a (:Theme {name: 'light'}) node and link it to separate nodes 
//representing colors, fonts, numbers, and margins using camel case relationships
MERGE (t:Theme {name: 'light'})

FOREACH (prop IN [
  {key: 'text', value: '#0a0a0a'},
  {key: 'comment', value: '#ca8a04'},
  {key: 'link', value: '#0a0a0a'},
  {key: 'group', value: '#a3a3a344'},
  {key: 'outline', value: '#a3a3a3'},
  {key: 'selection', value: '#0ea5e9'},
  {key: 'div', value: '#fff'},
  {key: 'gridMinor', value: '#e5e5e5'},
  {key: 'gridMajor', value: '#a3a3a3'},
  {key: 'overviewBox', value: '#c026d3'},
  {key: 'tempLink', value: '#2563eb'},
  {key: 'tempPort', value: '#c026d3'},
  {key: 'adornmentFill', value: '#0ea5e9'},
  {key: 'adornmentStroke', value: '#1e40af'},
  {key: 'dragSelect', value: '#c026d3'}
] |
  MERGE (c:Color {name: prop.key, value: prop.value})
  MERGE (t)-[:hasColor]->(c)
)

FOREACH (prop IN [
  {key: 'normal', value: '10pt sans-serif'},
  {key: 'bold', value: 'bold 12pt sans-serif'}
] |
  MERGE (f:Font {name: prop.key, value: prop.value})
  MERGE (t)-[:hasFont]->(f)
)

FOREACH (prop IN [
  {key: 'group', value: 1},
  {key: 'selection', value: 3}
] |
  MERGE (n:NumberProperty {name: prop.key, value: prop.value})
  MERGE (t)-[:hasNumber]->(n)
)

MERGE (m:Margin {name: 'group', value: 5})
MERGE (t)-[:hasMargin]->(m)

MERGE (a:Arrowhead {name: 'toArrow', value: 'Standard'})
MERGE (t)-[:hasArrowhead]->(a)
"""