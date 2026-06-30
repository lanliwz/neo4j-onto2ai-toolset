---
name: "UI Design Best Practices"
description: "Guidelines and patterns for implementing modern, theme-aware, and accessible UI components in Onto2AI Modeller."
---
# UI Design Best Practices

Use these instructions when designing or modifying the Modeller UI, especially when implementing themes, complex visualizations, or interactive components.

## Product Surface
Onto2AI Modeller is a workbench for adapting source ontologies into target ontologies and application code models. The UI should prioritize inspection, selection, refinement, and validation over dashboard-style summaries.

Use the current visible names consistently:
- `Source Ontology`
- `Target Ontology`
- `Semantic Interaction`
- `Native Query`
- `Ontology View`

For Source Ontology, keep UML Diagram and Pydantic Models disabled. Source Ontology should stay focused on Ontology View, source search, concept preview, and extraction seeds.

## Modern Theming (CSS)
Always implement a dual-theme system (Dark/Light) using CSS variables.
- **Root Variables**: Define default dark theme variables in `:root`.
- **Light Mode Overrides**: Define light theme overrides in `:root.light-mode`.
- **Transitions**: Apply smooth transitions to interactive elements:
  ```css
  * { transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease; }
  ```

## GoJS Theme Synchronization
When working with GoJS diagrams, synchronize the visual state with the application theme.
- **Model State**: Store the theme state in the diagram's `modelData`:
  ```javascript
  myDiagram.model.modelData.isLight = document.documentElement.classList.contains('light-mode');
  ```
- **Theme-Aware Bindings**: Use `.ofModel()` bindings to react to theme changes:
  ```javascript
  new go.Binding("fill", "isLight", (light) => light ? "#ffffff" : "#1a1a2e").ofModel()
  ```
- **State Preservation (CRITICAL)**: When replacing the diagram model (e.g., loading new data), ALWAYS re-set the `isLight` property from the current DOM state to prevent visual desync.
- **Zoom Behavior (CRITICAL)**: Preserve readable font sizes and line widths during zoom. Scale node geometry and positions without letting text strokes become too small or too large.
- **Viewport Stability (CRITICAL)**: Zoom in/out should keep the diagram centered on the user's visual focus. Avoid model replacement, layout re-run, or viewport reset during zoom interactions.

## Contrast & Accessibility
Ensure all text and diagram elements provide sufficient contrast in both themes.
- **Attributes & Datatypes**: Use theme-aware colors for text.
  - *Light Mode*: Dark green (`#065f46`) for attribute names, slate (`#475569`) for types.
  - *Dark Mode*: Bright green (`#34d399`) for attribute names, light slate (`#94a3b8`) for types.
- **Relationship Labels**: For labels over lines (like "extends"), use a theme-aware background shape to ensure text remains readable regardless of the line color.
  - *Light Mode Background*: `rgba(255, 255, 255, 0.9)`
  - *Dark Mode Background*: `rgba(15, 15, 26, 0.9)`

## UI Layout & Transitions
- **Workbench Density**: Favor navigator-style layouts with left catalog/search, center ontology view/detail, and right inspector/properties when the workflow involves browsing concepts.
- **Glassmorphism**: Use semi-transparent backgrounds sparingly. Do not let decorative style reduce legibility or density.
- **Animations**: Use micro-animations for hover states and transitions between views, but avoid motion that makes diagrams jump.
- **Responsive Splitters**: Use the `split.js` pattern for resizable panels.
- **URI Display**: Treat URIs as unique identifiers. Display them as selectable text, not links, unless a surface is explicitly intended for web navigation.
- **Configuration**: LLM model lists and defaults should be populated from `onto2ai_modeller/config.yaml`, not hard-coded in frontend code.
- **LLM Errors**: When chat fails, show provider, model, status/category, and a practical next action. Quota and missing-key failures should not look like generic chat failures.

## Implementation Workflow
1.  Define/Update CSS variables in `styles.css`.
2.  Implement theme toggle logic in `app.js`.
3.  Update GoJS templates in `graph.js` with theme bindings.
4.  Keep API response handling in sync with `onto2ai_modeller/api/schemas.py`.
5.  Verify contrast, tab state, zoom stability, and text overlap in both modes using a browser check when UI behavior changes.
