# Auditoría de huecos reales de autoría

## Actualización de implementación · 0.9.0

El usuario ha aplazado las pruebas nativas y autorizado continuar. Se conserva debajo la auditoría **inicial**, sin reescribirla como si ya hubiera conocido las mejoras. La observación humana limitada de 0.7.0 confirma tres NPC/conversaciones/viaje con enemigos, no el build 0.9.0 ni save/load exhaustivo.

| Apartados | Estado actualizado | Cambio / evidencia |
|---|---|---|
| 4–7 | PARTIAL / RUNTIME VERIFICATION REQUIRED | Auto cámara de diálogo y Release al restaurar; checkpoints de acciones, progreso y retry; harness de fallo parcial conserva XP/item/posición |
| 8–9,12 | PARTIAL / RUNTIME VERIFICATION REQUIRED | Entradas lógicas nombradas, default, colocación real, yaw y selectores escena/entrada; no cambia portales nativos |
| 10–11 | PARTIAL / RUNTIME VERIFICATION REQUIRED | IsExitValid/OpenExit/CloseExit y frames/pivote de puerta existente; no cerraduras ni override de su script |
| 13–15,26 | PARTIAL / OPEN | Inspector aclara carga static; ALL/NONE/SELECTIVE aún OPEN |
| 16–18 | PARTIAL / RUNTIME VERIFICATION REQUIRED | Waypoints por clic, orden/loop/actor, overlay, SendActorToPos y guardado de progreso; sin navmesh |
| 19–20 | PARTIAL / RUNTIME VERIFICATION REQUIRED | Presets legibles de escalares NAI y roles existentes; no AI completa |
| 21–22 | PARTIAL / RUNTIME VERIFICATION REQUIRED | Sonido one-shot situado con volumen/radios; música/ambient/perfil existentes; loop espacial persistente OPEN |
| 23–25 | PARTIAL / OPEN | Siete presets SDK y auto cámara; NCP desde vista/presentación avanzada por línea OPEN |
| 27–31 | PARTIAL / RUNTIME VERIFICATION REQUIRED | Actor/item propios en circuito; portable reconstruido y prueba local en workspace nuevo; máquina independiente OPEN |
| 32 | PARTIAL | Inspección de Code/method/pool real, 45.3 y compilación por escena; partición automática general de evento gigante OPEN |
| 33–37 | RESOLVED en subconjunto offline / RUNTIME VERIFICATION REQUIRED | Deploy con ownership y obsoletos, backup/rollback; ACTION/diálogo/quest a fuente, SAVE/RESTORE/RESTORED |
| 38–40,53–54 | PARTIAL / RUNTIME VERIFICATION REQUIRED | Un solo circuito, 3 áreas/6 NPC/4 enemigos/2 quests/rama/2 recorridos; no puerta ficticia ni PASS de principio a final |
| 43–46,58 | RESOLVED como auditoría | Checklist Aurora, madurez por apartado, firmas y SDK contrastados; estados separados de runtime |
| 48–52,56–57 | PARTIAL | Campaña directa, vocabulario escenas/geometrías, proyecto básico GUI con clic real→save→reopen→build; aventura completa GUI/humano pendiente |

Los apartados sin actualización conservan el estado inicial; no se declaran cerrados por número de fase. Suite ampliada: **198 tests, 0 fallos/errores/skips**, quality PASS. `research/phase9/full_tests.*` conserva ese resultado; pruebas posteriores focalizadas se registran separadamente. Golden y Fase 2 mantienen hashes fijados. OpenGL real y autoría básica documentados en `research/phase9/gui/probe.json`. Circuito completo fuente curada, no presentado como autoría GUI exhaustiva. [Madurez](AUTHORING_MATURITY_REPORT.md), [paridad](AURORA_PARITY_CHECKLIST.md), [matriz manual](RUNTIME_TEST_MATRIX.md).

## Auditoría inicial conservada

Auditoría inicial, 2026-10-08, antes de cambios de código de Fase 9. Encargo conservado íntegro en [AUTHORING_AUDIT_REQUIREMENTS.md](AUTHORING_AUDIT_REQUIREMENTS.md). Complementa [PHASE9_PLAN.md](PHASE9_PLAN.md).

## Alcance y evidencia inicial

Leídos informes disponibles de Fases 1–7, matriz de capacidades, huecos, problemas, bloqueos, pruebas runtime, notas de motor y formatos; contrastados módulos de modelo, generación, documento, GUI, formatos, recursos, depuración y despliegue. No hay informe de cierre de Fase 8.

Antes de modificar código: **188 tests, 0 fallos, 0 errores, 0 skips**, 160,47 s. Evidencia preservada en `research/phase9/baseline_tests.json` y `.log`. La suite construye Golden y verifica su SHA fijado, ejecuta harnesses System/Campaign con doubles, compila contra Codex y prueba GUI/modelo. System Test se ha construido adicionalmente por CLI: cinco clases 45.3, estado `compiled-unverified-in-game`. No se han cambiado las expectativas históricas para aceptar una salida distinta. Los 43 originales registrados mantienen sus hashes.

Redemption se ha abierto mediante doble clic sobre el acceso exacto del escritorio desde Explorer: intro y menú 1.1 observados, sin CD-key. El clic automatizado sobre Multiplayer no activó el menú. Se solicita ayuda para iniciar la partida; ningún caso de la campaña se marca aceptado por ese arranque.

Estados: **RESOLVED** = preocupación cubierta dentro del alcance/evidencia indicado; **PARTIAL** = capacidad existente incompleta; **OPEN** = falta; **RUNTIME VERIFICATION REQUIRED** = generación/compilación no acreditan motor; **NOT RELEVANT ANYMORE** = preocupación histórica superada. Se pueden combinar estados para distinguir autoría de aceptación nativa. No clasificar un hueco de RCM como imposibilidad del motor sin prueba.

## Contraste de los 59 apartados externos

| Nº | Preocupación | Estado inicial | Evidencia / decisión |
|---|---|---|---|
| 1 | Auditoría previa | RESOLVED | Baseline y documentos contrastados; este informe conserva resultados antes de editar código |
| 2 | Generated / compiled / runtime | RESOLVED / PARTIAL | Build usa `compiled-unverified-in-game`; matrices separan runtime, hay textos históricos de formatos por corregir |
| 3 | Suite runtime | PARTIAL / RUNTIME VERIFICATION REQUIRED | Checklist existente; observaciones históricas no aceptan 0.7.0 |
| 4 | Diálogo/cámara/UI | RUNTIME VERIFICATION REQUIRED | RCM-601, corrección offline; B1 abierto |
| 5 | Persistencia | RUNTIME VERIFICATION REQUIRED | Callbacks `(int)` y doubles; B2 abierto |
| 6 | Idempotencia | PARTIAL / RUNTIME VERIFICATION REQUIRED | Guards de flags, GUIDs y recompensas; reentrada nativa sin ensayar |
| 7 | Reentrada | RUNTIME VERIFICATION REQUIRED | Tres escenas de Fase 7; no hay recorrido actual observado |
| 8 | Entradas/runtime | OPEN | `Jump(alias,0)` y entradas originales; API de teletransporte existe, tablas/arrivals propios sin soporte |
| 9 | Entradas visuales | OPEN | Viewport admite transforms de otras entidades; no entries propias |
| 10 | Puertas/exits | OPEN | API OpenExit/CloseExit/ChangeExit contrastada; no equivale a puerta móvil |
| 11 | Autoría de puertas | OPEN | Door/PivotDoor requieren inspección de scripts/frames/parámetros; no añadir propiedades supuestas |
| 12 | Transiciones humanas | PARTIAL | Selector de escena en acciones; sin destino de llegada elegido |
| 13 | Estática/geometry only | PARTIAL | SDK confirma NSD static automático del mismo nombre NIL; codec complejo parcial |
| 14 | ALL/NONE/SELECTIVE | OPEN | No opción ficticia; investigar override y referencias antes de exponer |
| 15 | Geometría/decoración | PARTIAL | NIL read-only y hints de entidad originales; hints no son parser completo |
| 16 | Paths/waypoints | OPEN | No modelo ni GUI; revisar API y scripts originales |
| 17 | UX de paths | OPEN | Depende de traducción fiable; no navmesh nuevo |
| 18 | Movimiento scriptado | OPEN | No biblioteca normal de acciones de movimiento; verificar contratos reales |
| 19 | Presets AI | PARTIAL | NPC pasivo y enemigo, pause/enable; no todos los presets propuestos |
| 20 | NAI avanzado | PARTIAL / RUNTIME VERIFICATION REQUIRED | Sólo escalares conocidos; líneas desconocidas conservadas |
| 21 | Audio espacial | OPEN | CodexSound expone posiciones; no autoría/modelo probado |
| 22 | Environment | PARTIAL | Perfiles originales y música/ambient; no editar campos opacos ni lightmaps |
| 23 | Presets cámara | PARTIAL / RUNTIME VERIFICATION REQUIRED | Secuencias actor/shot/angle; auto diálogo usa SetupCutscene; encuadre por comprobar |
| 24 | Cámara desde vista | OPEN | Viewport libre no implica equivalencia de FOV/cámara del motor |
| 25 | Presentación conversación | PARTIAL / RUNTIME VERIFICATION REQUIRED | Speaker/texto y cámara automática; sin presentación avanzada por línea |
| 26 | Inspector original | PARTIAL | Hints readonly con template/offset/confianza; sin override fiable |
| 27 | NOT propio en motor | RUNTIME VERIFICATION REQUIRED | Writer restringido y fixtures; B3 abierto |
| 28 | Seguridad NOT | RESOLVED en subconjunto | Validación/readback/opaque preservation/rutas; writer sigue experimental |
| 29 | Máquina limpia | OPEN | Portable local probado; equipo/VM independiente pendiente B4 |
| 30 | SDK/toolchain | NOT RELEVANT ANYMORE para herramientas antiguas | ECJ/JVM modernos; classes.zip/Codex originales son bibliotecas leídas del juego; avisos conservados |
| 31 | Bytecode 45.x | RESOLVED | Compiler y `output_validation` inspeccionan cabecera exacta 45.3; tests existentes |
| 32 | Límites Java grandes | PARTIAL | Fixture 5 mapas/100 actores/100 eventos compila; aún no barrido de límites de métodos/pool |
| 33 | Build/deploy repetidos | PARTIAL | Tests de determinismo/actualización/rollback; bucle nativo completo pendiente |
| 34 | Deploy ownership | RESOLVED en archivos propios | Manifest, preflight, backups y rollback; conserva archivos ajenos; tests de fallos |
| 35 | Trace útil | PARTIAL | SCENE/ACTION/WATCH/conversation/spawn; faltan observaciones explícitas de save/restore |
| 36 | Trace→fuente | PARTIAL | Source map Java y escena/evento; parser no recupera todo contexto de ACTION |
| 37 | Trace persistencia | OPEN | Save/restore no tienen registros propios explícitos de fases |
| 38 | Estaciones System Test | PARTIAL | NPC/quest/inventario/cámara/audio/encuentros; no estaciones de features ausentes |
| 39 | Golden aventura | PARTIAL | Golden fija regresión de dos mapas; nueva aventura debe mantenerse separada de baseline |
| 40 | Matriz manual | PARTIAL | Checklist existente; añadir cases de entries/doors/path con estados honestos |
| 41 | Prioridades | RESOLVED como orden de trabajo | P0 nativo; P1 entries/doors/static/paths/portable; P2 audio/environment/camera/AI; P3 red |
| 42 | Red no bloquea beta local | RESOLVED como alcance solicitado | Conservar B5 y separar beta local de aceptación de red; actualizar gate explícitamente |
| 43 | Checklist Aurora | OPEN | Crear tabla de experiencia real con YES/PARTIAL/NO y alcance |
| 44 | RCM vs motor | PARTIAL | Muchas ausencias son de RCM; evitar inferir imposibilidad nativa |
| 45 | Auditoría Codex útil | PARTIAL | Firmas/scripts estudiados; revisar entradas/puertas/movimiento/audio enfocados a aventuras |
| 46 | Capability→editor | PARTIAL | FEATURE_MATRIX existente; ampliar GUI/contrato/evidencia para nuevos huecos |
| 47 | Evitar feature bingo | RESOLVED como criterio | Añadir sólo capacidades que resuelvan recorridos concretos |
| 48 | UX completa | PARTIAL | Nuevo proyecto schema1 requiere conversión; escenas llamadas mapas; editor aún no aceptado por usuario |
| 49 | YAML opcional | PARTIAL | Qt authoring de demos ya existe; experiencia completa nueva por demostrar |
| 50 | Advanced | PARTIAL | Java y NOT técnico accesibles; revisar separación del flujo habitual |
| 51 | Usuario sin SDK | OPEN | Ensayo conceptual y aceptación humana faltan; tests Qt no miden comodidad |
| 52 | Documentación humana | PARTIAL | Guía existente; requiere recorrido de Fase 9 desde vacío |
| 53 | Aventura 3 áreas completa | OPEN | Fase 7 tiene 3 escenas/2 geometrías; no toda la aventura externa |
| 54 | Jugar principio→final | OPEN / RUNTIME VERIFICATION REQUIRED | No hay partida actual completa, save/exit/load/finish observado |
| 55 | Geometría fuera | RESOLVED | Ningún writer NIL; nuevos paquetes no incluyen geometría |
| 56 | Reemplazar workflow | PARTIAL | Toolchain propio; authoring faltante entries/doors/paths; no declarar paridad completa |
| 57 | Author/build/play/save/load/iterate | PARTIAL | Cadena offline probada; recorrido humano/runtime pendiente |
| 58 | Informes | PARTIAL | Este audit inicial; checklist y maturity report se crearán durante la ejecución |
| 59 | Comprobar→corregir→verificar | RESOLVED como proceso | Baseline previo; evitar reescribir lo ya aceptado en su alcance |

## Orden de ejecución

P0: aceptación real de diálogo, persistencia, reentrada e identidad de templates. Mientras se espera acceso a partida, investigación y mejoras independientes de autoría/diagnóstico pueden continuar, sin declarar corregido el comportamiento nativo pendiente.

P1: crear campañas directamente; clarificar escena/base; entradas y llegadas con evidencia; controlar exits y estudiar puertas existentes; clasificar static; estudiar paths útiles; ensayar distribución independiente. P2: mejoras narrativas de cámara/AI/audio sólo respaldadas. P3: red.

El encargo eleva la aventura final a tres áreas, seis NPC, cuatro enemigos, dos quests con una rama, item/recompensa/encounter/secuencia/música/ambient/triggers/final. Entradas/puerta y patrullas se incorporarán sólo en el alcance que se demuestre; si falta una capacidad mínima se registra como hueco y no se afirma satisfecha la aventura completa.
