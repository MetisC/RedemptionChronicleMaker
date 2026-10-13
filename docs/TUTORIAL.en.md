# Una carta al amanecer

A short tutorial on two EastLondon layouts sharing unchanged geometry.

1. Arrive in the street. Anezka stands ahead. The journal has one errand with the next objective visible.
2. Accept her request. RETURN 1 activates go_to_square through a normal event. Declining or aborting does not set it.
3. Approach the barrel standing alone in the open section of the street, near your starting point. You do not need to click it: walking beside it starts the demonstration. Its area is trigger1. Entering before acceptance does not run the film; leave and enter again after accepting.
4. A six-second film presents **your character**: high wide shot, then a smooth close-up transition. Completion releases camera/control, sets square_reached and advances the journal. This uses SetShot, not continuous XYZ dolly movement.
5. A book representing the letter and Tomás appear. Pick up the book, labelled Carta para Elena in the inventory. It does not need to be opened or used. One basic Rat spawns. Kill it, or ask Tomás to skip combat. Skipping opens the route without the combat reward.
6. Talk to Anezka again after defeating the rat or skipping combat. Her follow-up dialogue offers Llévame a Elena; choose it to travel to the second layout and its arrival point. Give Elena the letter. Complete the journal and receive the reward once.
7. In the editor, save, validate, build and deploy with the game closed.

Loading during the new Player film restarts it after restoring the player's saved position. Completion is delivered once. Existing NPC films keep their cancel-on-load contract. Structural changes require a new game; native saves are not migrated.

Tutorial / Help has links to select each element or open the corresponding assistant. Previous technical experiments remain in examples/advanced_tutorial, outside the main story.

After delivery, return to the visible barrel in Elena's street to travel back to Anezka and check reentry without repeating the film or rewards.
