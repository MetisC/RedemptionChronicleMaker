# Using the editor

**Welcome:** create, open or return to a recent project. Tutorial and Showcase are working copies: creating a clean copy preserves earlier work.

**3D Space:** place entries, NPCs, objects and trigger areas on the ground. Start focuses the player entry. F focuses selection. Original geometry cannot be modified.

**Story / Resources:** select an actor, conversation, node or answer and edit Properties. Tooltips show complete text. Filter resources by type, family and origin; save favourites.

**Campaign / Overview:** create scenes, travel, paths, quests, encounters and cinematic sequences. Assistants create ordinary editable, undoable relationships. Reopening an assistant reads current entity values.

**Graph:** shows conversation branches or an event's action order. Select a card to edit it. Fit view frames the graph.

**Delete:** select an element and press Delete or the Delete button. Its basic spawn actions are removed together. For cross-references, the dialog shows where it is used and what would be removed: go directly to a use, cancel, or choose “Delete and remove references”. Empty events are removed too; unrelated uses and alternative spawn points remain. Undo restores the entire deletion in one operation.

**Playtest / Debug:** the trace comes from the game and does not replace visual verification. When a playtest started by RCM ends, the editor refreshes the trace.

**Save:** retains previous changed versions. Saved versions opens a copy or restores with confirmation. If the file changed externally, reload, copy or explicitly overwrite; overwrite is not the default. Concurrent editing of the same project is blocked with an explanation.

Change language in Tools → Settings. The bottom panel starts hidden; errors, builds and references reveal it when needed. Campaign / Overview brings together scenes and story across the chronicle.

**Clickable doors and objects:** right-click the visible door/object in 3D and choose **Original object / create passage…** or **Surface / click interaction…**. Enter the hover label, such as “Club entrance”. Choose any action: travel, conversation, note, another event, flags, sequence or scenery control. Use + and − to add/remove actions. No proximity zone is created.

The clickable prop appears under **Objects**, with an ordinary **Events** record. Select the prop and **Edit click actions…** to change actions or add conditions such as owning a key. “Only once” is optional; clicks are repeatable by default. **Event / Run** calls an event in this scene; choose “From another event” to avoid automatic activation. Recursive event calls are rejected.

A travel/link destination must be another scene. To change layout on the same map, create another scene reusing that level, then an arrival entry. With only one scene, notes and other interactions remain available, but travel has no valid destination.

To adjust a door, select its **Original scenery / Object or door** action: choose object, operation, frame and speed; for pivots, duration and direction. Frames 0/1 follow the original Door script, but are not guaranteed for every model. Hide is reversible; Remove cannot recreate the object. Unchecking a tree reference only changes the preview. Fixed NIL walls cannot be removed as objects. This feature needs testing in Redemption; the accepted tutorial remains unchanged.

**Within The Darkness (optional):** Tools → Settings → **Import mod content: Within The Darkness…**. Choose your NOB from any folder. The filtered pack is copied to the workspace and the game's `RCM/_content/within_the_darkness`; close Vampire before replacing content. The source file is no longer needed afterwards. Import applies immediately, independently of saving/cancelling the other preferences.

Story / Resources then offers **Available clans**, **Available disciplines** and supported templates/models. Use an actor's **Clan and disciplines…** button for initial traits. Event actions **Actor / Change clan** and **Actor / Set discipline** can target an NPC or Player, including rewards; discipline level 0 removes its level. **Penthouse · Within The Darkness** is available as a base level with original geometry/static objects. Its demo campaign and menu reskin are excluded. Without an import, the new categories/actions remain hidden and existing behaviour is preserved.

Build records the dependency; local deployment copies the pack to that chronicle's RCM folder. Chronicle and program distribution ZIPs do not include mod content; recipients must import it themselves. Rights remain with the original authors; local import grants no additional redistribution permission. Appearance and behaviour in Redemption require the WTD checklist.

**Pick objects directly in 3D:** right-click the object. The menu identifies its material/model and template; Original object / create passage opens with that target selected. Picking uses actual mesh triangles, respects intervening walls and works with reference markers hidden. The list also offers Locate in 3D without changing the chronicle.

**Tenebrae decorative doors:** the two back doors belong to the NIL. Right-click identifies the surface and adds a selectable prop matching it; the NIL and wall remain intact. The original exit uses `tracker_thing` + `ClickExit`. The new layer uses the same native hover/click mechanism with RCM actions. A decorative door does not gain an opening animation.

Old proximity triggers/events are not silently converted. Delete the previous trigger/event with the cascade preview, recreate the click interaction, rebuild and deploy. Self-links are blocked by validation. Native hover, click, highlighting, saves and networking for this layer remain pending (CLICK01–08).
