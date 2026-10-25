# Using the editor

**Link actions without assembling events by hand:** select an actor, object, area, conversation or level. Choose when to react in the linked-actions selector, then **Actions…**. The context menu also offers **Linked actions**. Set actions, additional conditions (AND/ALL/ANY/NOT) and **Once only** in the same window. Cancel keeps everything. **View event** opens the ordinary event with its filters and references; when several routes exist, choose which one to edit. Conditional routes are kept and reopening a shortcut does not create another event.

In Campaign / Overview, select an encounter to react to its defeat, a shot sequence or travelling to react on completion, or a quest to react to its state/step. For example, completing a film can spawn an encounter and advance a quest; an enemy death can give an item and experience; leaving an area can restore music. Inventory, deaths and quest states use existing engine/generator checks, including scene entry. Format-10 dynamic encounters offer start, wave, completion and stop reactions. Native-script regions keep their own callbacks. Note closure is scene-wide: it means **any** note, not one specific letter.

Quest steps are numbered from 1 in the selector; internal indices are preserved. Quest links belong to the active scene; add them to other scenes if needed there. A particular response has **Actions when choosing this response…**. The conversation-level link reacts to its final result and can retain an existing RETURN filter.

**Make a dialogue response turn an NPC hostile:** select the response, choose **Destination → End (RETURN)** and click **Make the speaker hostile**. **Actions when choosing this response…** lets you edit this effect or add other actions. Effects run after that response ends the dialogue, after its flag change and native conversation cleanup. Cancelling the dialogue runs no response actions. For a GOTO branch, use actions on the destination node's first line.

**React to flag changes:** select the flag alias under Chronicle Flags, then **Actions when enabled…** or **Actions when disabled…**. Add **Actor / Hostile or neutral behaviour**, select the NPC and choose **Behaviour → Enemy · Original AI**. The other state can make it neutral. These are ordinary **WHEN → A flag changes** events in the active scene, editable in Events. **Every time** means once per genuine transition, not continuously while enabled. Initial state does not trigger the event; **A condition becomes true** also checks initial state. **Index** identifies flag storage, not its in-game value. Requires project format 9/10.

**Uninterrupted typing:** authored text is applied when you leave the field; single-line fields also accept Enter. Enter in multiline fields keeps adding paragraphs. Saving, validating, building or changing selection first applies pending edits. Typing does not rebuild the scene or record every keystroke as a project change. Returning to the original value applies nothing. Typed numbers also wait until editing finishes; their arrow buttons still work immediately.

Searches apply on Enter or when leaving the field, so lists and model previews are not rebuilt while typing. The × resets results directly.

To delete a chronicle, select it in **Recent projects** and choose **Delete chronicle…**, press Delete or use the context menu. Confirmation shows the exact path: deletion permanently removes the local project and its resource folder. For a standalone YAML, only that file and its autosave are removed. Installed chronicles and saved games are kept. **Remove from recent** only hides the entry and keeps all files. Projects open in another editor and bundled original examples cannot be deleted.

**Welcome:** create, open or return to a recent project. Tutorial and Showcase are working copies: creating a clean copy preserves earlier work.

**3D Space:** place entries, NPCs, objects and trigger areas on the ground. Start focuses the player entry. F focuses selection. Original geometry cannot be modified.

**Story / Resources:** select an actor, conversation, node or answer and edit Properties. Tooltips show complete text. Filter resources by type, family and origin; save favourites.

**Campaign / Overview:** create scenes, travel, paths, quests, encounters and cinematic sequences. Assistants create ordinary editable, undoable relationships. Reopening an assistant reads current entity values.

**Find things quickly:** Ctrl+F filters the project tree by name or ID in the active scene. Ctrl+Shift+F searches the whole chronicle, including other scenes and dialogue text. Press Enter to open the selected result (or the first result). Clear a search with its × button. Opening another project clears these searches; filtering never hides content in the game. Collapsed project groups stay collapsed when you refresh.

**Choose resources:** search and press Enter to move to the results, then Enter again to choose. The confirmation button is available only for a valid selection. If nothing matches, **Reset filters** clears search, family, origin and favourites filters while retaining the resource type and any inventory restrictions. Selection stays on the same resource when it still matches after a refresh.

An invalid property stays visible when you try to select something else. Correct it before continuing; navigating does not discard the pending value. Recent projects on the welcome screen also open with Enter.

**Graph:** shows conversation branches or an event's action order. Select a card to edit it. Fit view frames the graph.

**Delete:** select an element and press Delete or the Delete button. Its basic spawn actions are removed together. For cross-references, the dialog shows where it is used and what would be removed: go directly to a use, cancel, or choose “Delete and remove references”. Empty events are removed too; unrelated uses and alternative spawn points remain. Undo restores the entire deletion in one operation.

**Playtest / Debug:** the trace comes from the game and does not replace visual verification. When a playtest started by RCM ends, the editor refreshes the trace.

**Save:** retains previous changed versions. Saved versions opens a copy or restores with confirmation. If the file changed externally, reload, copy or explicitly overwrite; overwrite is not the default. Concurrent editing of the same project is blocked with an explanation.

Change language in Tools → Settings. The bottom panel starts hidden; errors, builds and references reveal it when needed. Campaign / Overview brings together scenes and story across the chronicle.

**Clickable doors and objects:** right-click the visible door/object in 3D and choose **Original object / create passage…** or **Surface / click interaction…**. Enter the hover label, such as “Club entrance”. Choose any action: travel, conversation, note, another event, flags, sequence or scenery control. Use + and − to add/remove actions. No proximity zone is created.

The clickable prop appears under **Objects**, with an ordinary **Events** record. Select the prop and **Edit click actions…** to change actions or add conditions such as owning a key. “Only once” is optional; clicks are repeatable by default. **Event / Run** calls an event in this scene; choose “From another event” to avoid automatic activation. Recursive event calls are rejected.

A travel/link destination must be another scene. To change layout on the same map, create another scene reusing that level, then an arrival entry. With only one scene, notes and other interactions remain available, but travel has no valid destination.

To adjust a door, select its **Original scenery / Object or door** action: choose object, operation, frame and speed; for pivots, duration and direction. Frames 0/1 follow the original Door script, but are not guaranteed for every model. Hide is reversible; Remove cannot recreate the object. Unchecking a tree reference only changes the preview. Fixed NIL walls cannot be removed as objects. This feature needs testing in Redemption; the accepted tutorial remains unchanged.

**Within The Darkness (optional):** Tools → Settings → **Import mod content: Within The Darkness…**. Choose your NOB from any folder. The filtered pack is copied to the workspace and directly to the game's `RCM/rcm_wtd_content.nob`; close Vampire before replacing content. The source file is no longer needed afterwards. Import applies immediately, independently of saving/cancelling the other preferences.

Story / Resources then offers **Available clans**, **Available disciplines** and supported templates/models. Use an actor's **Clan and disciplines…** button for initial traits. Event actions **Actor / Change clan** and **Actor / Set discipline** can target an NPC or Player, including rewards; discipline level 0 removes its level. **Penthouse · Within The Darkness** is available as a base level with original geometry/static objects. Its demo campaign and menu reskin are excluded. Without an import, the new categories/actions remain hidden and existing behaviour is preserved.

Once installed in RCM, the pack applies to all managed RCM launch folders, regardless of the selected chronicle or whether the current workspace has an authoring import. Launching the game without RCM keeps the base game unchanged. Because the engine does not inherit parent user folders, deployment maintains verified runtime mirrors in isolated RCM launch folders automatically. Build still records explicit content dependencies. Chronicle and program distribution ZIPs do not include mod content; recipients must import it themselves. Rights remain with the original authors; local import grants no additional redistribution permission. Appearance and behaviour in Redemption require the WTD checklist.

**Pick objects directly in 3D:** right-click the object. The menu identifies its material/model and template; Original object / create passage opens with that target selected. Picking uses actual mesh triangles, respects intervening walls and works with reference markers hidden. The list also offers Locate in 3D without changing the chronicle.

**Tenebrae decorative doors:** the two back doors belong to the NIL. Right-click identifies the surface and adds a selectable prop matching it; the NIL and wall remain intact. The original exit uses `tracker_thing` + `ClickExit`. The new layer uses the same native hover/click mechanism with RCM actions. A decorative door does not gain an opening animation.

Old proximity triggers/events are not silently converted. Delete the previous trigger/event with the cascade preview, recreate the click interaction, rebuild and deploy. Self-links are blocked by validation. Native hover, click, highlighting, saves and networking for this layer remain pending (CLICK01–08).

**Native scenery:** right-click the ground → **+ Decoration…** adds parametric pieces (crates, walls, columns, platforms, invisible barriers, interactive panels) that the compiler turns into NSD brush entities; the original NIL geometry is untouched. Choose the mode (decorative, solid, invisible barrier, interactive), size in world units, level material and texture scale; then move, rotate and scale them like any object. Interactive pieces accept **click actions** from their inspector. **Save as prefab…** stores a composition of objects as a reusable prefab and **+ Prefab…** spawns editable copies; both live in `authoring.prefabs` in the YAML (formats 9/10). **Duplicate** clones the selection with an offset copy. Rendering is verified in the editor; native collision and behaviour remain EXPERIMENTAL until the SCENERY01–10 checklist checks.

Campaign → Sequences → Create/edit camera path captures the current 3D view. Add/reorder points and apply once; the window stays open while navigating. Timed Actions use the ordinary inspector. Dialogue line Properties offers Actions at line start. See CINEMATIC_DIRECTOR.en.md and the Help acceptance example.

**Resuming AI does not change hostility:** “AI / Resume (keep allegiance)” only removes the pause. A neutral NPC stays neutral. To turn it into an enemy, choose “Actor / Hostile or neutral behaviour” and “Enemy · Original AI”, or “Make the speaker hostile” on a response. An existing resume action offers “Convert this action to make hostile” and keeps its selected actor. New behaviour actions show the enemy preset immediately; existing advanced actions are preserved.
