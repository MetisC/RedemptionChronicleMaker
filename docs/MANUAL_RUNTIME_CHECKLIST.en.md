# Manual runtime checks Â· 1.0.0-rc4

**MANUAL RUNTIME TEST REQUIRED.** RCM does not automate gameplay. Previous tutorial acceptance does not certify the new dynamic combats.

First check setup in another folder, projects outside the program, Quick tutorial/F5, LAN with an existing carried RCM item, Showcase dialogue/cameras/notes/items/journal/travel and save/load/reentry. Edit a line, save/F5 with Redemption closed and verify it in a new game when required. Independent PC/VM, real GPU and physical 100/125/150/200% DPI remain pending.

Open chronicles/dynamic_lab/project.yaml, save/F5 with the game closed. In LAN â†’ New Game choose **RCM Â· Dynamic Encounter Lab** and start a new game. Record PASS/FAIL and retain the trace; all twelve cases need native observation.

| Case | Expected result |
|---|---|
| DYN01 | Anezka â†’ arm waves â†’ approach barrel. Entering its area creates three rats; no acceptance means no start. |
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

## Original objects and doors Â· native testing pending

In a campaign copy, use Addâ€¦ â†’ Original object / create passageâ€¦; leave the accepted tutorial unchanged.

| Case | Test and expected result |
|---|---|
| ORG01 | Hide a visible original static prop on entry: appearance and collision disappear; similar objects remain unchanged. |
| ORG02 | Restore from another event: recover its original appearance and collision. Save/load while hidden and travel/re-entry retain the desired state. |
| ORG03 | Remove: disappears. Restore reports failure rather than recreating it. Saving/loading and re-entry must not resurrect it. |
| ORG04 | Framed door: open frame 1, then close frame 0 after moving it. Check speed; for pivots, both directions and duration. Check original-script interaction and save/load separately. Compilation does not certify them. |
| ORG05 | Create an editable proximity zone with travel and a key/flag condition; approach without/with the requirement and check arrival. Original geometry remains unchanged. |
| ORG06 | Missing/ambiguous object or frameless door: logs ORIGINAL_FAILED without affecting an alternative object. Subsequent event actions continue in their normal order. |

All cases remain pending native observation. The eight-unit identity tolerance requires exactly one local prop with the selected template. This does not enable removal of baked NIL surfaces or reconstruct Door/PivotDoor script state.

## Imported WTD Â· native testing pending

| Case | Test and expected result |
|---|---|
| WTD01 | Without import, tutorial/mini behave unchanged; optional clans, disciplines and actions remain hidden. |
| WTD02 | Settings â†’ Import NOB from outside the game. Only available content; original menus and no demo chronicle. Restart and retain the catalogue. |
| WTD03 | Create a Penthouse chronicle with a valid ground entry. Check scenery, environment, navigation and static doors; compilation does not verify pathfinding. |
| WTD04 | Spawn an actor with chosen clan/discipline; check normal dialogue/animation. For an enemy using original AI, verify the chosen power, effect, sound and target. |
| WTD05 | Event grants Player a discipline, then changes level/clan. Save/load and scene re-entry retain state without duplicate rewards or reset. |
| WTD06 | Acquire a project item inheriting from WTD, finish playtest and switch chronicle through LAN. Required libraries/pack load before Crypt restoration. Never edit the profile. |
| WTD07 | Chronicle distribution contains no WTD assets. An unimported workspace explains the dependency; import and rebuild before local deployment. |

All remain pending in Redemption. Resolved dependencies do not certify every graphical/AI combination, discipline execution or multiplayer networking.

ORG07 pending: in Tenebrae, right-click the real exit, hide/restore and check passage. The two fixed back doors offer a transition, remain visible and travel to the chosen destination only when clicked.


CLICK01â€“08 â€” PENDING / PENDIENTE (new native brush layer):

| Case | Manual check |
|---|---|
| CLICK01 | One-scene project: self travel/jump cannot build; destination excludes current scene. No native launch is needed to test rejection. |
| CLICK02 | Tenebrae: right-click each back door, distinct selectable patch and editable hover label. Build/deploy; hover shows the authored label. |
| CLICK03 | Approach/walk past door: nothing happens. Click: exactly one configured action. Check selection/highlight against original geometry and collision near the edge. |
| CLICK04 | Two scenes on same/different NIL: click travel reaches chosen entry once; no repeated transition. Return and click again. |
| CLICK05 | Click note, conversation with NPC speaker, flag, quest, sequence and Event / Run. Conditions/key guard exact selected action; note/dialogue restores UI/cursor. |
| CLICK06 | Save/load with the clickable prop: same label, capture and one-time/repeatable state; no duplicated mesh or callback. |
| CLICK07 | Remove a click prop during gameplay and revisit; check intended lifecycle and no invisible blocking volume. Editor deletion/cascade and undo preserve unrelated events. |
| CLICK08 | Multiplayer: client selection reaches server once, target belongs to the correct scene; no duplicate action or transition. Not certified by doubles. |

CLICK09 / ARRIVAL01 — USER CONFIRMED for the tested new-game clicks and initial movement; load/re-entry remain PENDING: In «Mi nueva crónica» (RaveClub), start a new game, issue one nearby floor click immediately after arrival and verify the direct route; repeat after travel and save/load. Hover/click Salida: first note. Hover/click second prop: NOTA 11 and 1000 XP, exactly once per click. Walking past must not run either action. Inspect CLICK_BOUND/CLICK_RECEIVED and absence of repeated SPAWN_FAILED in RCM/new_chronicle/runtime_trace.log.

CLICK10 / ARRIVAL02 — USER CONFIRMED for the tested new-game clicks and initial movement; load/re-entry remain PENDING: «Mi nueva crónica», new game after native NSD entry build. Hover all three click props and invoke each authored action. First floor click after entry must use the correct route; repeat after travel and load. Expected trace: CLICK_BOUND and CLICK_RECEIVED; ARRIVAL_AFTER must match the authored native entry. In editor, create a fourth drippyCandle interaction: click_drippyCandle_4, editable. Right-click an unbound fixed door: temporary bounds remain during menu/dialog and disappear on cancel, without new data.

# Cinematic Director closure · EMB01–24

**MANUAL RUNTIME TEST REQUIRED.** Use a fresh copy of Help → Acceptance chronicle: the refuge, plus copies of the Showcase for specialist cases. Never alter the accepted tutorial to perform these tests. Record pass/fail, build fingerprint, save name and trace. Offline validation, real Codex compilation and doubles are separate evidence.

| Case | Procedure and expected result |
|---|---|
| EMB01 | Click the original club exit labelled Refugio. Its hover label is visible; approaching does nothing; clicking starts the configured conversation once. The user's earlier scenery click acceptance remains valid for that earlier build/scenario. |
| EMB02 | In a copy, select an original framed/pivot door with documented frames. Open, close, save, load and return. Check collision and original scripts. The refuge exit is hidden, not an animated-door demonstration. |
| EMB03 | Add a fixed-surface click overlay to a separate door. Only the selected patch highlights and runs its action; original NIL bytes stay unchanged. |
| EMB04 | Speak to Elena. OTS framing, visible participants facing each other, no T pose; cursor, movement and GUI return on finish/abort. Try a named staging entry in a copy. |
| EMB05 | In a sequence copy add three timed camera_shot Actions with different subject/reference pairs, including Player. Each runs in order and preserves control ownership. |
| EMB06 | Watch the guard LookAt and gesture in the refuge arrival. He remains visible and resumes a valid idle pose. Try another motion offered by his real NMS catalogue. |
| EMB07 | Watch the guard walk during the film. End/abort releases the camera and stops a route started by the film; routes already running before it keep their previous policy. |
| EMB08 | In a suitable scene copy select an original NCP known to belong to that geometry. It plays and ends; do not interpret a path authored elsewhere as a camera failure. |
| EMB09 | Capture one viewport camera point and save the path. In a copy play it as a fixed shot, checking position, pitch/yaw/roll and control return. No FOV key is offered. |
| EMB10 | Capture at least three distinct points. Play the path and compare order, endpoints, orientation and shortest rotation. Confirm it stays clear of walls; the editor preview does not model native clipping. |
| EMB11 | Play the same path at 15, 30 and 60. Increasing rate must shorten playback without changing endpoints. Rate is not a duration in seconds. |
| EMB12 | At entry fade from black; near the film end fade to black; clear effects and return. No lasting black screen after abort or load. |
| EMB13 | In a copy add a short white flash and white filter, then clear effects. Check actual intensity/duration. Arbitrary color presets are excluded. |
| EMB14 | Hear the positioned sound cue once while moving the camera. Check volume and distance from its waypoint; no per-tick repetition. |
| EMB15 | Finish the arrival. The normal completion event releases control, updates the journal and spawns one weak rat. Waiting, repeated clicks and a second poll must not repeat it. |
| EMB16 | Save during a cue film, load and wait. The film cancels, UI returns and no already-run side effect replays. Verify the mentor allows the scenario to continue. Separately verify old Player films retain their prior resume policy. |
| EMB17 | Abort/skip; in a separate copy remove a required actor before its cue. Expect bounded failure trace and restored controls, with no repeated failure every tick. Try a second film/conversation while one owns control. |
| EMB18 | Add line-start LookAt, camera and sound Actions to two lines. They run at the appropriate line; GOTO/RETURN still work. Opening another modal interaction from a line is rejected, including through run_event. |
| EMB19 | In a copy start a named spatial loop on entering a trigger, stop on leaving. Save active/load, travel/return and repeat. At most one owned sound handle is recreated and Stop ends it. |
| EMB20 | In a copy attach a dynamic light to an authored prop; change style/color/radius, remove, save/load and re-enter. Test drizzle/lightRain/heavyRain/snow separately. Check appearance and state; no baked lighting is modified. |
| EMB21 | With local WTD import, use a supported actor/motion and clan/discipline in a sequence. Save/load. Without WTD, ordinary examples still work; public packages contain no imported mod assets. |
| EMB22 | Complete Arrival at the refuge: click → dialogue → film or skip → weak rat → mentor → fade/travel → epilogue. Repeat from a fresh game and from a save; no duplicate reward. |
| EMB23 | In the editor edit a point/cue/line action, undo/redo, save, close/reopen and F5. Path data stays with the project and build invalidates. Export/import project and distribution package; referenced resource deletion offers validated cascade. |
| EMB24 | On an independent supported Windows PC/VM, open the portable EN/ES editor without system Python/JDK. Select a legitimate game installation, open the example, build and run manually. Record physical DPI/GPU, camera and audio results. A moved-folder/offscreen probe is insufficient. |

The new EMB suite is pending user observation. Initial navigation and repaired original clicks were previously confirmed by the user; that does not certify new cinema, restore, re-entry or network combinations. EMB02 is resource-dependent and cannot turn fixed NIL faces into animated doors.
