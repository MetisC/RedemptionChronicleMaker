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

**Dynamic encounters:** Campaign → + Dynamic encounter…, assistants or the 3D ground context menu. Choose Ambush/Waves/Continuous/Reinforcements/Boss, enemies/count, points/activation and completion actions. Advanced stays collapsed. [Guide and laboratory](DYNAMIC_ENCOUNTERS.en.md). First use in format 9 makes a backup and opts into format 10; opening the tutorial does not convert it.


## Advanced scene and instance properties

Level > Scene environment offers inherited or explicit audio, volume, fog,
view distance and paired sky. EAX remains inherited from the static original.
No geometry or lightmaps are changed.

Actor/Object > Instance properties changes AI, Foley, compatible motion set and
hover text for that instance only. Containers offer inherited treasure, none or
an actual original GAME.NTT class. Native script (advanced) selects real stock
constructors and typed entity/scalar parameters. Native frame 0 is the initial
transform; additional frames select existing waypoints in order. The stock
script owns its callbacks; conflicting RCM inventory/conversation/dynamic spawn
ownership is rejected. Some scripts need original region/campaign context.

A waypoint can also belong to native interest group 0..9. Active AI must use the
same interestNum. This does not impose a patrol route.

Settings > Import template library accepts selected new templates in NOT/NOB,
resolves parents and data dependencies, and excludes menus, chronicles and code.
Imported assets remain local dependencies, outside exported ZIPs. Missing
required external code fails clearly; this is not a universal mod importer.

Cargo at the refuge is an optional example; the accepted tutorial is unchanged.
New native behaviour requires the manual EMB checklist. Custom map images,
locations and labels are technically feasible, but no map editor exists yet.


## Chronicle combat difficulty

Select the chronicle in the tree, then choose Easy, Normal, Hard or Nightmare in
Properties. Missing settings default to Normal; formats9/10 are not upgraded.
Normal preserves original behaviour and generated runtime code.

| Setting | Health and maximum | Strength | Stamina |
|---|---|---|---|
| Easy | ×0.80 | ×0.90 | ×0.90 |
| Normal | ×1 | ×1 | ×1 |
| Hard | ×1.20 | ×1.10 | ×1.10 |
| Nightmare | ×1.50 | ×1.20 | ×1.20 |

These scale native base/current attributes, not damage per hit directly. Native
clan caps and damage-specific resistances remain in control. Only newly created
RCM enemies are affected, including waves/bosses; neutral/ally teams, players and
ordinary conversation NPCs are excluded. Dynamic custom health is applied before
the global factor. Boss percentage thresholds use the resulting max health;
absolute thresholds stay absolute. Existing saved enemies retain their values.
Start a new game after changing difficulty for consistent balance.

Imported libraries can be removed through Settings > Imported libraries. Removal
checks the open chronicle and parent-library dependencies, deletes verified local
copies only, and preserves original mod files and installed game content. Other
projects may require reimporting that library. Saved inventory compatibility
retains complete verified libraries, including transitive data dependencies.
Native-script-owned actors retain their original initialisation; global difficulty
modifies fresh actors created by the RCM spawn runtime, not original world actors.
