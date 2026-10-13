# Dynamic encounters

## An ambush in 30 seconds

1. In **3D Space**, right-click visible ground and choose **Dynamic encounter here…**.
2. Choose **Ambush**. The default group is three original rats; change their template using the resource catalogue.
3. Keep the selected point. Choose **On entering an area** and the new area around that point, or choose an existing trigger area.
4. Choose completion actions to advance a quest, change a flag, play a sequence or open a valid existing exit.
5. Click **Create**, save and press **F5**. Enter the area manually in Redemption.

Campaign / Overview also has **+ Dynamic encounter…**. Select existing waypoints, place them first in 3D, or use Near the player: the engine chooses a nearby position. Collision-free placement is not guaranteed.

## Waves

The preset has three waves and two-second delays. Edit enemy types and counts, or add/remove waves. The next wave waits until the current wave is cleared; completing the last spawn alone is insufficient. Runtime enemies are not fictitious authored actors.

## Continuous generator

Set **Spawn one every** and **Maximum living enemies**. The generator replaces losses without exceeding the cap. Stop it through another event, or set a maximum total and let the remaining enemies be defeated. Normal actions start, stop, pause and resume it from conversations, areas, quests, timers and conditions.

Count is a sequential batch: spawn that many of one type, one per interval, before selecting another type. Round robin follows the pool; weighted random uses the original Math.random. Pausing stops spawning/phases; existing actors continue behaving normally. Stopping keeps living enemies by default.

## Reinforcements

The preset has no automatic start. Add **Dynamic encounter / Start** to another event. Examples: an active encounter has at most one enemy left, a 30-second timer, a conversation response or a boss phase.

## Phased boss

Choose an existing actor or generate a boss with a unique role and count 1. The original template health/AI/flags are preserved by default. Optional health overrides affect the spawned instance only.

The preset has 50% and 25% phases and a linked reinforcement group. Edit phases in percentage or HP, and select any normal action: music, sequences, flags, quests or generators. Completion can stop portals and complete a quest.

**Crossing means previous > threshold and current <= threshold while the actor remains valid and alive. A lethal hit can skip it.** There is no before-death guarantee, automatic invulnerability or phase protection. Phases are once by default across save/load/reentry; repeatable phases require a new crossing after recovery.

## Enemies and points

Resource Browser's original-enemy filter uses the original _Enemies family and actor flags, with catalogue scene references. No invented difficulty score. All actors and origin filters remain available. Confirmed model, AI, script, health/max health, clan/flags and known usage are shown. Scene hints are not a complete NSD parse; undecoded team/actor-type metadata is not fabricated.

Spawn points are editable waypoints. Selection highlights points, activation area and linked visual prop. A visual representation is a normal prop, not a new emitter or geometry. Existing callbacks/actions supply sound and sequences.

## Save, load and reentry

Native records store state, wave, pending counts, active GUID/role ownership, pause, cooldown and phases. Restored GUID/location/template must reconcile before spawning. Missing persistent ownership or unresolved restored actors cause a bounded diagnostic error rather than blind respawn. This prevents duplicates; real-engine restoration still requires manual verification.

Policies: **Once** preserves completion; **Resume** keeps progress; **Reset on reentry** retires only known owned actors and resets (not during load); **Repeat after cooldown** starts another cycle. Once-only rewards/events retain their own checkpoints. Reset does not clear unrelated event flags. Structurally different saves are not migrated; build fingerprints warn when the record contract changes.

## Advanced options and limits

Living cap 1..64; 256 dynamic actors per scene, 32 generators, 1..32 waves and bounded groups/counts/intervals/retries. These are conservative RCM limits, not certified engine benchmarks. The existing 0.15-second scene poll controls everything, sharing four spawns per tick. Tracking stores active actors only; counters saturate at one million.

Failures rotate points, trace and retry a bounded number of times. There is no timer per enemy. Health overrides affect instances, not templates; native team overrides do not automatically change AI/invulnerability flags.

This revision supports **clear-before-next-wave**, not overlapping or manually advancing one wave list. Independent generators and events can overlap groups. No arbitrary random-volume placement, new model preview, universal doors, or direct dynamic-role camera targets: phases can launch existing sequences with their ordinary targets.

## Examples

**Quick tutorial:** Una carta al amanecer stays unchanged in format 9.

**Showcase:** talk to the guide → optional dynamic encounter laboratory. Start two rats, a boss and a reinforcement, or start/stop a continuous generator capped at two. The book story is unchanged.

**Dynamic Encounter Lab:** open chronicles/dynamic_lab/project.yaml. Anezka arms the wave test: then approach the barrel to enter its trigger area. She also offers continuous spawning, pause and resume. All enemies use Rat; the example boss has a health multiplier so its phases can be observed. Save/load mid-combat.

**MANUAL RUNTIME TEST REQUIRED.** Java 45.3 compilation, doubles and widget tests do not certify these battles in Redemption. Follow DYN01–DYN12 in MANUAL_RUNTIME_CHECKLIST.md.

Generated roles are health/counter targets. Actor-specific animation, AI, inventory and camera actions still target authored actors; select an existing actor as boss for that control. External activations are edited in ordinary events; editing a generator preserves them and adds a new activation only when requested. Per-entry delay/caps/AI-state controls are unavailable. The active roster cap does not automatically remove native corpses.
