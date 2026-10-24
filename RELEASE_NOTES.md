# Redemption Chronicle Maker 1.0.0-rc10

This release makes linked story behaviour easier to author and removes interruptions while editing text.

- **Write smoothly:** names, dialogue, descriptions and other authored fields apply after editing, only when changed. Save, validation and builds commit pending edits. Typing no longer rebuilds the project on every key.
- **Stay in the conversation:** creating a contextual conversation opens its editor immediately; deleting a node keeps that conversation open.
- **Act on a response:** a RETURN response can run ordinary actions after the dialogue ends. Make the speaker hostile with one button, or configure inventory, quests, notes, travel and other effects. Cancelled dialogue does not execute the response.
- **React to flags:** choose actions when a flag becomes enabled or disabled. The storage index is clearly distinguished from its boolean state. Hostile/neutral behaviour presets manage the original actor team and AI flags.
- **Link from the source:** actors, objects, areas, conversations and scenes offer linked actions. Campaign / Overview adds quest states/steps, defeated groups, timeline/travelling completion and optional dynamic encounter callbacks. Configure actions, extra conditions and repetition together; View event opens the ordinary underlying event.
- **Keep existing work:** shortcuts reuse routes and preserve filters, conditions, references, cancel, unchanged OK and undo. Native-script regions retain ownership of their callbacks. Object conversation buttons use the same speaker selection and immediate editing as the context menu.

See the editor guide for examples such as a cutscene spawning an encounter, an enemy death granting loot, leaving an area restoring music, and quest progression changing flags.

## Verification and compatibility

The complete offline gate passed **706 tests, with zero failures, errors or skips**, plus Ruff and the configured mypy checks. Local verification also includes Qt authoring regressions, compilation against the real Codex API and packaged-source/translation verification. Release evidence records the exact results. GitHub Actions builds and publishes this prerelease from its version tag and verifies the bundled sources before packaging.

The accepted format-9 tutorial and mini chronicle are preserved. Dynamic encounters remain opt-in format 10. Original game/mod assets are not included in the application ZIP. Original geometry remains immutable; no legacy authoring tools are required.

This remains a release candidate. New DLGFX01–03/QOL01–04 and existing native save/load, re-entry, encounters, multiplayer and manual cases still require user acceptance. Offline tests, doubles, compilation, CI and portable startup checks do not certify gameplay or another PC/GPU/DPI configuration.
