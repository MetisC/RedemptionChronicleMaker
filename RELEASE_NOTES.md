# Redemption Chronicle Maker 1.0.0-rc9

This release improves everyday actor and object authoring in the desktop editor.

- **Choose once:** an actor/object selected while the level is loading stays queued. When loading finishes, click the floor to place it. Escape or changing project/scene cancels the pending placement.
- **Preview before placing:** the resource picker displays the actual NOD model with its original textures. Turn the preview with the arrow buttons. Loading runs in the background; browsing does not modify the chronicle. This is a static model preview, not an animation preview.
- **Smooth rotation:** free rotation is the default. Set an angle step to enable snapping. Dragging no longer serializes the entire chronicle on every mouse move; each drag has one undo step.
- **Contextual conversations:** right-click an authored actor or object in the 3D view or project tree and choose **+ Conversation**. The actor is bound directly. For objects, choose the character who speaks when clicked. Ordinary actions are preserved; replacing a note, cutscene or journey requires confirmation and supports undo.

## Verification and compatibility

The complete offline gate passed **648 tests, with zero failures, errors or skips**, plus Ruff and the configured mypy checks.

A final focused pass also passed **15 actor-authoring/preview regressions**, including cache invalidation when project resources change.

Automated editor regressions cover first acceptance, delayed placement, cancellation, previews, original textures/UVs, continuous rotation, undo and dialogue bindings. Complete gate results and portable verification are recorded with the release evidence in the repository.

The accepted format-9 tutorial and mini chronicle are preserved. Dynamic encounters remain opt-in format 10. Original game/mod assets are not included in the application ZIP. Original geometry remains immutable; no legacy authoring tools are required.

This remains a release candidate. Native save/load, re-entry, encounters, multiplayer and the other cases in the manual checklist still require user acceptance. Offline tests and portable startup checks do not certify gameplay or another PC/GPU/DPI configuration.
