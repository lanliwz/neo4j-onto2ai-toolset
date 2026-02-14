---
name: "UI Design Best Practices"
description: "Guidelines and patterns for implementing modern, theme-aware, and accessible UI components in Onto2AI Model Manager."
---
# UI Design Best Practices

Use these instructions when designing or modifying the Model Manager UI, especially when implementing themes, complex visualizations, or interactive components.

## 1. Modern Theming (CSS)
Always implement a dual-theme system (Dark/Light) using CSS variables.
- **Root Variables**: Define default dark theme variables in `:root`.
- **Light Mode Overrides**: Define light theme overrides in `:root.light-mode`.
- **Transitions**: Apply smooth transitions to interactive elements:
  ```css
  * { transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease; }
  ```

## 2. GoJS Theme Synchronization
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

## 3. Contrast & Accessibility
Ensure all text and diagram elements provide sufficient contrast in both themes.
- **Attributes & Datatypes**: Use theme-aware colors for text.
  - *Light Mode*: Dark green (`#065f46`) for attribute names, slate (`#475569`) for types.
  - *Dark Mode*: Bright green (`#34d399`) for attribute names, light slate (`#94a3b8`) for types.
- **Relationship Labels**: For labels over lines (like "extends"), use a theme-aware background shape to ensure text remains readable regardless of the line color.
  - *Light Mode Background*: `rgba(255, 255, 255, 0.9)`
  - *Dark Mode Background*: `rgba(15, 15, 26, 0.9)`

## 4. UI Layout & Transitions
- **Glassmorphism**: Use semi-transparent backgrounds with backdrop filters for a premium feel in dark mode.
- **Animations**: Use micro-animations for hover states and transitions between views.
- **Responsive Splitters**: Use the `split.js` pattern for resizable panels.

## 5. Implementation Workflow
1.  Define/Update CSS variables in `styles.css`.
2.  Implement theme toggle logic in `app.js`.
3.  Update GoJS templates in `graph.js` with theme bindings.
4.  Verify contrast in both modes using the browser subagent.
