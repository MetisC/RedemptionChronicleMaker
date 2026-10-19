# Optional authoring laboratory

Open Help > Authoring laboratory, then F5 and create a new game. Speak to Anezka near arrival. This is separate from the accepted tutorial and mini chronicle.

1. Stationary camera: turn 3 seconds, hold 2.5 seconds, then regain control.
2. Spawn the weak Rat, then follow it. Kill/remove it while testing interruptions; the camera must return rather than switch targets.
3. Create the neutral guest (stops the rat), wait, then check inventory. The success note requires actual native inventory membership.
4. Reveal the second map location, inspect the in-game map, then travel using Anezka's dialogue. Return from the second layout.
5. Walk near the guard for the native bell region. The larger zone by the rat corner activates an owned sound loop and blue point light. Leave/re-enter; save/load and repeat.

EAX roomtype uses the original console command and requires a compatible native 3D audio provider. Neither compilation nor doubles prove visual/audio/native-save behaviour. Read docs/MANUAL_RUNTIME_CHECKLIST.md for the exact observations. All models, sounds and geometry are references to the user's game, not redistributed assets.

The turn is a Player film without cues: after save/load it follows the existing replay-from-start policy. NPC/dynamic-target films and films with cues cancel on restore. Test control recovery and no duplicate completion rewards separately.
