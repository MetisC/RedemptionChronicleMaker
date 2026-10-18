# Final surgical audit — current HEAD

Baseline inspected: 1d505c5 (rc6), plus the CASH loader repair. The user
confirmed that Taller del Narrador now opens: “Funciona bien y abre.”
That acceptance covers initial loading only. No new product version,
project format, main tab, geometry work or automated gameplay is authorized.
Full requirements: FINAL_FLECKS_REQUIREMENTS.md.

## Music: decision before implementation

CONFIRMED IN API / ORIGINAL BYTECODE: PushMusic(String,int) and PopMusic()
are Java wrappers in CodexSound, not native stack operations. Push saves
GetMusicName/GetMusicVolume into one static pair (aMusicName/musicVolume),
then StopMusic/StartMusic. Pop stops and restarts that pair. A second Push
overwrites the only snapshot. Pop does not clear it. Fresh archive scan:
55 original script classes reference Push, 53 reference Pop. SDK lists
signatures but does not promise nesting or persistence. See fresh
CodexSound_flecks_bytecode.txt and final_flecks_references.json.

Decision: ordinary temporary-music/restore Actions, volume 0..100, same
compiler/UI as all Actions. One bounded owner; reject nested Push and
unowned Pop. No parallel stack. Do not claim native snapshot save/load
without evidence. Cleanup may Pop only a still-owned, unchanged Codex
snapshot. Trace foreign replacement and fail closed. Native audio,
transition and save/load cases remain manual.

## Conversation starts: decision before implementation

CONFIRMED IN SDK: Embrace exposes separate playerstarts and convstarts,
each named indices 0..15. CONFIRMED IN API: two distinct teleport methods.
Fresh archive scan: 107 original script classes reference conversation
teleport, one references entrance teleport.

CONFIRMED IN EXECUTABLE: JNI table identifies entrance at 0x470ae0 and
conversation at 0x470b20. They select separate tables in the shared party
relocation routine (0x462c90 / lookup 0x4b33b0), with an additional MP
player branch in the conversation wrapper. They are not internally
identical. NSD entrance records are 60 bytes, conversation records also
60 bytes, after a separate 72-byte-record table. Conversation count is
the fourth generated global count, at empty-global offset +12. The
loader stores its count/table at location+0xb4/+0xb8. Sector indices are
resolved to native sector pointers, then the stored matrix is copied.

CONFIRMED IN ORIGINAL FILES: bounded tail-table extraction validated
99 nonempty NSD conversation tables / 473 records. Each record is
sector u32, 12 matrix floats, group u32, party-selector u32. Original
formations repeat a group with several records and selector zero;
lookup chooses matching successive fallback records for party members.
Evidence: native_conversation_starts.txt and original_conversation_tables.json.

Decision: preserve string Entry staging byte-for-byte. Add optional native
conversation staging using a small ordered selection of existing named
Entry markers (one to four), no new marker editor. Generate only the
proven table inside RCM NSD, group indices bounded 0..15. Use the actual
TeleportPartyToConversation. Named points, transforms, references,
deletion and undo remain in existing infrastructure. Ground/yaw-only
matrix authoring is bounded explicitly; no universal NSD writer claim.
Formation/orientation/collision and MP differences require native tests.

## Stationary NCPs: decision before implementation

CONFIRMED IN ORIGINAL FILES: all 174 original paths scanned. There are
22 adjacent pairs with equal XYZ in three files: eight with differing
Euler, fourteen with equal Euler. Every pair has equal parameter too.
Examples oldtownday and prague_3_3_bed have nontrivial cubic spatial
coefficients; repeated XYZ is not proof of a timed stationary hold.
Several bed records contain very large coefficients and repeated keys.
Full classified pairs: stationary_ncp_pairs.json.

The evaluator advances its path parameter by speed; there is no proven
duration inferred from an equal-position/equal-parameter pair. A new
positive span would invent timing. Decision: retain the authored-point
restriction, preserve lossless playback of originals, and document
PARTIAL stationary NCP authoring. A fixed shot already supports a hold.
No arbitrary minimum span or fake stationary-rotation button.

## Implementation and verification

Implemented within the existing Actions, conversation inspector, Entry references and generated NSD writer. No version/format increase, new main tab or parallel stack/marker editor. Tutorial, mini, dynamic lab and user workspaces remain unchanged. Optional Showcase lab and the independent refuge example exercise the new features.

Full gate: 525 tests, 0 failures, 0 errors, 0 skipped; Ruff and configured mypy pass, with 112 sector catalogues verified. After the last inspector-width fix, 140 widget regressions pass with 0/0/0. Real Codex compilation produces 45.3 classfiles; source export/import, package inspection, references, rename, cascade and undo are included. Bilingual frozen-app checks are separate from native gameplay. Current receipt: final_flecks_delivery.json.

Push/Pop and native party staging: IMPLEMENTED, OFFLINE VERIFIED, COMPILED AGAINST REAL CODEX, PACKAGED; native sound/formation/collision/load/MP remain MANUAL RUNTIME TEST REQUIRED. Stationary NCP authoring: PARTIAL, deliberately constrained until a positive-span timing rule is demonstrated; fixed holds and lossless original paths remain available.

Only corrected initial Showcase loading has new user acceptance. Independent PC, actual GPU/DPI and all new manual cases remain unverified. No universal Embrace parity or final-1.0 claim. No further feature phase is started.
