# Current implementation state

Baseline 51982be, rc7. Branch codex/strict-authoring-and-difficulty (created with
existing changes carried; main not committed). No original game writes/UI runs.

Implemented: optional environment editor (audio/volumes/fog/ZClip/paired sky),
instance Foley/AI/motions/hover/treasure overrides, template controls, native NTT
catalogue, typed real native script constructors/labels/refs, orientation-first
24-byte movement frames from waypoints, native GUID adoption without Capture,
72-byte interest table and optional waypoint role / AI interestNum, local data
NOT/NOB import with dependencies outside public ZIPs, refs/rename/cascade/undo.
Original code and unknown bytes retained; default projects unchanged.

Evidence:291 env tails;64 lossless NSDs (old28 baseline independently asserted),
380 public stock Codex constructors,376 complete labels including zeroarg,
15 original interest tables,160 NTT classes. Original ClassBobbing bytecode uses
tracker frames + linked target/scalar args. Frame order is ORIENTATION then
POSITION, superseding early guess. global_72_candidates.json is a disproven
heuristic, not interest evidence; actual interest_reverse_candidates is used.

Strict matrix rewritten to8 columns and honest limits. EAX static precedence,
generic native region meshes, native sound/light boxes, stationary positive-time
camera keys and arbitrary code-bearing mods remain partial/unsafe. No100claim.
MAPS.md analyses NUI/TGA/NSC/NLS and actual location flag API; map editor absent.

Dedicated chronicles/strict_acceptance generated via prepare_acceptance.py:
optional refuge quest, cargo ClassBobbing with actual ref+3floats+2frames,
class230/inherited supply barrels, fog/instance edits, interest-group marker.
No tutorial/mini changes. Portable example whitelist updated.

Tests: focused source/UI/library suites in progress. Full final quality gate,
portable build and EN/ES moved-path verification still required. Earlier full
suite failed stale translation keys and sandbox hardlink creation; isolated
hardlink passes escalated. Run final tools/quality.py --no-coverage elevated
with reason limited temp hardlink regression. No baseline fixture changes.

Queued user request difficulty: research/combat_difficulty/REQUIREMENTS.md copied.
Read actual campaign/dynamic runtime/inspector/API. Original manual.pdf extracted
read-only with bundled pypdf, combat attributes pp31-33; API native registration
and stat setter disassembly recorded. No difficulty source implemented yet.
Must implement optional chronicle selector, Normal identical, central fresh-only
enemy scaling manual/dynamic, team/neutral/player exclusions, HP override order,
save warning/tests/real Codex compile and PR; no product version bump.

Do not delete user_workspaces or existing backups. Test-generated tracked logs
and old test scratch should not be committed. Final product build not yet fresh.
