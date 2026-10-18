# Final strict authoring audit — rc7

Baseline 51982be45c9931495c4655d02239178b053e189a. Current work is isolated on
codex/strict-authoring-and-difficulty. No original authoring tool or game UI was
run. This report corrects the earlier generous parity conclusion; it does not
announce 100% parity or final 1.0. The accepted tutorial remains format 9.

1. **Every material Thing override? Partly.** Foley, motions, AI, hover text,
   native treasure, inheritance and script removal have normal controls.
   Parameterised script assignment has typed controls; region-dependent script
   context is not universally authorable. Generic unknown tags stay readonly.
2. **Every scene environment property? No.** Music/ambient, volumes, fog
   mode/RGB/distances, ZClip and paired sky are editable. EAX remains inherited
   because native activation prioritises the original static scene.
3. **Reuse a parameterised original script without custom Java? Yes, bounded.**
   Public real constructors, scalar/entity parameters and native movement frames
   are available through the inspector. ClassBobbing cargo is the acceptance
   example. Context-dependent scripts are not guaranteed on arbitrary objects.
4. **Native treasure? Implemented, native observation pending.** Container-only
   tag 92 with actual GAME.NTT catalogue, inherit/none and real class choices.
   No replacement loot implementation. Random rolls require repeated testing.
5. **Interest spots distinct? Yes.** Native 72-byte group table, selected by AI
   interestNum, now authored as an optional waypoint role; not ordinary patrols.
6. **Soundboxes distinct? Yes.** A trigger plus a sound is not strict proof of
   box/sector semantics. The exact writer remains unsafe/insufficient evidence.
7. **Lightboxes relevant outside baking? Not conclusively resolved.** Dynamic
   light Actions work through real APIs, but native box ownership is unproven.
   This remains an explicit gap rather than a geometry-only dismissal.
8. **External NOT libraries without Embrace? Yes for selected data.** Normal
   Settings import selects templates, resolves parents/data and retains local
   ownership. Unsupported required code fails clearly. No universal mod claim.
9. **Useful authoring still requiring YAML?** Newly implemented intentions have
   controls and undo. Missing native box/region capabilities cannot be made safe
   simply by typing YAML. Manual format edits are not advertised as parity.
10. **Useful authoring still requiring custom Java? Yes.** Specialised native
    callback semantics and entirely new gameplay remain advanced scripts.
    The new typed stock constructor route itself does not require custom Java.
11. **Must authors launch Embrace?** Not for implemented workflows. We cannot
    honestly prove the stronger statement that every material native workflow
    has a safe RCM equivalent. Unsupported native boxes/context remain gaps.
12. **All unresolved items geometry/build only? No.** EAX, stationary NCP timing,
    native boxes and regional callback contexts are material uncertainties.

Evidence: inventory and matrix (8 explicit columns), treasure_class.md,
codex_linker_format.md, SAFETY_DECISIONS.md, environment/interest corpus JSON and
original disassembly beside them. New code is optional; unconfigured projects
retain existing generation. Strict acceptance is a separate short quest, not a
rewrite of tutorial/mini. No third-party assets are redistributed.

Automated results: see build/tests/quality_report.json and test_report.json for
the most recent complete gate, with native_engine_test=false. Focused tests cover
291 environments, 64 NSD lossless round-trips, constructor metadata, typed bounds,
real Codex 45.3 compilation, interface transactions and local library ownership.
Only the user's in-game observations can close new EMB manual cases.

Maps: eight original NUI map layouts and NSC/NLS point mapping are understood.
Own illustration/locations/labels and native visibility flags are feasible
without NIL edits. A normal map editor is not implemented. MAPS.md separates
that conclusion from existing authored scene/map inheritance.
