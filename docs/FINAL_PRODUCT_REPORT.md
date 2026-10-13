# Cierre de producto · 1.0.0-rc2

No se declara 1.0 final. Los ensayos offline, compilación y pruebas nativas se mantienen separados. La nueva distribución requiere los casos manuales indicados.

| AREA | STATUS | EVIDENCE | MANUAL TEST NEEDED |
|---|---|---|---|
| First Run | IMPLEMENTED / OFFLINE VERIFIED | first-run widgets and fresh-profile probe | Fresh real first run |
| Game Detection | IMPLEMENTED / OFFLINE VERIFIED | bounded registry detection; complete executable/archive checks | Select installed game |
| Workspace | IMPLEMENTED / OFFLINE VERIFIED | standard Documents default; validated writable path; preserved legacy workspace | Select/change folder |
| Welcome | IMPLEMENTED / OFFLINE VERIFIED | Qt welcome, tutorial/showcase/new/recent actions | Windows visual review |
| New Chronicle | IMPLEMENTED / OFFLINE VERIFIED | name-derived ID, selected scenario, advanced ID/folder, initial saved draft | Create first project |
| Save/Recovery | IMPLEMENTED / OFFLINE VERIFIED | atomic saves, external-change guard, timestamped recovery choices, locks | Recover an autosave |
| Backup | IMPLEMENTED / OFFLINE VERIFIED | 20 changed source versions; confirmed restore and independent copy | Optional visual review |
| Viewport | IMPLEMENTED / HISTORICAL ACCEPTANCE | existing renderer/navigation preserved; safe-mode settings | Real GPU / scaling |
| Authoring | IMPLEMENTED / OFFLINE VERIFIED | 10 existing assistants plus packaged widget circuit | Human edit/play iteration |
| Conversation | COMPILED / TESTED WITH DOUBLES; tutorial accepted | unchanged tutorial classes; current gallery source/compilation | New gallery framing |
| Quest | COMPILED / TESTED WITH DOUBLES; tutorial accepted | tutorial acceptance; showcase journal/quest entities | Showcase completion/save/load |
| Inventory | COMPILED / OFFLINE VERIFIED; tutorial accepted | carried-template compatibility, own hashes, preserved profiles | LAN with carried item; showcase |
| Triggers | COMPILED / TESTED WITH DOUBLES; tutorial accepted | conditioned barrel circuit preserved; showcase enter/leave | New showcase placement |
| Paths | COMPILED / TESTED WITH DOUBLES | ordered loop/patrol using existing runtime | Pathfinding/collision |
| Cinematics | COMPILED / TESTED WITH DOUBLES; tutorial accepted | Player film unchanged; optional NPC film in Showcase | NPC film/movement |
| Audio | COMPILED / TESTED WITH DOUBLES | music/ambient/spatial one-shot examples | Listen to Showcase |
| Resources | IMPLEMENTED / OFFLINE VERIFIED | catalogue filters, recent/favourites, actual motion slots | Visual selection |
| Graph | IMPLEMENTED / OFFLINE VERIFIED | existing graph/navigation, current Showcase | Large graph / scaling |
| Search | IMPLEMENTED / OFFLINE VERIFIED | existing global search / references retained | Optional human review |
| Build | COMPILED / OFFLINE VERIFIED | 3 real Codex 45.3 builds and fingerprint checks | Edit then playtest |
| Deploy | IMPLEMENTED / OFFLINE VERIFIED | per-chronicle folders, manifests, rollback, compatibility | Real folder/permissions |
| Playtest | IMPLEMENTED / OFFLINE VERIFIED | F5 pipeline, current-build/deploy skip, direct args/cwd | Direct launching |
| Debug | IMPLEMENTED / OFFLINE VERIFIED | session PID/exit/trace refresh and existing navigation | Finish actual game session |
| Packages | IMPLEMENTED / OFFLINE VERIFIED | existing inspect/export/install/uninstall; compatibility added | Install/play with carried item |
| Showcase | SOURCE VALIDATED / COMPILED | generated capabilities matrix, all entity links exercised | All Showcase stations |
| Tutorial | RUNTIME VERIFIED (accepted story scope) | native_acceptance.json; source/classes identical | New launch folder + save/load edges |
| Portable | BUILT; FRESH PROFILE SIMULATION | bundled JVM, curated docs, no originals | Independent machine |
| i18n | IMPLEMENTED / OFFLINE VERIFIED | all literal editor tr keys covered; English/Spanish probes | Human wording |
| DPI | OFFSCREEN SIMULATION / MANUAL REQUIRED | 1100×720 font-loaded Qt captures | 100/125/150/200% Windows |
| Clean machine | MANUAL REQUIRED | same-machine reduced-PATH simulation only | Independent PC/VM |
| Runtime native | HISTORICAL TUTORIAL ACCEPTANCE; NEW FLOW REQUIRED | user's 2026-10-13 acceptance retained | New setup/playtest/showcase circuit |

La matriz completa está en SHOWCASE_MATRIX.md. El tutorial fuente y sus clases se compararon byte a byte con rc1. El juego no se ha automatizado ni se ha abierto durante esta revisión; los despliegues de los probes son sintéticos.

Se mantienen limitados o pendientes: exportación arbitraria de cámara desde viewport, geometría, puertas universales, eliminación universal de estática, audio espacial persistente avanzado y red. No se inventa paridad con Embrace. P2 opcionales (instalador, temas elegibles, preview de recursos y Ctrl+P) no forman parte de esta candidata. P1 secundarios todavía parciales: oferta de acceso en Escritorio, seguimiento de trace durante toda la partida, comparador de versiones de ejemplos y adopción de patrones manuales como asistentes.
