# Step-by-step tutorial: one map, seven lessons

Start a **new game** in **RCM · Tutorial paso a paso**. The story and dialogue remain in Spanish; changing editor language does not rewrite your authored content. Close the prologue and talk to Tomás in front of the start. The journal gives one current objective; complete or skip a lesson to meet the next teacher there. The optional laboratory is on the left, on the same street.

| Lesson | In the game | In the editor |
|---|---|---|
| 1. Start | Talk to Tomás; continue or skip. | [Starting entry](rcm://workshop/entries/safe). 3D Space → Start, position/orientation/default arrival. |
| 2. Dialogue | Vera demonstrates 13 shots individually. Choose next or skip the rest. | [Introduction](rcm://workshop/conversations/camera), [first shot](rcm://workshop/conversations/framed). Dialogue camera in Properties. |
| 3. Cinematic | Anezka introduces a twelve-second sequence with door opening, walking and a final shot. Watch or skip. | [Sequence](rcm://workshop/sequences/walk_scene), [door model](rcm://workshop/objects/stage_door), [movement](rcm://workshop/paths/walker_walk). |
| 4. Inventory | Elena gives a physical bone key; leave room in the inventory grid. Skipping also provides it. | [Elena](rcm://workshop/actors/keeper) → Edit initial inventory → + From catalogue. [Item and flag](rcm://workshop/events/next_4). T_tutor_key keeps BoneKey's model/icon and sets item_type to 0. |
| 5. Layout | Click the barrel for a note, then talk to the agent. With the key, change layout: same street, previous teachers/barrel removed. | [Change](rcm://workshop/events/change_layout) requires Has item key. + Scene creates a layout; travel chooses scene/entry. |
| 6. Encounter | Ask for one basic rat near the start. Kill it or skip. | [Encounter](rcm://combat/encounters/one_rat), [completion](rcm://combat/events/cleared). Removing without killing does not award combat completion. |
| 7. Save | Save/reload and check key/teacher. Finish or skip. | [Final dialogue](rcm://finished/conversations/final). Save writes YAML, Build compiles, Deploy updates RCM. Save the game inside Redemption. |

The barrel is scenery with a note, not a physical door. Skipping prepares the next lesson. Completed objectives may remain in journal history.

## Camera examples

The default is a close shoulder view toward the speaker, also used when YAML omits the camera. The engine automatic view remains an explicit option. Each example lets you advance or skip the remaining shots:

| Example | Shot |
|---|---|
| [1](rcm://workshop/conversations/framed) | Over your shoulder, close to Vera |
| [2](rcm://workshop/conversations/frame_2) | Extreme close-up of Vera |
| [3](rcm://workshop/conversations/frame_3) | Extreme close-up of your character |
| [4](rcm://workshop/conversations/frame_4) | Close-up of Vera |
| [5](rcm://workshop/conversations/frame_5) | Close-up of your character |
| [6](rcm://workshop/conversations/frame_6) | Over Vera's shoulder, close to you |
| [7](rcm://workshop/conversations/frame_7) | Wider view over your shoulder |
| [8](rcm://workshop/conversations/frame_8) | Wider view over Vera's shoulder |
| [9](rcm://workshop/conversations/frame_9) | Vera in profile |
| [10](rcm://workshop/conversations/frame_10) | Your character in profile |
| [11](rcm://workshop/conversations/frame_11) | Both characters |
| [12](rcm://workshop/conversations/frame_12) | Medium shot |
| [13](rcm://workshop/conversations/frame_13) | Full-body shot |

## Optional laboratory

The [laboratory actor](rcm://workshop/actors/lab) is separate from the teachers. Start/stop [his path](rcm://workshop/paths/lab_walk), pause/resume AI, set/clear a flag, or try the experimental original [EASTOttoVan camera path](rcm://workshop/sequences/original_path). Approach the [book trigger](rcm://workshop/triggers/station) to collect an item; Read trace shows entry, exit and pickup.

The animation teacher offers rest, idle gesture, talking, listening and five ST_Christof_MD gestures. In [his conversation](rcm://workshop/conversations/lab), select a node such as `gesture10` and choose Speaking animation. A line overrides its node; without an explicit motion the engine uses talking/listening. Only available character motions are offered.

Read the laboratory note example. For your objects, **Add note on use** opens/creates their event. **Story / Show note** also supports prologues and other text windows. The [cinematic](rcm://workshop/sequences/walk_scene) starts with a wide aerial view and zero initial transition; edit individual shots there.

## Verification and limits

Editor 0.9.13 leaves native gameplay unchanged. Existing code was compiled against the real API and checked with Java doubles; the latest actor visibility/notes changes still need visual confirmation in Redemption. Test cameras, animations, layouts and save/load separately. Use a new game for gameplay revision 0.9.12; older saves have no migration.

Local position/orientation are restored after player creation on load. Explicit travel uses its entry. Repeated position rejection falls back to the native position and logs failure without blocking logic. No geometry editing; the cinematic door is moving scenery, not an embedded door. Full embedded-door handling, a custom NCP writer and multiplayer remain limited.
