# Changes · 1.0.0-rc10

- Apply authored text and typed numbers after editing, only when modified. Avoid per-keystroke validation, snapshots, scene refreshes and resource filtering; Save/Build first commit pending fields. Preserve invalid drafts and multiline paragraphs.
- Open the conversation editor immediately after contextual creation. Keep the current conversation view when deleting a node, line or response.
- Give RETURN responses ordinary actions, including a one-click hostile speaker preset, after native dialogue cleanup. Add genuine boolean flag-change reactions, saved observation state and clear flag-index explanations.
- Edit linked actions from actors, objects, areas, conversations, scenes, quests, completed groups, timeline/travelling sequences and optional format-10 dynamic encounters. Reuse ordinary events with their filters, extra conditions and repetition; navigate directly to them.
- Reuse conditional routes instead of making duplicates. Preserve cancellation, no-op, pending ID changes and one-step undo. Prevent removing a called event's last actions without the normal reference review.
- Unify object/actor conversation creation with the speaking-character chooser. Modern area links no longer choose arbitrary Chronicle Flags.
- Keep English and Spanish UI/guide coverage. Verify packaged Python sources and translations in the release workflow.

The accepted tutorial, mini chronicle, immutable original geometry and legacy generation contracts are preserved. No original authoring tools or original game/mod assets are distributed. Native DLGFX/QOL and the existing manual checklist remain pending user acceptance; this is not final 1.0.
