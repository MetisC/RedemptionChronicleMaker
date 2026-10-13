# Manual runtime checks · 1.0.0-rc4

**MANUAL RUNTIME TEST REQUIRED.** RCM does not automate gameplay. Previous tutorial acceptance does not certify the new dynamic combats.

First check setup in another folder, projects outside the program, Quick tutorial/F5, LAN with an existing carried RCM item, Showcase dialogue/cameras/notes/items/journal/travel and save/load/reentry. Edit a line, save/F5 with Redemption closed and verify it in a new game when required. Independent PC/VM, real GPU and physical 100/125/150/200% DPI remain pending.

Open chronicles/dynamic_lab/project.yaml, save/F5 with the game closed. In LAN → New Game choose **RCM · Dynamic Encounter Lab** and start a new game. Record PASS/FAIL and retain the trace; all twelve cases need native observation.

| Case | Expected result |
|---|---|
| DYN01 | Anezka → arm waves → approach barrel. Entering its area creates three rats; no acceptance means no start. |
| DYN02 | Kill three; after about two seconds, two appear. One survivor prevents advancing. |
| DYN03 | Start continuous through Anezka: one per about five seconds, at most three living. Kill one; a replacement appears. |
| DYN04 | Stop: no new rats; survivors remain. Also check pause/resume. |
| DYN05 | After waves the boss rat appears. Crossing 50% creates two reinforcements once. Avoid killing it outright. |
| DYN06 | Crossing 25% plays spatial sound once; staying below does not repeat it. |
| DYN07 | Boss death completes encounter/quest and stops reinforcements/continuous. No repeated reward. |
| DYN08 | Save mid-wave with two alive; load preserves group/counts without duplication. |
| DYN09 | Save after 50%, load and wait: no repeated reinforcements. Repeat around 25%, death and reward. |
| DYN10 | In a Showcase copy activate the optional station and travel/return active and complete. Check Once/Resume; create separate Reset on return/Cooldown trials. Lost ownership must stop with an error, never duplicate. Record whether the engine restores records/captures across instances. |
| DYN11 | In a copy change count/template through the wizard, save/F5, start fresh when contract changes. Check edit/undo/reopen. |
| DYN12 | In a copy use points the engine actually rejects and few retries. Bounded retries/rotation, GENERATOR_SPAWN_FAILED/ERROR trace, responsive game. Bad coordinates do not guarantee factory failure: if no rejection is reproduced, mark PENDING rather than PASS. |

Intervals are quantized by the scene poll. This is not a collision/pathfinding certification. Ordinary enemies use original Rat; only the example boss has x10 health to expose thresholds. Showcase combat is optional; Quick tutorial is unchanged.
