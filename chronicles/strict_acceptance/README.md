# Cargo at the refuge — optional native acceptance

Open project.yaml in RCM, build and use Test in Redemption. Start a new game.
Knock on the refuge door, speak to Elena, watch or skip the keeper, defeat the
weak Rat, then follow Elena. The tutorial and mini chronicle are unchanged.

Before leaving, inspect the floating barrel and the two supply barrels near
the keeper. The left supply barrel uses native treasure class 230; the other
inherits its template. Break them to compare native loot (random, not guaranteed
on one attempt). Cargo motion uses ClassBobbing, scalar parameters and a thing
link; edit it under Object > Native script. Frame 0 is the initial transform;
the named cargo_high waypoint is frame 1. These are ordinary editor controls.

Level > Environment configures fog, audio volumes and ZClip. Elena > Instance
properties sets only her hover text and Foley. In the epilogue a waypoint has
native interest group 8; matching active AI is required to demonstrate interest
selection. This marker alone does not certify AI behaviour.

All new native behaviour is MANUAL RUNTIME TEST REQUIRED. No original assets
or Java classes are copied into this example. Geometry remains immutable.
