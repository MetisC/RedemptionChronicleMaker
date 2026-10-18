======================================================================
REDEMPTION CHRONICLE MAKER
STRICT 100% EMBRACE AUTHORING PARITY
NON-GEOMETRY FINAL CLOSURE
======================================================================

MISSION

Perform the definitive, evidence-driven closure of Redemption Chronicle
Maker against the useful NON-GEOMETRY authoring capabilities of the
original Vampire: The Masquerade — Redemption Embrace toolchain.

This is NOT another generic feature phase.

This task exists because the previous parity audit used a criterion that
was sometimes too permissive.

From now on:

    “RCM can preserve the value”
    is NOT automatically authoring parity.

    “The user could write custom Java”
    is NOT automatically authoring parity.

    “The same outcome might be possible somehow”
    is NOT automatically authoring parity.

The strict target is:

    IF EMBRACE LET A NORMAL CHRONICLE AUTHOR CONFIGURE
    A MATERIAL NON-GEOMETRY BEHAVIOUR,

    RCM MUST EITHER:

    A) expose the same author intent through normal RCM UI,

    B) expose a clearly equivalent RCM abstraction through normal UI,

    OR

    C) prove with evidence that the original capability is irrelevant,
       inseparable from geometry, unsupported by the runtime, or cannot
       be authored safely without speculative binary writing.

The desired end state is:

    “For normal chronicle authoring over existing Redemption levels,
     there is no material reason to launch Embrace.”

======================================================================
ABSOLUTE SCOPE BOUNDARY
======================================================================

PERMANENTLY OUT OF SCOPE:

- brush creation
- CSG
- wall/floor/room modelling
- vertex/edge/face geometry editing
- structural NIL modification
- structural sectors
- structural portals
- UV mapping
- structural texturing
- baked lightmaps
- lightmap generation
- terrain modelling
- mesh modelling
- Embrace MAP authoring
- recreating the 2D brush editor
- creating geometry for Quick Doors
- a mini Blender
- a mini Radiant
- rebuilding Embrace as a level editor

These do NOT count against the 100% target.

The target is:

    100% OF MATERIAL NON-GEOMETRY CHRONICLE AUTHORING.

======================================================================
STRICT PARITY RULE
======================================================================

Rebuild the parity matrix using this stricter test.

A capability is COVERED only when an ordinary author can express the
relevant intention in RCM without:

- editing generated Java,
- writing raw YAML,
- manually editing binary files,
- manually creating CODEXPVALUE values,
- manually using Embrace,
- manually invoking old SDK authoring tools.

Custom Java remains an escape hatch.

It does NOT count as ordinary parity.

A preserved original environment profile does NOT count as editable
environment authoring.

A raw technical inspector does NOT count as an author-facing editor.

A low-level backend capability invisible from normal UI does NOT count
as completed authoring.

“Covered differently” is allowed ONLY if the normal RCM workflow reaches
the same material author intent.

======================================================================
0. AUDIT CURRENT HEAD FROM ZERO
======================================================================

Start from the real current repository HEAD.

At the time this requirement was written, the observed HEAD was:

    51982be45c9931495c4655d02239178b053e189a

DO NOT assume that remains current.

Resolve HEAD first.

Read actual implementation, not historical reports.

Mandatory sources:

    research/sdk/embrace_manual.htm.txt
    research/sdk/cutscene.htm.txt
    research/sdk/Codex*.htm.txt
    research/sdk/sdk_contents.htm.txt

    research/API_SIGNATURES.txt

    research/engine_evidence/*
    research/embrace_closure/*
    research/original/* when available
    original Resource.nob contents where needed

    docs/EMBRACE_AUTHORING_PARITY.md
    docs/FINAL_PRODUCT_REPORT.md
    docs/SCENE_MODEL.md
    docs/FORMAT_NOTES.md
    docs/NOT_FORMAT.md
    docs/ENGINE_NOTES.md

    src/rcm/formats.py
    src/rcm/not_library.py
    src/rcm/not_inspector.py
    src/rcm/project_resources.py
    src/rcm/editor/resource_panel.py
    src/rcm/editor/inspector.py
    src/rcm/campaign.py
    src/rcm/campaign_generator.py

and any newer relevant files.

======================================================================
1. CREATE A STRICT EMBRACE INVENTORY
======================================================================

Create:

    research/embrace_strict_parity/
        EMBRACE_CAPABILITY_INVENTORY.md

Do NOT start from the existing parity matrix.

Reconstruct the non-geometry authoring capabilities from the original
manual and original runtime evidence.

For every Embrace control or authoring concept, classify:

    GEOMETRY_ONLY
    NON_GEOMETRY_MATERIAL
    NON_GEOMETRY_OBSCURE
    EDITOR_ONLY
    RUNTIME_RELEVANT
    UNKNOWN

At minimum audit:

THING / TEMPLATE AUTHORING
--------------------------

- template placement
- transforms
- template inheritance
- Script
- Foley
- AIClass
- DescriptionID
- TreasureClass
- script property removal
- template files / external NOT libraries
- light properties
- sound properties

SCENE AUTHORING
---------------

- scene layers
- music
- music volume
- ambient
- ambient volume
- EAX
- fog mode
- fog colour
- fog Distance 1
- fog Distance 2
- ZClip
- sky NOD
- sky NAD

SPATIAL / WORLD
---------------

- playerstarts
- convstarts
- interestspots
- paths
- regions
- sound objects
- soundboxes
- lights
- lightboxes
- exits
- doors
- selectable objects

SCRIPTING
---------

- script assignment
- Codex Linker
- CODEXPVALUE
- string parameters
- int parameters
- float parameters
- thing parameters
- actor parameters
- target links
- custom scripts

CINEMATIC
---------

- fixed camera
- SetShot
- path cameras
- camera keyframes
- fades
- flashes
- filters
- actor choreography
- convreached choreography
- LookAt
- motions
- moving actors
- camera release

RESOURCE AUTHORING
------------------

- original resource libraries
- added NOT libraries
- AI files
- sounds
- foley
- models
- animations
- external mod content

For each capability record:

    ORIGINAL UI
    ORIGINAL FILE/API
    ORIGINAL RUNTIME USAGE
    RCM BACKEND
    RCM NORMAL UI
    STATUS
    EVIDENCE
    TEST REQUIRED

======================================================================
2. REWRITE THE DEFINITION OF “COVERED DIFFERENTLY”
======================================================================

A row may be marked COVERED DIFFERENTLY only if:

1. The user can express the same practical intention.
2. It is available through normal RCM UI.
3. It does not require custom Java.
4. It does not require raw YAML.
5. It does not require editing engine files manually.
6. Save/load/reference semantics are acceptable.
7. The difference does not remove a meaningful authoring capability.

Example:

    Embrace layers
        vs
    RCM per-scene entity ownership

may genuinely be COVERED DIFFERENTLY.

Example:

    Embrace editable Fog RGB/Distance
        vs
    RCM preserving some original scene's opaque environment bytes

is NOT full coverage.

That is PARTIAL.

======================================================================
3. GAP A — COMPLETE THING / TEMPLATE OVERRIDES
======================================================================

The original Embrace manual explicitly exposes:

    Script
    Foley
    AIClass
    DescriptionID
    TreasureClass

for placed templates.

Current RCM backend already recognises several corresponding NOT tags.

Observed known tags include:

    4   model
    6   foley
    9   motions
    11  script
    56  ai
    81  cast_id
    82  description_id
    114 actor_flags

Verify against current HEAD and primary evidence.

----------------------------------------------------------------------
3.1 EXPOSE ALREADY-SAFE TEMPLATE PROPERTIES
----------------------------------------------------------------------

The current backend supports typed conservative editing for several
properties that normal Resource UI does not expose.

Audit and, where safe, expose:

    Foley
    MotionSet / motions
    DescriptionID

Do not merely expose raw tag numbers.

UI example:

    Template propio

      Base
      Modelo
      AI
      Script

      Apariencia y comportamiento
        Foley
        Motion set
        Texto al señalar

Use catalogues where possible.

Do not make users type file paths.

----------------------------------------------------------------------
3.2 DESCRIPTION ID / HOVER TEXT
----------------------------------------------------------------------

Embrace DescriptionID maps to an NLS string key.

RCM already generates NLS data for own resources and already supports
hover text in click interactions.

Unify the author-facing intention.

Preferred UX:

    Texto al señalar:
        [Una vieja caja de madera]

RCM decides the NLS key.

Do NOT force the author to invent:

    DESCRIPTION_MY_BOX_3

unless advanced mode explicitly exposes the technical key.

Ensure:

- unique generated key
- NLS generation
- rename safety
- localization behaviour
- references
- package/export
- save/reopen

Do not confuse:

    selectable click overlay hover text

with:

    generic template DescriptionID.

Both may exist and should have coherent precedence.

======================================================================
4. GAP B — TREASURECLASS
======================================================================

This is explicitly documented by the original Embrace manual.

A placed breakable/lootable container could receive:

    TreasureClass

The manual points to:

    GAME.NTT
    CLASS: entries

The repo contains an original game.ntt sample/evidence.

DO NOT invent TreasureClass representation.

----------------------------------------------------------------------
4.1 RESEARCH
----------------------------------------------------------------------

Study:

- GAME.NTT format documentation in the SDK archive.
- Original GAME.NTT.
- All original NOT/NSD references to TreasureClass.
- Ordered engine property names.
- Executable reader/property lookup if necessary.
- Scripts interacting with treasure.
- Container templates.

Determine exactly:

- where TreasureClass is stored;
- property/tag ID if applicable;
- type and range;
- inheritance behaviour;
- default behaviour;
- valid class catalogue;
- whether zero/none has semantic meaning.

Create:

    research/embrace_strict_parity/treasure_class.md
    research/embrace_strict_parity/treasure_catalogue.json

----------------------------------------------------------------------
4.2 IMPLEMENT
----------------------------------------------------------------------

If safely demonstrated:

For container-capable templates/entities:

    Loot / Treasure
        Heredar de la plantilla
        Sin treasure class
        <human-readable class list>

Show technical class ID in tooltip/advanced mode.

Do NOT offer TreasureClass on entities for which the original engine
does not meaningfully support it.

Do not create a new loot system.

Use the engine's original treasure system.

----------------------------------------------------------------------
4.3 ACCEPTANCE
----------------------------------------------------------------------

Create manual test:

    EMB-TREASURE-01

Place/create a known breakable container with a non-default
TreasureClass, break/open it in Redemption and confirm the resulting
native loot behaviour.

Also test inherited/default behaviour.

======================================================================
5. GAP C — CODEX LINKER / NATIVE SCRIPT PARAMETERS
======================================================================

This is a MAJOR strict-parity item.

The original Embrace Codex Linker lets an author assign a script and bind
its parameters.

Documented parameter types include at least:

    string
    int
    float
    thing
    actor

and potentially other demonstrated types.

The current parity matrix must NOT mark this fully covered solely because
RCM has:

    Events
    Actions
    Conditions
    custom Java

Those are excellent abstractions, but they do not necessarily let an
ordinary author reuse every useful original parameterised script.

----------------------------------------------------------------------
5.1 INVESTIGATE SCRIPT PARAMETER STORAGE
----------------------------------------------------------------------

Study:

- Embrace manual Codex Linker section.
- SCRIPT / CODEXNAME / CODEXTARGETNAME / CODEXCLASSNAME.
- CODEXPVALUE.
- entities.def if available.
- original NSD entities with parameterised scripts.
- original NOT templates using parameterised scripts.
- Codex classes.
- class metadata/reflection mechanisms.
- executable NSD entity loader.
- variable blocks following NSD entity tags.

Current `formats.py` explicitly states that the generic NSD subset does
not support script parameters.

Treat this as a real codec gap until disproven.

Determine:

- exact binary representation;
- parameter count;
- order;
- type encoding;
- thing/actor reference representation;
- scalar encoding;
- null/default values;
- how parameter descriptions/types are discovered by Embrace;
- whether script metadata can be reconstructed from Java classfiles,
  entities.def, SDK metadata or another file.

Create:

    research/embrace_strict_parity/codex_linker_format.md
    research/embrace_strict_parity/script_parameter_catalogue.json

----------------------------------------------------------------------
5.2 SUPPORT ORIGINAL SCRIPT CATALOGUE
----------------------------------------------------------------------

Where reliable parameter metadata exists, RCM should let the author do:

    Script nativo · avanzado

        Script:
            <original script>

        Parámetros:

            Puerta objetivo:
                Door01

            Actor:
                Guard

            Cantidad:
                3

            Texto:
                hello

Use typed widgets.

For actor/thing parameters:

- select RCM entity IDs;
- use References;
- rename safely;
- Safe Delete must detect dependencies;
- never expose raw GUID as normal UX.

For int/float/string:

- typed controls;
- demonstrated ranges where known;
- otherwise conservative bounded values.

----------------------------------------------------------------------
5.3 ORIGINAL AND CUSTOM SCRIPTS
----------------------------------------------------------------------

The system should support:

A)
    original stock scripts with demonstrated parameter metadata

B)
    RCM custom Java scripts if equivalent metadata can be declared safely

Do NOT parse arbitrary Java source with regex and pretend that is a type
system.

If custom script metadata needs an explicit small RCM declaration,
design it conservatively.

----------------------------------------------------------------------
5.4 DO NOT DUPLICATE RCM ACTIONS
----------------------------------------------------------------------

Normal users should still use:

    Events
    Actions
    Conditions

for ordinary authoring.

Native Script is an ADVANCED escape route for original engine behaviours
not modelled by Actions.

Do NOT encourage authors to use Door.java instead of the normal RCM Door
action.

Progressive disclosure:

    Advanced
        Native script

----------------------------------------------------------------------
5.5 GENERATION SAFETY
----------------------------------------------------------------------

Do not write generic NSD variable blocks until the format is proven.

Required:

- original roundtrip fixtures;
- bounds;
- count limits;
- type validation;
- unknown data preservation;
- reject unsupported script parameter types.

FAIL CLOSED.

----------------------------------------------------------------------
5.6 ACCEPTANCE
----------------------------------------------------------------------

Build a native acceptance case using a REAL original script that takes
at least:

    one thing/actor reference
    and
    one scalar parameter

Author it entirely through RCM UI.

No custom Java.

No manual binary edits.

Manual case:

    EMB-CODEX-01

======================================================================
6. GAP D — SCENE ENVIRONMENT AUTHORING
======================================================================

The current parity matrix is TOO GENEROUS here.

Embrace Scene Editor exposes per-scene:

    music
    music volume
    ambient
    ambient volume
    EAX

Render tab exposes:

    fog type
        linear
        exponential

    fog RGB
    Distance 1
    Distance 2
    ZClip

Sky tab exposes:

    NOD
    NAD

RCM currently preserves an original 176-byte environment profile and
knows the final 64-byte sky fields.

PRESERVATION IS NOT EDITABLE AUTHORING.

This row must be considered PARTIAL until resolved.

======================================================================
6.1 REVERSE ENGINEER THE 176-BYTE ENVIRONMENT TAIL
======================================================================

Do NOT guess offsets.

Perform a dedicated binary investigation.

Sources:

- all original NSD environment tails;
- Embrace manual semantic field list;
- executable NSD reader;
- executable scene environment application;
- API/constants;
- original script changes;
- scene combinations with known visible/audio differences.

Known confirmed structure includes:

    final 32 bytes → sky NOD
    final 32 bytes → sky NAD

The preceding region is not yet fully attributed.

Use:

- cross-file differential analysis;
- float/int/string detection;
- clustering;
- known EAX enum values if obtainable;
- executable disassembly;
- loader data flow;
- runtime setter calls if any.

Create:

    research/embrace_strict_parity/environment_tail.md
    research/embrace_strict_parity/environment_fields.json
    research/embrace_strict_parity/environment_profiles.csv

Every field must carry:

    offset
    width
    type
    meaning
    confidence
    evidence

Confidence levels:

    CONFIRMED_EXECUTABLE
    CONFIRMED_FILE_CORRELATION
    CONFIRMED_SDK
    STRONG_INFERENCE
    UNKNOWN

Only CONFIRMED fields are writable.

----------------------------------------------------------------------
6.2 FOG
----------------------------------------------------------------------

If fields are demonstrated, expose per-scene:

    Niebla
        Heredar perfil original
        Sin niebla
        Lineal
        Exponencial

        Color
        Empieza a
        Oculta completamente a
        ZClip

Respect real engine units.

Do not invent metres.

Do not “improve” exponential fog despite old hardware warnings.

----------------------------------------------------------------------
6.3 EAX
----------------------------------------------------------------------

Determine:

- field type;
- allowed presets/enums;
- original scene values;
- engine application mechanism.

If confirmed:

    Ambiente acústico / EAX
        Heredar
        <known presets>

Do not invent descriptive presets without mapping them to real engine
values.

----------------------------------------------------------------------
6.4 MUSIC / AMBIENT DEFAULTS
----------------------------------------------------------------------

RCM can already start/stop music and ambient through Actions.

Determine whether the original Scene Editor's per-scene music/ambient
fields are merely initialization semantics that RCM scene_start Actions
cover exactly enough.

If YES:

    COVERED DIFFERENTLY

but make this a NORMAL scene property UI:

    Audio inicial
        Música
        Volumen
        Ambiente
        Volumen

Generate through existing Actions if that is semantically equivalent.

The author should not need to create four startup Actions manually just
to match Embrace Scene Editor.

If native fields have behaviour Actions cannot reproduce, write the
native fields only after proof.

----------------------------------------------------------------------
6.5 SKY
----------------------------------------------------------------------

Sky NOD/NAD offsets are already demonstrated.

Ensure the CURRENT CAMPAIGN EDITOR, not only legacy/YAML code, provides:

    Cielo
        Heredar del perfil
        Modelo
        Animación

using resource catalogues.

No raw filenames when a resource browser can be used.

A sky override must:

- preserve all other environment bytes;
- validate model and animation resources;
- package dependencies correctly;
- survive reopen;
- participate in undo/redo.

----------------------------------------------------------------------
6.6 DO NOT TOUCH BAKED LIGHTING
----------------------------------------------------------------------

Changing fog/sky/EAX does NOT imply relighting the NIL.

Never claim otherwise.

World lightmaps/global baked lighting remain immutable.

======================================================================
7. GAP E — LIGHT / LIGHTBOX STRICT AUDIT
======================================================================

The Embrace Thing Editor distinguishes:

- lights exported as runtime dynamic lights
- Editor Only lights used only for baked lightmaps

The latter are OUT OF SCOPE.

Runtime dynamic lights are already represented in RCM.

Now audit:

    light
    lightbox

Determine whether a lightbox provides:

A) only baked/level-lighting behaviour
B) runtime dynamic behaviour
C) both

Use original NSDs, executable loader and scripts.

If it is A:

    OUT OF SCOPE: BAKED LIGHTING

If B/C has material runtime authoring not covered by current dynamic
lights:

implement the minimal equivalent.

Do NOT create geometric lightbox brushes simply for parity.

======================================================================
8. GAP F — INTEREST SPOTS
======================================================================

Do NOT automatically equate:

    interestspot

with:

    waypoint

The manual exposes interestspots 0–9, but the previous audit did not
identify unique semantics.

Perform a deeper investigation.

Search:

- original NSD tables;
- executable loaders;
- AI code paths;
- original Java scripts;
- template properties;
- named constants;
- original levels using interest spots.

Determine:

- storage format;
- lookup API;
- consumers;
- whether actors idle/look/wander/use them automatically;
- whether numbered slots matter;
- whether they are editor-only remnants.

Possible outcomes:

A)
Unique material AI behaviour demonstrated.

    Implement:
        AI interest point

using existing viewport marker infrastructure.

B)
Intent is genuinely equivalent to RCM paths/waypoints.

    Document exact reason and mark COVERED DIFFERENTLY.

C)
No runtime consumer found / obsolete.

    Mark:
        NOT MATERIAL / NO RUNTIME EVIDENCE

Do NOT implement speculative markers.

======================================================================
9. GAP G — SOUNDBOX STRICT AUDIT
======================================================================

RCM currently models soundbox intent using:

    trigger volume
    + start/stop spatial sound

This may be genuinely equivalent.

Prove it.

Investigate native soundbox semantics:

- shape;
- position;
- enter/leave;
- falloff;
- min/max distance;
- looping;
- multi-player behaviour;
- save/re-entry;
- whether it clips sound spatially or merely activates it.

If current RCM volumes reproduce the material behaviour:

    COVERED DIFFERENTLY

with evidence.

If a significant semantic difference exists:

implement only that missing behaviour.

No brush editor.

======================================================================
10. GAP H — GENERIC EXTERNAL TEMPLATE LIBRARIES
======================================================================

Embrace Template Files allows loading additional NOT files into the
authoring catalogue.

RCM currently has:

- game originals;
- own templates;
- WTD-specific filtered import;
- project/package import.

No generic external NOT/NOB authoring-library workflow was found during
the strict audit.

Investigate whether this is a material parity capability.

If yes, create a SAFE GENERAL CONTENT LIBRARY IMPORT.

NOT:

    “copy this whole mod into Vampire”.

Preferred concept:

    Tools
      Import content library…

Input:

    NOT
    or
    NOB containing template/resources

Pipeline:

1. scan;
2. identify templates;
3. resolve parent chains;
4. identify models;
5. identify motions;
6. identify AI;
7. identify Foley;
8. identify scripts;
9. identify textures/effects;
10. display dependency closure;
11. allow selecting safe content;
12. package locally under RCM namespace.

Never silently import:

- menu replacements;
- global UI;
- chronicles;
- unrelated resources;
- executable modifications;
- arbitrary native DLLs.

Java classes require explicit trust/review.

Do not execute imported code during import.

Imported copyrighted assets remain LOCAL dependencies unless the user
owns redistribution rights and explicitly packages them.

Reuse/genericise the proven WTD import architecture where appropriate.

WTD itself must continue to work exactly as before.

======================================================================
11. GAP I — NCP STATIONARY ROTATION
======================================================================

Keep the previous conservative decision unless new evidence resolves it.

Known:

- 174 original NCP files audited;
- 22 adjacent equal-position pairs;
- some change Euler;
- all relevant pairs also repeat path parameter;
- no demonstrated positive-span timing rule.

Do a final deeper check:

- native debug `savepath` implementation;
- native key insertion;
- native path parameter generation;
- orientation contribution to parameter;
- evaluator handling of repeated parameter;
- zero-span branch.

If duration semantics become demonstrated:

support stationary authored turns.

If not:

leave PARTIAL.

This capability alone does NOT prevent “100% material authoring” if
evidence proves it cannot be safely reproduced and normal cinematic intent
can be achieved through:

    fixed shot
    + camera shot change
    + original NCP playback.

But document it precisely.

======================================================================
12. THING OVERRIDES VS ENTITY OVERRIDES
======================================================================

Audit an important distinction:

Embrace allows changing properties on the PLACED TEMPLATE INSTANCE.

RCM project-owned templates currently provide many overrides at template
definition level.

Determine which original properties are:

    template-definition properties

versus:

    per-instance NSD entity overrides.

The user should not have to clone a whole template merely to change a
property that Embrace allowed on one placed instance.

Where the engine supports safe per-instance tags:

offer them in the Actor/Object inspector.

Example:

    Actor
      Template: businessWoman

      Overrides
        AI: inherit
        Foley: inherit
        Description: inherit
        Script: inherit

Only implement fields with demonstrated entity semantics.

Avoid template explosion.

======================================================================
13. REMOVE FALSE PARITY CLAIMS
======================================================================

Rebuild:

    docs/EMBRACE_AUTHORING_PARITY.md

Do not preserve old statuses for compatibility.

Specifically re-evaluate:

    Fog/EAX/ZClip/sky
    Codex Linker/script relationships
    Interest spots
    Template overrides
    External template libraries
    Lightboxes
    Soundboxes

Do not mark them COVERED DIFFERENTLY merely because an advanced user
could work around them.

======================================================================
14. STRICT PARITY MATRIX FORMAT
======================================================================

Every row must include:

    EMBRACE CAPABILITY
    ORIGINAL AUTHOR INTENT
    ORIGINAL EVIDENCE
    RCM NORMAL UI
    RCM ENGINE IMPLEMENTATION
    STATUS
    NATIVE TEST
    REMAINING LIMITATION

Allowed statuses:

    COVERED
    COVERED DIFFERENTLY
    PARTIAL
    NOT MATERIAL
    OUT OF SCOPE: GEOMETRY
    OUT OF SCOPE: BAKED LEVEL BUILD
    UNSAFE / INSUFFICIENT EVIDENCE
    NATIVE TEST REQUIRED

No vague green ticks.

======================================================================
15. 100% TARGET DEFINITION
======================================================================

For this project:

“100% Embrace authoring parity” means:

    100% OF MATERIAL NON-GEOMETRY AUTHORING INTENT
    NEEDED TO CREATE A NORMAL REDEMPTION CHRONICLE

It explicitly excludes:

    geometry creation
    structural sectors
    structural portals
    CSG
    UV
    baked lightmaps
    level build pipeline

It does NOT require reproducing:

    obsolete UI
    editor bugs
    unused debug controls
    texture browser ergonomics
    old preference dialogs
    exact Embrace workflow

It DOES require that a normal author no longer needs Embrace to configure
a material gameplay/narrative/runtime property.

======================================================================
16. NORMAL AUTHOR TEST
======================================================================

At the end, an author should be able to do all of this without Java or
raw YAML:

    Choose an existing Redemption level.

    Choose its environment profile.

    Override sky.

    Configure fog.

    Configure ZClip.

    Configure EAX.

    Select initial music and ambient.

    Place an NPC.

    Override that NPC's AI if desired.

    Override Foley.

    Override hover description.

    Override MotionSet where valid.

    Assign an original script.

    Fill that script's typed parameters.

    Link its actor/thing parameters to objects visually.

    Place a loot container.

    Assign a native TreasureClass.

    Add a positioned sound.

    Create a looped sound region.

    Add runtime dynamic light.

    Place arrivals.

    Place native conversation staging.

    Add interactive original scenery.

    Control an existing animated door.

    Create dialogue.

    Create quest state.

    Create encounters.

    Create a cinematic.

    Capture a custom camera path.

    Use camera effects.

    Coordinate actor motions.

    Use temporary music and restore it.

    Travel to another scene.

    Press F5.

If one of these still requires:

    Embrace
    Java
    hand-edited YAML
    raw binary work

the strict audit must explain why.

======================================================================
17. ACCEPTANCE CHRONICLE
======================================================================

Extend or create ONE dedicated strict-parity acceptance chronicle.

Do not pollute the tutorial.

It should demonstrate, where implemented:

    environment profile
    custom sky
    custom fog
    EAX
    initial music/ambient

    placed NPC
    Foley override
    Description override
    AI override
    MotionSet override

    original native parameterised script
    typed thing/actor parameter binding

    loot container + TreasureClass

    click interaction

    spatial loop / soundbox equivalent

    runtime light

    native conversation start

    cinematic
    custom NCP
    camera effects

    quest
    encounter
    travel

The scene should feel like an actual Redemption quest.

Not a button museum.

======================================================================
18. MANUAL TESTS
======================================================================

Preserve all existing manual cases.

Add focused groups:

    EMB-ENV-*
    EMB-TEMPLATE-*
    EMB-TREASURE-*
    EMB-CODEX-*
    EMB-INTEREST-*
    EMB-LIBRARY-*

only for capabilities actually implemented.

Examples:

EMB-ENV-01
    Override linear fog and visually verify colour/start/end/ZClip.

EMB-ENV-02
    Switch EAX and confirm audible environment difference where practical.

EMB-ENV-03
    Override sky model/animation.

EMB-TEMPLATE-01
    Foley override produces expected native sound set.

EMB-TEMPLATE-02
    DescriptionID hover appears correctly.

EMB-TEMPLATE-03
    MotionSet override exposes/plays valid animations.

EMB-TREASURE-01
    Native container TreasureClass produces expected loot behaviour.

EMB-CODEX-01
    Original parameterised script receives one RCM thing reference and one
    scalar parameter and behaves correctly.

Do not mark them PASS automatically.

======================================================================
19. BINARY SAFETY
======================================================================

NO SPECULATIVE WRITING.

For every new binary field:

- prove offset;
- prove width;
- prove type;
- prove bounds;
- prove ownership;
- compare original examples;
- roundtrip;
- preserve unknown bytes;
- reject unsupported variants.

Never add:

    “probably fogRed”
    “maybe EAX”
    “looks like TreasureClass”

to production writers.

If something cannot be proven:

    preserve it
    document it
    leave it unsupported

rather than corrupting NSD/NOT.

======================================================================
20. PROJECT FORMAT
======================================================================

Do NOT bump format merely because optional authoring fields are added.

Keep:

    CURRENT_PROJECT_FORMAT = 10

if backward-compatible optional fields can represent the new data.

Only introduce format 11 if an actual incompatible persistence contract
requires it.

If format 11 becomes necessary:

- justify it explicitly;
- no auto-conversion on open;
- backup before opt-in upgrade;
- future-format guard remains.

======================================================================
21. REFERENCES / SAFE DELETE / UNDO
======================================================================

Every new entity reference must participate in:

    References
    rename
    Safe Delete
    cascade preview
    undo
    redo

Especially:

    script parameter → actor
    script parameter → object
    sound region → waypoint
    environment resource → model/animation
    external content dependencies

No dangling native links.

======================================================================
22. PACKAGING
======================================================================

No original game asset redistribution.

Project-owned generated resources are packaged normally.

Imported third-party content:

- local dependency by default;
- no automatic redistribution;
- manifest records dependency;
- missing dependency fails clearly.

WTD behaviour remains unchanged.

Portable app remains:

    ZIP
    extract
    run RedemptionChronicleMaker.exe

NO installer.

======================================================================
23. FULL QUALITY GATE
======================================================================

At the end execute the complete available gate, not only focused tests.

Required:

- full Python suite
- Ruff
- configured mypy
- actual Java compile against real Codex
- classfile 45.3
- original NOT roundtrips
- original NSD relevant roundtrips
- NCP 174 regression
- new environment field corpus tests
- new Codex Linker fixtures
- TreasureClass tests
- references
- rename
- Safe Delete
- undo/redo
- project export/import
- distribution package
- portable build
- EN/ES UI probes
- current examples
- Tutorial
- Mini
- Dynamic Lab
- Showcase
- Director acceptance
- strict-parity acceptance chronicle

Record exact:

    tests
    failures
    errors
    skips

Do not reuse historical numbers.

======================================================================
24. RUNTIME STATUS LANGUAGE
======================================================================

Use only:

    IMPLEMENTED
    OFFLINE VERIFIED
    COMPILED AGAINST REAL CODEX
    PACKAGED
    DEPLOYED
    MANUAL RUNTIME TEST REQUIRED
    RUNTIME VERIFIED
    RUNTIME FAILED

Never turn successful compilation into runtime verification.

The user performs native Redemption tests.

======================================================================
25. FINAL STRICT AUDIT
======================================================================

Create:

    research/embrace_strict_parity/FINAL_STRICT_AUDIT.md

Answer, one by one:

1. Can RCM configure every material non-geometry Thing override Embrace
   exposed?

2. Can RCM configure every material scene environment property?

3. Can RCM reuse an original parameterised script without custom Java?

4. Can RCM author the native treasure behaviour exposed by Embrace?

5. Are interestspots materially distinct?

6. Are soundboxes materially distinct?

7. Are lightboxes materially relevant outside baked level construction?

8. Can external template libraries be used without Embrace?

9. Does any useful authoring operation still require raw YAML?

10. Does any useful authoring operation still require custom Java?

11. Does any useful authoring operation still require Embrace?

12. Are any unresolved items only geometry/build-pipeline concerns?

======================================================================
26. DEFINITION OF DONE
======================================================================

The strict closure is DONE only when every MATERIAL non-geometry row is:

    COVERED

or:

    COVERED DIFFERENTLY

or has a rigorous evidence-backed exclusion.

Not:

    “custom Java can do it.”

Not:

    “copy an original profile.”

Not:

    “probably unnecessary.”

Not:

    “we could theoretically edit the binary.”

At that point the report may state:

    “RCM provides complete practical authoring coverage for the
     material non-geometry capabilities of Embrace required to create
     a normal Vampire: The Masquerade — Redemption chronicle.”

This is an AUTHORING claim.

It is NOT automatically a claim that every combination has been runtime
verified.

======================================================================
27. FEATURE CREEP KILL SWITCH
======================================================================

DO NOT implement a capability merely because it appears in the SDK.

For a newly discovered feature to enter RCM it must satisfy ALL:

1. original author-facing capability;
2. non-geometry;
3. meaningful chronicle use;
4. demonstrated engine behaviour;
5. no adequate existing RCM UI equivalent;
6. safe implementation;
7. maintainable architecture.

Otherwise document and stop.

======================================================================
28. FINAL PRODUCT QUESTION
======================================================================

At the end ask only this:

    “Could an author reasonably build the gameplay, story,
     staging, environment, scripting, cinematics and resource setup
     of an original-style Redemption chronicle using RCM alone,
     while reusing existing level geometry?”

If YES:

    STOP.

Do not hunt another API.

Do not make RCM bigger for the sake of bigger.

If NO:

    name the exact remaining author intention
    and the exact evidence proving the gap.

======================================================================
FINAL MANTRA
======================================================================

NO MORE GENEROUS PARITY.

PRESERVING IS NOT AUTHORING.

CUSTOM JAVA IS NOT NORMAL AUTHORING.

RAW YAML IS NOT NORMAL AUTHORING.

A WORKAROUND IS NOT PARITY UNLESS IT PRESERVES THE AUTHOR INTENT.

DO NOT REBUILD EMBRACE'S GEOMETRY EDITOR.

DO REPLACE THE REST OF EMBRACE.

WHEN A NORMAL CHRONICLE AUTHOR CAN DO EVERYTHING MATERIAL
WITHOUT LEAVING RCM:

                         100%.

THEN STOP.
======================================================================