# Changes · 1.0.0-rc11

- Author native parametric scenery as NSD brush entities (decor, solid, interactive layers) over the immutable original geometry; fix decor dialog accept behaviour and round out the scenery editing UX. The scenery lab gains an optional wave-based Rat dynamic-encounter example.
- Improve reference navigation and hostility authoring across actors, dialogues and contextual responses; add the missing English UI strings for the new scenery tooling.
- Publish the project under the MIT License and purge proprietary snapshot data from repository history; ship `LICENSE` in the portable root.
- Replace GitHub Actions releases with a maintainer-local pipeline: local quality gate, portable build, packaged-source verification, product audit, staged artifacts, explicit draft-then-publish via authenticated GitHub CLI, post-publication byte verification and immutable published releases. Workflows keep manual-dispatch definitions only; no push or tag consumes hosted minutes.

The accepted tutorial, mini chronicle, immutable original geometry and legacy generation contracts are preserved. No original authoring tools or original game/mod assets are distributed. Native SCENERY/DLGFX/QOL and the existing manual checklist remain pending user acceptance; this is not final 1.0.

# Changes · 1.0.0-rc10

- Publish the project under the MIT License and ship `LICENSE` inside the portable root. Remove the frozen legacy application snapshot — including extracted original game data — from repository history; it stays on disk only.
- Merge the optional native parametric scenery layer (decor/solid/interactive brush entities) with its scenery lab example; native acceptance SCENERY01–10 stays on the manual checklist.
- Apply authored text and typed numbers after editing, only when modified. Avoid per-keystroke validation, snapshots, scene refreshes and resource filtering; Save/Build first commit pending fields. Preserve invalid drafts and multiline paragraphs.
- Open the conversation editor immediately after contextual creation. Keep the current conversation view when deleting a node, line or response.
- Give RETURN responses ordinary actions, including a one-click hostile speaker preset, after native dialogue cleanup. Add genuine boolean flag-change reactions, saved observation state and clear flag-index explanations.
- Edit linked actions from actors, objects, areas, conversations, scenes, quests, completed groups, timeline/travelling sequences and optional format-10 dynamic encounters. Reuse ordinary events with their filters, extra conditions and repetition; navigate directly to them.
- Reuse conditional routes instead of making duplicates. Preserve cancellation, no-op, pending ID changes and one-step undo. Prevent removing a called event's last actions without the normal reference review.
- Unify object/actor conversation creation with the speaking-character chooser. Modern area links no longer choose arbitrary Chronicle Flags.
- Keep English and Spanish UI/guide coverage. Verify packaged Python sources and translations in the release workflow.

The accepted tutorial, mini chronicle, immutable original geometry and legacy generation contracts are preserved. No original authoring tools or original game/mod assets are distributed. Native DLGFX/QOL and the existing manual checklist remain pending user acceptance; this is not final 1.0.
