# Storyteller's Workshop

This Showcase is a short adventure with an optional laboratory. It demonstrates how RCM's existing tools work together and links to their examples in the editor. Follow the errand or stop to experiment; you do not have to visit every station.

## Start here

1. Open the Showcase and press **F5** to prepare it. Enter your chronicle manually in Redemption.
2. At the workshop, speak to [Anezka](rcm://quay/actors/victoria) and accept the errand. The [opening conversation](rcm://quay/conversations/intro) is linked here for editing.
3. Speak to the [guide](rcm://quay/actors/guide) beside her. Choose the journey to the archive to continue the story; the other choices belong to the optional laboratory.
4. At the archive, speak to the [archivist](rcm://archive/actors/archivist) and decide how to obtain the book.
5. With the book and key, speak to the [keeper](rcm://archive/actors/keeper) to return.
6. Speak to the [witness](rcm://return/actors/witness) to finish the delivery. The courier can take you back to the beginning.

## Main route

The [workshop](rcm://quay/scene/quay) uses EastLondon. The [archive](rcm://archive/scene/archive) uses another location. The [return](rcm://return/scene/return) reuses EastLondon with different characters and state: a scene is a content layer, not new geometry.

The [book quest](rcm://quay/quests/ledger) tracks progress in the journal. Your [decision at the archive](rcm://archive/conversations/ledger) changes the witness's response. Both branches reach the ending. Return to the beginning to review what the story remembers; rewards should only be granted once.

## Optional laboratory

### Cameras

Ask the guide to show the shots one at a time. Start with the [first camera conversation](rcm://quay/conversations/cam1) and use Next to compare framing. Select a conversation in the editor to change its camera in Properties. The [arrival sequence](rcm://quay/sequences/sequence1) is a separate cinematic example.

### Animations

The [gesture conversation](rcm://quay/conversations/anim) only offers animations available on the guide's model. Select a node or line to find its animation setting. Each model has its own repertoire.

### Paths / Waypoints

The guide's path and sound choices let you start and stop a walk. The [path](rcm://quay/paths/guide_walk) connects [its first waypoint](rcm://quay/waypoints/guide_a) to [the second](rcm://quay/waypoints/guide_b). Geometry stays unchanged; check actual navigation while playing.

### Sound

The same [laboratory conversation](rcm://quay/conversations/lab) plays music, ambience and thunder from [a point in the street](rcm://quay/waypoints/audio). It also stops music and ambience. The [sound event](rcm://quay/events/controls4) links to these actions in the editor.

### Objects and notes

Click the [notice](rcm://quay/objects/notice) to read a note; closing it can continue an event. The [lectern](rcm://quay/objects/talkprop) starts a conversation from an object. The [laboratory book](rcm://quay/objects/sample) demonstrates pickup and a state change. The [guide's key](rcm://quay/objects/lab_key) belongs to her initial inventory.

### Optional combat

The guide only activates [the rat](rcm://quay/actors/enemy1) when you explicitly choose combat. It is a basic enemy and **fighting is not required to finish the story**. You can skip combat from the guide's conversation.

## Field test

Travel to the archive and return to check locations, arrivals and two scenes using the same geometry. The keeper also offers an [optional camera and sound test](rcm://archive/sequences/two_shot).

Save and load, return to the start and repeat an interaction. Check that the journal, inventory, choices and rewards retain the expected state. You perform these checks in Redemption; compilation and offline tests do not certify the gameplay route.

Guide links select project elements in the editor. The following index retains all reference links; you do not need it to play the adventure.

## Complete technical index

- [quay · safe](rcm://quay/entries/safe)
- [quay · victoria](rcm://quay/actors/victoria)
- [quay · guide](rcm://quay/actors/guide)
- [quay · enemy1](rcm://quay/actors/enemy1)
- [quay · notice](rcm://quay/objects/notice)
- [quay · sample](rcm://quay/objects/sample)
- [quay · talkprop](rcm://quay/objects/talkprop)
- [quay · lab_key](rcm://quay/objects/lab_key)
- [quay · arrival_zone](rcm://quay/triggers/arrival_zone)
- [quay · trigger1](rcm://quay/triggers/trigger1)
- [quay · guide_a](rcm://quay/waypoints/guide_a)
- [quay · guide_b](rcm://quay/waypoints/guide_b)
- [quay · audio](rcm://quay/waypoints/audio)
- [quay · guide_walk](rcm://quay/paths/guide_walk)
- [quay · sequence1](rcm://quay/sequences/sequence1)
- [quay · intro](rcm://quay/conversations/intro)
- [quay · pact](rcm://quay/conversations/pact)
- [quay · guide](rcm://quay/conversations/guide)
- [quay · cleared](rcm://quay/conversations/cleared)
- [quay · cam1](rcm://quay/conversations/cam1)
- [quay · cam2](rcm://quay/conversations/cam2)
- [quay · cam3](rcm://quay/conversations/cam3)
- [quay · cam4](rcm://quay/conversations/cam4)
- [quay · cam5](rcm://quay/conversations/cam5)
- [quay · cam6](rcm://quay/conversations/cam6)
- [quay · cam7](rcm://quay/conversations/cam7)
- [quay · cam8](rcm://quay/conversations/cam8)
- [quay · cam9](rcm://quay/conversations/cam9)
- [quay · cam10](rcm://quay/conversations/cam10)
- [quay · cam11](rcm://quay/conversations/cam11)
- [quay · cam12](rcm://quay/conversations/cam12)
- [quay · cam13](rcm://quay/conversations/cam13)
- [quay · lab](rcm://quay/conversations/lab)
- [quay · anim](rcm://quay/conversations/anim)
- [quay · arrival](rcm://quay/events/arrival)
- [quay · new](rcm://quay/events/new)
- [quay · remember](rcm://quay/events/remember)
- [quay · accept](rcm://quay/events/accept)
- [quay · to_archive](rcm://quay/events/to_archive)
- [quay · cleared_trip](rcm://quay/events/cleared_trip)
- [quay · combat](rcm://quay/events/combat)
- [quay · combat_done](rcm://quay/events/combat_done)
- [quay · arrival_trigger](rcm://quay/events/arrival_trigger)
- [quay · end1](rcm://quay/events/end1)
- [quay · event1](rcm://quay/events/event1)
- [quay · cam_next1](rcm://quay/events/cam_next1)
- [quay · cam_next2](rcm://quay/events/cam_next2)
- [quay · cam_next3](rcm://quay/events/cam_next3)
- [quay · cam_next4](rcm://quay/events/cam_next4)
- [quay · cam_next5](rcm://quay/events/cam_next5)
- [quay · cam_next6](rcm://quay/events/cam_next6)
- [quay · cam_next7](rcm://quay/events/cam_next7)
- [quay · cam_next8](rcm://quay/events/cam_next8)
- [quay · cam_next9](rcm://quay/events/cam_next9)
- [quay · cam_next10](rcm://quay/events/cam_next10)
- [quay · cam_next11](rcm://quay/events/cam_next11)
- [quay · cam_next12](rcm://quay/events/cam_next12)
- [quay · guide_lab4](rcm://quay/events/guide_lab4)
- [quay · guide_lab5](rcm://quay/events/guide_lab5)
- [quay · guide_lab6](rcm://quay/events/guide_lab6)
- [quay · guide_lab7](rcm://quay/events/guide_lab7)
- [quay · cleared_lab4](rcm://quay/events/cleared_lab4)
- [quay · cleared_lab5](rcm://quay/events/cleared_lab5)
- [quay · cleared_lab6](rcm://quay/events/cleared_lab6)
- [quay · cleared_lab7](rcm://quay/events/cleared_lab7)
- [quay · controls1](rcm://quay/events/controls1)
- [quay · controls2](rcm://quay/events/controls2)
- [quay · controls3](rcm://quay/events/controls3)
- [quay · controls4](rcm://quay/events/controls4)
- [quay · controls5](rcm://quay/events/controls5)
- [quay · sample_taken](rcm://quay/events/sample_taken)
- [quay · talk_prop](rcm://quay/events/talk_prop)
- [quay · read_notice](rcm://quay/events/read_notice)
- [quay · notice_closed](rcm://quay/events/notice_closed)
- [quay · left_zone](rcm://quay/events/left_zone)
- [quay · clock](rcm://quay/events/clock)
- [quay · rat_killed](rcm://quay/events/rat_killed)
- [quay · state_lab](rcm://quay/events/state_lab)
- [archive · safe](rcm://archive/entries/safe)
- [archive · archivist](rcm://archive/actors/archivist)
- [archive · keeper](rcm://archive/actors/keeper)
- [archive · book](rcm://archive/objects/book)
- [archive · key](rcm://archive/objects/key)
- [archive · arrival_zone](rcm://archive/triggers/arrival_zone)
- [archive · sound](rcm://archive/waypoints/sound)
- [archive · keeper_a](rcm://archive/waypoints/keeper_a)
- [archive · keeper_b](rcm://archive/waypoints/keeper_b)
- [archive · keeper_walk](rcm://archive/paths/keeper_walk)
- [archive · two_shot](rcm://archive/sequences/two_shot)
- [archive · ledger](rcm://archive/conversations/ledger)
- [archive · back](rcm://archive/conversations/back)
- [archive · arrival](rcm://archive/events/arrival)
- [archive · peace](rcm://archive/events/peace)
- [archive · force](rcm://archive/events/force)
- [archive · to_return](rcm://archive/events/to_return)
- [archive · camera](rcm://archive/events/camera)
- [archive · arrival_trigger](rcm://archive/events/arrival_trigger)
- [return · safe](rcm://return/entries/safe)
- [return · witness](rcm://return/actors/witness)
- [return · courier](rcm://return/actors/courier)
- [return · arrival_zone](rcm://return/triggers/arrival_zone)
- [return · courier_a](rcm://return/waypoints/courier_a)
- [return · courier_b](rcm://return/waypoints/courier_b)
- [return · courier_walk](rcm://return/paths/courier_walk)
- [return · peace](rcm://return/conversations/peace)
- [return · force](rcm://return/conversations/force)
- [return · final](rcm://return/conversations/final)
- [return · back](rcm://return/conversations/back)
- [return · arrival](rcm://return/events/arrival)
- [return · peace](rcm://return/events/peace)
- [return · force](rcm://return/events/force)
- [return · final](rcm://return/events/final)
- [return · back](rcm://return/events/back)
- [return · finish_peace](rcm://return/events/finish_peace)
- [return · finish_force](rcm://return/events/finish_force)
- [return · arrival_trigger](rcm://return/events/arrival_trigger)
