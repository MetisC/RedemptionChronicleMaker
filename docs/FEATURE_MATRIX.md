# Matriz de funciones · versión actual

PASS se refiere al alcance descrito y a evidencia de esa columna. La tabla histórica corresponde a Fase 6; las confirmaciones históricas no se transfieren automáticamente a 0.7.0. PARTIAL/NOT IMPLEMENTED aparecen sin ocultar huecos. Fase 7 añade selector de perfiles de entorno (modelo/GUI/build/roundtrip probados offline, runtime pendiente), catálogo de estáticas y versión de paquete centralizada. Comparación ampliada en [EMBRACE_COMPARISON.md](EMBRACE_COMPARISON.md).

| Feature | Model | GUI | Save/load fuente | Validation | Generator | Build | Deploy | Runtime test | Evidencia/límite |
|---|---|---|---|---|---|---|---|---|---|
| Levels originales | PASS | PASS | PASS | PASS | PASS | PASS | PASS | NOT TESTED | catalogue/core/spatial; históricos aceptados |
| Geometry/mesh read-only | PASS | PASS | NOT APPLICABLE | PASS | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT TESTED | 112 NIL y 1476 NOD históricos; regresión GL actual |
| Actor/posición/orientación | PASS | PASS | PASS | PASS | PASS | PASS | PASS | NOT TESTED | core/spatial/campaign; colisión requiere motor |
| Props/items originales | PASS | PASS | PASS | PASS | PASS | PASS | PASS | NOT TESTED | campaign/format/build |
| Conversaciones/RETURN/GOTO | PASS | PASS | PASS | PASS | PASS | PASS | PASS | NOT TESTED | phase2/campaign_callbacks; fallo nativo previo documentado |
| Grafo diálogo/story | PASS | PARTIAL | NOT APPLICABLE | PASS | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | story_graph derivado; árbol es fuente |
| Flags/condiciones all-any-not | PASS | PASS | PASS | PASS | PASS | PASS | PASS | NOT TESTED | campaign/callback harness |
| Quests/journal/pasos abstractos | PASS | PASS | PASS | PASS | PASS | PASS | PASS | NOT TESTED | campaign/CampaignEngine; límites NQD |
| Inventario/pickup/give/take | PASS | PASS | PASS | PASS | PASS | PASS | PASS | NOT TESTED | campaign harness; identidad persistente |
| Triggers box/sphere yaw | PASS | PASS | PASS | PASS | PASS | PASS | PASS | NOT TESTED | spatial y harness; muestreo 150 ms |
| Eventos/acciones | PASS | PASS | PASS | PASS | PASS | PASS | PASS | NOT TESTED | ACTIONS/WHEN compartidos; Java compilado |
| Encuentros/enemy/death | PASS | PASS | PASS | PASS | PASS | PASS | PASS | NOT TESTED | campaign; combate real pendiente |
| Multi-level/Jump | PASS | PASS | PASS | PASS | PASS | PASS | PASS | NOT TESTED | 2 y 5 mapas compilados; entrada original |
| Cámara/plano temporizado | PASS | PASS | PASS | PASS | PASS | PASS | PASS | NOT TESTED | API CodexCamera real; callback mocks |
| Timeline/XYZ cámara | NOT IMPLEMENTED | NOT IMPLEMENTED | NOT IMPLEMENTED | NOT IMPLEMENTED | NOT IMPLEMENTED | NOT IMPLEMENTED | NOT IMPLEMENTED | NOT TESTED | no botón presentado como terminado |
| Música/ambiente | PASS | PASS | PASS | PASS | PASS | PASS | PASS | NOT TESTED | recursos reales y CodexSound |
| Templates NOT propios | PARTIAL | PARTIAL | PASS | PASS | PARTIAL | PASS | PASS | NOT TESTED | NOT subset/opaque safety; writer experimental |
| AI propia/Nai | PARTIAL | PARTIAL | PASS | PASS | PARTIAL | PASS | PASS | NOT TESTED | AI_FIELDS contrastados; neutral pausa AI |
| Paths/waypoints | NOT IMPLEMENTED | NOT IMPLEMENTED | NOT IMPLEMENTED | NOT IMPLEMENTED | NOT IMPLEMENTED | NOT IMPLEMENTED | NOT IMPLEMENTED | NOT TESTED | fuera de authoring actual |
| Java propio/texturas | PASS | PARTIAL | PASS | PASS | PASS | PASS | PASS | NOT TESTED | resources/integration/gui pendiente Java |
| Rename/referencias | PASS | PASS | PASS | PASS | PASS | PASS | PASS | NOT APPLICABLE | campaign/spatial/phase2 |
| Safe Delete | PASS | PASS | PASS | PASS | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | safe_edit tests; bloquea y conserva fuente |
| Undo/redo/duplicate | PASS | PASS | PASS | PASS | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | GUI-model; history campaña completa |
| Save/SaveAs/autosave/backup | PASS | PASS | PASS | PASS | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | document/phase2/editor |
| Picking/gizmos/snap | PASS | PASS | PASS | PASS | PASS | PASS | PASS | NOT TESTED | math3d/spatial + GL; ground no collision |
| Resource catalogue/cache | PASS | PASS | NOT APPLICABLE | PASS | PASS | PASS | PASS | NOT APPLICABLE | fresh scan/repair; contenidos originales readonly |
| Build validado/determinista | PASS | PASS | PASS | PASS | PASS | PASS | PASS | NOT TESTED | e2e/réplicas/hash Phase2 idéntico |
| Atomic publication/rollback | PASS | PASS | NOT APPLICABLE | PASS | PASS | PASS | PASS | NOT APPLICABLE | fault injection; manifest último, sin aislamiento total |
| Clean owned artifacts | PASS | NOT IMPLEMENTED | NOT APPLICABLE | PASS | NOT APPLICABLE | PASS | NOT APPLICABLE | NOT APPLICABLE | CLI clean; no borra archivos ajenos |
| Deploy/Install/Uninstall RCM | PASS | PASS | PASS | PASS | PASS | PASS | PASS | NOT TESTED | fake game tests; native deployment evidencia separada |
| Project export/import | PASS | PASS | PASS | PASS | PASS | PASS | NOT APPLICABLE | NOT APPLICABLE | e2e byte-identical distribution + GUI roundtrip |
| Package manifest/deps/trust | PARTIAL | PASS | PASS | PASS | PASS | PASS | PASS | NOT TESTED | version local; sin assets compartidos ni firma |
| Playtest/logs/source map | PARTIAL | PARTIAL | PASS | PASS | PASS | PASS | PASS | NOT TESTED | trace parser; observaciones, no inspector vivo |
| First run/settings/safe mode | PASS | PARTIAL | PASS | PASS | NOT APPLICABLE | PASS | NOT APPLICABLE | NOT APPLICABLE | startup + portable smoke separado |
| Portable executable | PASS | PASS | NOT APPLICABLE | PASS | PASS | PASS | NOT APPLICABLE | NOT TESTED | local build/probe; máquina limpia pendiente |
| Save/restore nativo | PASS | NOT APPLICABLE | PASS | PASS | PASS | PASS | PASS | NOT TESTED | firma capture real; engine todavía B2 |
| Puertas/entradas arbitrarias | NOT IMPLEMENTED | NOT IMPLEMENTED | NOT IMPLEMENTED | NOT IMPLEMENTED | NOT IMPLEMENTED | NOT IMPLEMENTED | NOT IMPLEMENTED | NOT TESTED | geometría no se edita; API parcial |
| Multiplayer replication | PARTIAL | NOT APPLICABLE | NOT APPLICABLE | PARTIAL | PARTIAL | PASS | PASS | NOT TESTED | NetIsClient no prueba sincronización |
| Cancel build | NOT IMPLEMENTED | NOT IMPLEMENTED | NOT APPLICABLE | NOT APPLICABLE | NOT APPLICABLE | NOT IMPLEMENTED | NOT APPLICABLE | NOT APPLICABLE | cierre/cambios bloqueados mientras compila |
# Actualización de Fase 9

El estado de 0.9.0 se detalla en [AUTHORING_MATURITY_REPORT.md](AUTHORING_MATURITY_REPORT.md) y [AURORA_PARITY_CHECKLIST.md](AURORA_PARITY_CHECKLIST.md). Entradas, waypoints, recorridos, destinos de viaje, presets de cámara, sonido situado y checkpoints por acción ya tienen implementación y validación offline; las pruebas nativas quedan pendientes. Las filas históricas siguientes no acreditan aceptación de estas ampliaciones.

