# Authoring completion — controls and acceptance

These optional controls work in formats 9/10; dynamic roles require format 10
encounters. They do not convert the accepted tutorial or mini chronicle.
Open **Help → Authoring laboratory** for the separate example. Choose a fresh
copy if you already have an older personal copy, then start a new game via F5.

- **Maps:** Chronicle properties → Maps and locations, or Campaign → Add… →
  Maps and locations. New map imports your image, fitted to640×480. Add and drag
  locations, edit names/Visible/Haven and bind scenes below the image. Cancel
  copies nothing; OK is one undoable project change. Location flags Actions and
  the Location visible condition control discovery. This is the original kind
  of informational map, with hover names and no click travel.
- **Stationary turn/hold:** Sequence → Create/edit own camera path → Time per
  segment. Duplicate a point and change its orientation to turn in place. Keep
  both position and orientation to wait. Set seconds to the next point; native
  speed stays1, total at most 120seconds. Distance mode still requires distinct
  consecutive positions. Original NCP files remain untouched; no per-key FOV.
- **Native regions:** create a box trigger, then choose Native region for scripts
  or Native region script. Select a real constructor and typed local links. A
  controller can link to a region without its own script. Stock scripts retain
  callbacks/save ownership; conflicting RCM trigger events are rejected. The
  supported subset is yaw-only boxes, at most8, linked to actual level sectors.
- **Sound/light zones:** Trigger → Sound zone / Dynamic light zone. Choose WAV,
  volume/radii, or an owned entity/color/intensity/radius/style. Occupancy activates
  one positioned loop or point light. This is an activation alternative, not
  literal sector clipping, baked lighting or the full original box payload.
- **Reverb:** Level → Scene environment → EAX reverb, inherit or original preset
  0..25. Environment Actions can change it later. The proven original roomtype
  command runs after scene activation; an audible result requires a compatible
  installed 3D audio provider. The original static NSD stays untouched.
- **Generated actors:** normal subject/reference/actor/entity selectors offer
  generator / role #n. It resolves the nth currently living owned role in the
  existing GUID roster, not a persistent identity or another manager. Cameras,
  animation/look/movement/routes, attached sound/light, inventory and team/AI
  pause controls use this selector. Missing targets fail safely; a film releases
  control when its pinned dynamic GUID changes. Aliases are not saved or spawned.
- **Clans/disciplines:** Actor → Clan and disciplines also works with original
  game resources without a mod. WTD extends only locally imported content. New
  actor initialization does not reset restored actor state.

The original-source evidence, source files and complete implementation matrix
are in research/authoring_completion/EVIDENCE.md and EMBRACE_AUTHORING_PARITY.md.
This is not a100% or final1.0 claim. Unknown campaign-specific CodexPlayer
constructor binding and literal sound/light box clipping remain separate from
the implemented alternatives. Unknown executable mod dependencies are rejected.
Geometry/CSG/sectors/UV/lightmap authoring remains outside the agreed scope.

## Six short native checks, in order

Speak to Anezka in the new laboratory. Each exercise is independent.

| Case | Observe in Redemption |
|---|---|
| COMP01 | Turn and hold: framing, shortest rotation, completion/cancel restore GUI/cursor. Save/load cancels films with cues or NPC subjects. Player films without cues retain the previous replay-from-start policy without duplicate rewards. |
| COMP02 | Enter the native box beside the guard: bell/callback, no solid visible region; save/load/reenter without duplicate entities. |
| COMP03 | Enter/leave sound/light zone: one loop, radii/color, stop outside. Change reverb with3D provider. Save/load while active. |
| COMP04 | Open normal map: image, names, points/haven; reveal second layout, travel through dialogue and return; save/load discovery. |
| COMP05 | Spawn weak rat, follow it, cancel/finish/kill; neutral guest movement/pause and Dagger inventory give/take. Save/load/reenter without duplicates or GUID replacement. |
| COMP06 | In a copy, set an original clan/discipline without WTD; compare newly created/restored actor. Tutorial and mini still load. |

These observations remain pending until the user performs them. Real Codex 45.3
compilation, binary readback, doubles and Qt offscreen are distinct evidence;
they do not certify gameplay, physical GPU/DPI, a separate PC or networking.


Converting a shared camera path to time per segment updates its sequence and action playback rates to1 in the same undo transaction.
