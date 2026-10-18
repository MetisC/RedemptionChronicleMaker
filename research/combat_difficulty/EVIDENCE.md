# Combat difficulty evidence and lifecycle

CONFIRMED IN ORIGINAL FILES / API

Source identities in source_identity.json. API_SIGNATURES.txt and actual
CodexActor.class expose Get/SetActorStat(int,float), Get/SetActorBaseStat,
Get/SetActorHealth, Get/SetActorMaxHealth and base/effective soak APIs.
ACTOR_STAT_STRENGTH=0, STAMINA=2. Enemy teams are 12..19; players 0..7,
pedestrians 10. The JNI registration table is recorded in api_registration.json.
GetActorStat 46be10 and base getter 46c040 read distinct arrays; setters 46be60 /
46c090 delegate to 495150 / 4955a0. The setters preserve native clan/range caps
(fallback 0..10000); RCM does not bypass them. The physical stat branch does not
run the humanity/blood side effects. Original FredVarneyCigar.beginscene and
single-player Christof setup explicitly update both base and current values.

CONFIRMED IN ORIGINAL GAME MANUAL

manual_combat_extract.txt, PDF pages 15–16 (printed pp30–33), establishes Strength
as a melee damage modifier, Stamina as natural soak (damage types depend on
species), and Dexterity as movement/attack speed, ranged aim and criticals.
Strength also affects equipment requirements. RCM does not re-equip, replace
weapons or promise linear damage multipliers; Easy equipment behaviour requires
a native check. Dexterity is deliberately unchanged to avoid speed/pathing
changes. Raw per-damage soak arrays are deliberately unchanged: changing them
could erase species vulnerabilities/immunities or double-count Stamina/armour.
Mental/social attributes, disciplines, rank, XP and loot remain unchanged.

IMPLEMENTED POLICY

Optional chronicle.difficulty: easy/normal/hard/nightmare. Missing = normal.
Formats9/10 remain their original version. Normal emits no helper/call, preserving
pre-feature Java SHA baselines and exact generated NOB bytes.

                 Health/max   Strength(base/current)  Stamina(base/current)
Easy                0.80               0.90                    0.90
Normal              1.00               1.00                    1.00
Hard                1.20               1.10                    1.10
Nightmare           1.50               1.20                    1.20

Same factors retain relative values until the engine's native stat caps apply.
Health and max are scaled together, retaining an initially wounded actor's ratio;
0/negative/dead and nonfinite health are not revived. Zero stats remain zero;
invalid/nonfinite stats are left alone. No raw damage/DPS multiplier is promised.

One shared difficultyEnemy helper is called only in fresh manual spawn after
team/traits and only for behavior:enemy; dynamicSpawn calls it after individual
health/health_multiplier override and final team override, before boss baseline
capture. Thus custom health50 -> Nightmare75; multiplier2 -> baseline200 ->300.
Only actual nonplayer, local, living enemy-team actors without NEUTRAL are
eligible. Neutral/ally/conversation-only default NPCs stay unchanged. Original
native-script-owned entities are adopted, not reinitialised as RCM spawns.

Existing GUIDs, createdOnce actors, restore/re-entry and dynamic slot recovery
never call the helper. There is no new save record/version/flag/array and no
periodic stat reapplication. Native actor saving preserves the modified stats.
Changing difficulty mid-save affects only future enemies; inspector warning and
changed-build warning recommend a new game for uniform balance. Changing it
alone does not change save_schema_sha256. Percentage boss thresholds use scaled
max health; explicit absolute HP thresholds stay absolute. Death/reward/phase
code is unchanged. Host-only execution respects the existing NetIsClient guard.

TEST SCOPE

See tests/test_combat_difficulty.py: format/default/invalid/roundtrip, Normal
pre-feature source SHA + byte-identical package, UI selection/undo, fresh manual
presets, original GUID, neutral/ally/player/dead/client guards, dynamic override
order and boss percentage/absolute phases, save/re-entry no double scale/reward,
actual Codex JVM45.3 builds. Doubles do not prove native balance or persistence.
Native cases DIFF01–06 remain the user's checks. No game process is launched.
