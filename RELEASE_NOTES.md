# Redemption Chronicle Maker 1.0.0-rc5

This release builds on RC4 and includes the latest editor safety and deletion workflow improvements.

The main change is a unified **safe delete** flow across the editor, 3D viewport and campaign tools. Before removing referenced content, RCM now previews incoming references, lets you navigate to them, applies validated cascade rules where supported, removes empty events when appropriate, preserves unrelated references and blocks unsafe removals instead of leaving the project in an invalid state. Deletions remain undoable.

RC5 keeps the RC4 dynamic encounter system intact: ambushes, waves, continuous generators, reinforcements and boss phases continue to use confirmed Redemption runtime behaviour and the existing event/action system. Existing authored encounters and original geometry are preserved.

Format 9 remains supported. Dynamic encounters use format 10 as before. The accepted Quick tutorial is preserved, and the dedicated dynamic encounter lab remains available for native-game testing.

**MANUAL RUNTIME TEST REQUIRED** still applies to engine-specific behaviour that cannot be fully proven offline, especially native save/load ownership, re-entry, collision/pathfinding for spawned actors and networking. A lethal hit may skip a health threshold; no universal before-death interception is promised.

Projects live outside the program folder. RCM does not distribute original Vampire: The Masquerade — Redemption assets or the original authoring tools. This remains a release candidate rather than final 1.0.
