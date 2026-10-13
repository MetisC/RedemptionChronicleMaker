# Author your adventure

Start with a level, player arrival and one NPC. **Campaign → Assistant…** offers ten tasks: talking NPC; NPC sends you somewhere; trigger actions; cinematic trigger; pickup; quest; encounter; travel with arrival; note/letter; object conversation.

Assistants create ordinary entities. **Chronicle → Edit assistant** reopens saved configurations by reading their current text, positions and shots, including Properties edits. There is no parallel data copy. Cancel does nothing; Apply is undoable. Missing references show **Incomplete configuration**: explicitly repair, choose another resource or unlink while keeping the adventure.

The first answer of **NPC sends you somewhere** must end with RETURN 1 to arm the trigger. Answer/enter/end events and flags are ordinary project elements. The second answer leaves it disarmed. Edit complex branches in Story or the graph; the assistant edits the first line and two entry answers without removing other nodes.

**Trigger actions** supports multiple common actions, conditions and once. Use Events / Properties for composite logic and advanced actions. Complex conditions are preserved unless you change the simple condition selector. Conditions are checked on entry, not continuously while inside.

**Camera:** conversations default to shoulder framing. The sequence form asks Shot / Shot sequence / Original travelling. Player is a valid subject for shot sequences. An NPC reference aligns the line of action; avoid references too close or far away. Presets use real constants. Edit time, transitions and angles normally. Changing type warns and is undoable. NCP playback reuses original resources; no writer exists.

**Quest:** title, description, steps and XP. Start / Advance / Complete quest events control the journal; completion requires every step. **Encounter:** the assistant starts with a basic Rat and a group. Edit members and its spawn event normally. Reward arrives when all are dead. Change the spawn event to Item in inventory or a flag condition to delay it.

**Travel:** create the destination scene first. The assistant places an arrival there and a travel trigger here. Changing destination keeps the previous arrival and creates another without hidden deletion. Arrival moves the player only on entry; loading restores the saved pose.

**Notes:** use an interactive object. Show note generates NTX and calls the native text panel. Object conversations require a real speaker in the scene. Continue after a note with When a note closes; do not combine two modal actions in one event.

**Once and saves:** checkpoints prevent logical repetitions and duplicated rewards in doubles. A native effect and its checkpoint are not atomic. Test saves around effects in Redemption. Avoid ID/structural changes during an active playthrough; check Build's new-game warning.

**Playtest in Redemption (F5):** saves and validates, builds only when changed, prepares your chronicle folder and opens the game. Close Redemption before updating. Separate build and diagnostic tools remain available.

Open chronicles/mini_chronicle/project.yaml for a complete example adventure, editable using the same panels and assistants.
