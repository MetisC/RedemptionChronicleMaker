# Release candidate limits

**CORE 1.0:** arrivals, NPCs/objects, inventory, RETURN/flag dialogues, notes, journal/quests, conditional triggers, presets and Player shot sequences, simple encounters, once rewards, travel/arrival, contract-based saves, GUI/undo, build/deploy and portable.

**ADVANCED / EXPERIMENTAL:** NOT editing with unknown-byte preservation; supported original doors; conservative static handling; geometry-specific original NCP playback; model-specific animation slots; existing AI and positioned sounds. Compilation and format readback do not verify every native field.

**POST-1.0:** NCP writer, arbitrary XYZ/FOV cameras, universal doors, full static ALL/NONE/SELECTIVE, advanced AI/audio, verified replicated networking and native save migration. Geometry editing stays out of scope.

Local adventures load through the game's Multiplayer/LAN menu. This does not establish multi-client network support. Use one local player. The new tutorial requires a fresh game. Previous chronicles and Crypt profiles are not deleted; old tutorial templates remain available to avoid orphaned character profiles when opening LAN.

Human checks remain for camera framing/collision, loaded position, dialogue abort/cursor/control, reentry, rewards and a separate-machine portable run. Neither Embrace parity nor final 1.0 is claimed while these core acceptance checks remain open.

Original objects: a picker and actions can hide/restore/remove identified props, operate framed/pivot doors and create native hover/click interactions with travel or other event actions. This cannot remove NIL faces or synchronize Door/PivotDoor private state. ORG01–06 remain pending; the engine may reject a missing candidate or a door without the required frames.

CLICK01–08: hover, selection/collision, click range, dialogue/notes, native saves, reentry and multiplayer remain manual checks for the new brush layer. Self-scene links are blocked before building; old user proximity triggers are not silently migrated.
