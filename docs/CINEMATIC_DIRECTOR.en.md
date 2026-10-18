# Cinematic Director

Use **Campaign → select a sequence**. No extra main tab is needed. Existing shots and original camera paths still work.

## Make a camera path

1. Open the 3D viewport and frame your first view.
2. Select a sequence, then **Create / edit project camera path…**. The small window stays open while you navigate in 3D.
3. Move the viewport camera and choose **Point from this view**. Repeat for the remaining points.
4. Select a point to edit its position/orientation. Insert, update, duplicate, remove and reorder points with the buttons. A duplicate must be moved before accepting: consecutive positions cannot coincide.
5. Accept. The whole edit is one undo operation. Choose **Camera path** as the sequence camera type if necessary, and set its speed. F5 builds the native NCP automatically.

A static path needs one point. Moving paths use linear interpolation and up to 128 points, the original engine's buffer limit. The viewport displays the path and viewing directions; it does not preview native camera collision or guarantee identical framing. No FOV field is invented. Project resources retain the creation scene/level, and validation warns about cross-scene reuse.

## Choreograph a scene

The sequence's **Scene timeline** is an ordered list of times and ordinary Actions. Add a scene action, set its time and use **Edit actions…**. The inspector is the same one used by events and scenery clicks.

Useful actions include a shot or camera path, Look at actor/point, Play gesture, Start patrol, positioned sound, fade, flag, quest or Event / Run. Motion choices come from the selected model's actual motionset. Existing shot steps and prop movement remain available. The 150 ms runtime tick quantises cue times; equal-time cues preserve their list order. A sequence supports up to 64 cues, like the existing shot budget, and its established maximum duration remains 120 seconds.

Fades provide **From black**, **To black** and custom intensities. White flash and white filter use the native API; arbitrary packed colours are deliberately not exposed. Use **Clear effects** to remove active camera effects. A failed cue cancels the film and returns control; an interrupted cue film is cancelled on load rather than replaying rewards or other side effects. Existing Player films without cues retain their established restore behaviour.

## Coordinate dialogue

Select a dialogue line and choose **Actions when this line starts…**. Set a close-up, a look, gesture, sound or state change without changing RETURN/GOTO. Start another conversation, a film, a note or travel after the dialogue ends, rather than opening competing interfaces from a line.

The conversation's **Staging** option can use a named existing entry. It relocates the party through the native entrance mechanism and applies the authored orientation before dialogue. It does not create a second set of spatial markers or rewrite the level.

## Sound, light and weather

Positioned sound supports one-shot playback or a named loop while the scene is active. The loop uses an existing waypoint, volume and full/audible radii. Use **Stop positioned sound** with its name. Up to 32 named loops is an RCM ownership/polling budget, not a claimed engine limit. Save/load records active ownership and recreates each handle once; leaving the scene stops owned sounds.

Dynamic light attaches to one of your entities. Set RGB components, intensity, radius and an original light style; use Remove dynamic light to clear it. Light configuration and supported weather choices participate in the new save contract. Weather choices are limited to names actually used by original scripts. Baked lighting, fog/lightmap editing and geometry remain outside scope.

## Try the examples

- **Help → Acceptance chronicle: the refuge** opens a separate short acceptance adventure. Knock on the original Refuge door, speak to Elena, watch or skip the film, defeat the basic rat and speak to Elena again. It then travels to a second scene.
- In **Full showcase**, the guide's optional laboratories menu offers the **Cinematic Director Lab**. The main book errand is preserved. Existing personal copies are never overwritten; request a fresh example copy if yours predates this addition.

The refuge door demonstrates hiding/restoring native scenery and clearing collision. It does **not** pretend that its frameless original mesh has an opening animation. Compatible framed/pivot doors retain their existing tools.

New data remains optional in project formats 9/10. Opening an older project never upgrades it. Structural cinematic/audio/light changes can require a new game; RCM reports the changed save contract. See EMB01–24 in the manual checklist: compilation and offline tests are not visual/audio acceptance in Redemption.
