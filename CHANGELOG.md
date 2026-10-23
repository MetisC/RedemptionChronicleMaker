# Changes · 1.0.0-rc9

- Keep the chosen actor/object while the 3D level is loading; the first acceptance arms placement as soon as the level is ready. Escape, failed loads and project/scene changes cancel pending placement.
- Preview real textured NOD models in the resource picker, with turntable buttons, asynchronous loading, complete framing on resize and stale-result protection. Cached previews are invalidated when project resources or the installation change. Browsing does not add entities to the project.
- Rotate freely by default, with optional degree snapping. Dragging updates the viewport immediately and records one undo operation on release instead of serializing the project on every mouse move.
- Create and bind conversations from the viewport/project-tree context menu for authored actors and objects. Objects choose a speaking character. Preserve ordinary actions; confirm replacing an existing note, cutscene or journey.
- Preserve the accepted tutorial, mini chronicle, geometry and generated runtime contracts. Manual native acceptance remains separate.

No geometry editing or original authoring tools. Native game acceptance remains subject to the manual checklist; this is not final 1.0.
