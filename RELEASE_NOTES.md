# Redemption Chronicle Maker 1.0.0-rc4

Create dynamic combats without writing Java. Use **+ Dynamic encounter…** in Campaign, assistants or the 3D ground menu. Choose a mode, enemies/count, spawn waypoints and activation. Boss phases use percentage or absolute health crossings and the existing action editor.

The original Generator was found and studied. RCM uses confirmed factories, timers, capture/death callbacks, health and native save records with bounded ownership tracking and retries. Defaults retain original health/AI. Existing authored encounters and geometry are preserved.

Format 9 opens unchanged. The first dynamic encounter opts into format 10 with backup and undo. Structural changes may require a new game; saves are not migrated.

The accepted Quick tutorial is preserved. Open examples/dynamic_lab/project.yaml for the independent combat lab or select the optional dynamic station from the Showcase Guide. Weak original Rats are used; example bosses have increased health to make thresholds visible.

**MANUAL RUNTIME TEST REQUIRED.** Native combat/save ownership remain unaccepted. A lethal hit may skip a threshold; no universal before-death interception is promised. Waves advance on clear. Arbitrary random-volume positions, overlapping/manual advance inside one wave list, direct dynamic-role camera targets and per-entry delay/AI overrides are unavailable. Use separate generators/events and existing action targets where appropriate.

Projects live outside the program. Settings selects English/Spanish. No original authoring tools or game assets are distributed. Local single-player candidate; networking, independent-PC, physical DPI and real GPU validation remain pending. Not final 1.0.
