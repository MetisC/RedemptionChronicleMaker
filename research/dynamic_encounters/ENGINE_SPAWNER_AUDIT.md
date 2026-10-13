# Original engine spawner audit · RC4

## CONFIRMADO EN ORIGINAL

Generator.class exists in Codex.nob (compiled from Generator.java). Generator.bytecode.txt is the complete disassembly. It takes templateName, delay, frequency, maxThings and maxAlive. beginscene obtains its own thing, optionally its frame-1 position and sets a timer; timer uses generatorThing.SpawnThing, optional SendActorToPos(150), increments counters, CaptureThing when maxAlive is enabled, KillTimer before rescheduling. killed decrements alive and can reschedule. maxThings=0 means unbounded, maxAlive=0 bypasses alive capture. Frequency below 0.1 prevents beginscene scheduling. Save/restore records are string, two floats and four ints in identical order; no complete GUID roster. No explicit zero-GUID guard is present (wrapping new CodexThing is not validation). This design is informative, not suitable as an unchanged general authoring director.

Original references appear in Resource.nob scenes SEW4_35_1, SEW4_LOT_12_1, SIM1_5_1 and SIM2_5_1. No NOT script-tag binding to Generator was found in the extracted libraries; these are scene script bindings with variable parameters. Archive reference offsets/hashes and bounded entity hints are recorded separately; hints are not a full NSD reader. MysticSpawner is used in ARC1_17_1 and calls Math.random(), spawns effects/items and saves booleans and a GUID as int.

The audit enumerates 465 original class/interface blocks and 223 call sites of SpawnThing, SpawnThingNear, CreateThing or PreloadTemplate. spawn_calls.json retains class, method, instructions, context, string constants and related methods. All six installation NOB archives and all relevant NSD/NSS/NOT/NSC/NMF/class/text/source entries were scanned for Generator/MysticSpawner references. Not all control flow/string constants can be resolved to a single template statically.

DisciplineSummonSoul/Elemental use SpawnThingNear(template,0,0), test GUID 0, set SUMMONED and copy caster team with SetActorTeam. SUMMONED is a timed discipline lifecycle, not a generic save/ownership switch: RCM will not set it for encounter enemies. EMITTER=32 and PROXIMITYTRIGGER=1024 are native thing flags; no evidence makes them a combat generator. No automatic emitter or invulnerability is introduced.

Native Get/SetActorHealth/MaxHealth, IsActorGuid, GetTemplateName, SetPosition/Orientation, CaptureThing, ReleaseThing and Remove signatures exist. Original killed(int,int,int) callbacks are widespread, including Generator. hit(int,int,float,int) exists in projectile scripts; it does not prove a universal actor pre-damage hook. Original Math.random() has 240 call sites; java.util.Random is unnecessary.

NOT ordered property labels in Vampire.exe at recorded offsets, original tag/payload values, inheritance and Codex constants underpin the catalogue. Tags 52/60 are integer template health/max health (Rat=20, base actor=100), 26 clan and 114 actor flags; runtime health uses floats. Hostile taxonomy is the explicit _Enemies parent hierarchy and original scene usage, not guessing from actor names. TEAM ranges are native constants; template team/actor-type decoding beyond existing confirmed fields is not claimed.

## CONFIRMADO EN SDK

Existing SDK archive index, scene/Embrace documentation and original cutscene example corroborate the script/scene binding, native timer/save/capture pattern and immutable geometry layer. Some CodexThing/World/Actor page bodies were unavailable locally (receipts alone are not method documentation). API signatures are attributed to original class bytecode, not falsely to missing SDK text.

## CONFIRMADO POR RCM

Accepted format-9 runtime uses a KillTimer/SetTimer single scene loop (0.15s), SaveInt GUIDs, SaveBoolean/Float in paired order, local GUID validation, SAVEALWAYS and native factories. Native tutorial showed CreateThing may return 0: existing fallback PreloadTemplate + SpawnThingNear(player,0,0) then explicit transform is accepted for authored actors. Existing format-9 tutorial and encounter implementation will remain unchanged.

## INFERIDO / DECISIONES

Reuse native factories, capture/death callbacks plus bounded health sampling in the existing scene loop. Use native records for counters/slots/thresholds; only persistent story latches need Chronicle Flags. Maintain a bounded active GUID roster, never all historic enemies. Factory retry must be bounded and rotate authored points. Lost/unmatched restored GUIDs must stall instead of blindly respawning; this favours no duplicates over hiding a native restore failure. Exact actor placement does not guarantee a navigable or collision-free point. Health crossing means previous > threshold and current <= threshold while alive; a lethal jump may skip it. Random selection uses original Math.random; no RNG sequence continuity guarantee.

## NO ENCONTRADO

No universal actor damage-before-death callback or safe automatic pre-death protection was demonstrated. No safe arbitrary random placement volume or universal geometry/door operation was established. No complete engine-native generator source file was located; original class/bytecode and scene bindings ARE found.

## REQUIERE PRUEBA NATIVA

GUID reconciliation and native record timing on save/load/reentry; location suspension; corpse rot and removal; near-player collision; high concurrency limits, UI/cinematic interruptions and all health/boss demonstrations. Server-only guard is retained; network behaviour is not certified. Offline doubles and real Java 45.3 compilation do not certify gameplay.

The external 'original generator script' reference was located in the mod author's Steam discussion: https://steamcommunity.com/app/559680/discussions/0/1471966894871297402/?ctp=12&l=polish . It served only as a search lead. All implementation decisions above derive from local original evidence.
