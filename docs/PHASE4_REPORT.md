# Fase 4 — autoría de campañas, versión 0.4.0

Entrega del 8 de octubre de 2026. El núcleo prioritario está implementado, compilado y desplegado para ensayo nativo. **No se ha ejecutado una partida de esta campaña en Redemption.** La validación automática no permite dar por aceptados journal, viajes, combate o persistencia nativos.

## IMPLEMENTADO

Campañas con varias ubicaciones, quests de pasos, inventarios, encuentros, condiciones compuestas, acciones narrativas, viajes, planos de actor, música/ambiente y despliegue. Todo utiliza el mismo proyecto, editor espacial, catálogos, validación y codecs de las fases anteriores. No se ha usado ninguna herramienta original de autoría ni modificado geometría.

Demo creada mediante controles reales de la GUI, sin escribir su YAML manualmente: `chronicles/phase4_demo/project.yaml`, **RCM: El libro de Londres**. EastLondon y WestLondon; cuatro NPC, tres enemigos, libro de inventario, quest de tres pasos, trigger espacial, encuentro, conversaciones con consecuencias de flag, música, plano de llegada y recompensa de 500 XP. El encuentro tiene otra recompensa de 100 XP.

El generador produce NSC, NMF, NSD, NOT mínimos, NCO, NVO, NLS, NQD, WAV de soporte y Java compilado a **45.3** contra Codex original. Un NOB agrupa los recursos; cuatro clases quedan en `codex/`. La geometría no se incluye ni altera. Demo: `build/phase4_demo/phase4_demo_distribution.zip`.

## QUEST SYSTEM

Editor de ID, título, descripción, pasos y XP. Iniciar, avanzar y completar; condiciones de estado y paso activo; respuestas conectadas mediante RETURN/evento de fin. Generación directa de NQD/NLS y llamadas reales `CodexQuest.Load`/`Complete`.

Resumen y pasos son entradas distintas del journal nativo. No hay gramática inventada de objetivos internos en un NQD. Máximo de 64 entradas contando pasos/resúmenes; icono QuestCheck fijo. Progreso y acciones únicas usan Chronicle Flags reservados, separados de 0–255 del autor. Detalles: [QUESTS.md](QUESTS.md).

## ITEM SYSTEM

Objetos de inventario de familias items/weapons/armour; props separados. Colocación espacial o junto al jugador, inventario inicial de actor, dar/quitar al jugador y condición Tiene objeto. Entrega puede referenciar un objeto de otro mapa por ID cualificado; el autor no introduce GUID. Renombres actualizan estas referencias.

Quest Item clasifica el objeto, sin inmunidad artificial a vender/soltar. Pickup se deriva del inventario observado cada 0,15 s. Búsqueda acotada a 4096 enlaces. No hay slots/equipo/belt nuevos. [ITEMS.md](ITEMS.md).

## ENCOUNTERS

Grupos de enemigos declarados en la escena, creación y retirada desde eventos. Validación de integrantes, tipo enemigo y único propietario de creación. Encounter Complete deriva de la salud de todos los actores ya creados, mientras sus GUIDs sigan siendo válidos. Invalidar un GUID no se equipara a matarlo.

## TRANSITIONS

Ubicaciones propias en NSC que referencian NIL original y NSD propio. Escena de entrada seleccionable; viaje a otro alias mediante `CodexSequence.Jump(alias, 0)`. Viajar libera cámara, detiene el controlador anterior y debe ser la última acción del evento. Varias ubicaciones pueden reutilizar la misma geometría.

No se reescriben puertas, exits ni tablas geométricas. La entrada 0, punto de aparición y conservación de inventario/estado entre ubicaciones requieren ensayo nativo. La demo coloca personajes y libro junto al jugador para facilitarlo.

## CAMERAS / SEQUENCES

Planos de actor con duración, ShotType medio/cercano/amplio y ShotAngle bajo/medio/alto. SetupCutscene y Release reales; liberación por timer, conversación o viaje. Diálogos usan ángulo medio. Enfocar en viewport es una ayuda de ubicación, no una simulación del encuadre del juego.

Sin XYZ/FOV arbitrarios, paths ni timeline multi-shot: esos contratos no están acreditados. [SEQUENCES.md](SEQUENCES.md).

## AUDIO

Selección de recursos originales de música y StereoAmbient; Start/Stop Music y Start/Stop Ambient, volumen actual 100. Referencias validadas contra catálogo y compiladas a funciones reales. No se ofrecen preview, sonidos 3D, voz grabada ni mezcla avanzada. Los WAV de conversación siguen siendo silencio de soporte para mostrar texto.

## AI

NPC neutral con AI pausada; enemigo TEAM_ENEMY0 con pausa/neutral desactivados; Enable/Disable AI. Se heredan perfiles originales por NOT, sin fabricar un motor AI. Inspección de 136 NAI y de su uso por plantillas. Los hijos utilizan script Passive propio; algunas plantillas pueden necesitar lógica original adicional.

Sin autoría NAI, patrullas, follow/guard, waypoints, disciplinas o selector de perfiles aplicables no verificados. [AI.md](AI.md).

## EVENTS / CONDITIONS / ACTIONS

Editor de eventos existente ampliado: inicio, clic, fin de conversación, entrada/salida de trigger, muerte, pickup, encuentro completo, timer y cambio de estado. Muerte/pickup/encuentro/estado son eventos derivados de muestreo, identificados como tales.

Condiciones AND de lista y grupos ALL/ANY/NOT, flags, estado/paso de quest, actor vivo, entidad existente e inventario. Biblioteca de acciones compartida por GUI, validador y generador: mundo, conversación, flags, quests, inventario/XP, encuentros, viajes, audio, cámara y AI. Referencias inválidas y acciones sin contrato bloquean build.

Los eventos derivados y timers son únicos por defecto; Cada vez habilita nuevos flancos, o periodicidad en timers. Trigger Enter respeta también la opción única del volumen. Los tiempos avanzan en ticks de muestreo y pueden retrasarse durante diálogos. Guardado usa funciones reales Save/RestoreInt/Boolean; no hay almacenamiento RPG alternativo.

## RESOURCE BROWSER

Conserva catálogo original y colocación 3D. Añade inspección de propiedades/bytes/offsets NOT y texto NAI. Búsqueda global de campaña con Ctrl+Shift+F y navegación a escenas/entidades/quests; Find References incluye vínculos entre mapas. Cache de geometría independiente de cambios narrativos.

No se ha añadido un sistema público de prefabs ni un grafo general de campaña editable. Se priorizan las referencias reales y el pipeline completo del núcleo.

## .NOT RESEARCH

Global: 915 templates; modernDay: 776; darkAges: 726; Multiplayer: 202. Lectura y recodificación exacta de las cuatro bibliotecas, preservando tags y bytes desconocidos. Multiplayer conserva una cola opaca de 6786 bytes. Inspector muestra herencia y propiedades tipadas solo donde existe evidencia.

Writer de hijos mínimos anterior: parent/script/Cast ID/Description ID. No hay writer completo ni reinterpretación de campos desconocidos. Evidencia: `research/phase4/not_comparison.json`, [NOT_FORMAT.md](NOT_FORMAT.md).

## DEPLOYMENT

Build permanece en workspace. Deploy explícito verifica estado compilado y hashes, respalda destinos y escribe exclusivamente dentro de RCM, rechazando escapes/enlaces/hardlinks. La GUI comprueba que el documento coincida con la fuente compilada. Ejecutar abre Vampire con `-user RCM\<ID>`, trabajando desde la raíz del juego; no maneja sus menús. Ruta de instalación configurable; CLI conservado.

La demo está en **RCM/phase4_demo** y también en **RCM/east_demo**, compatible con el acceso directo habitual. Auditoría: `research/phase4/deployment_audit.json`; originales verificados antes/después y pruebas anteriores preservadas. Sustitución atómica por archivo, sin transacción atómica de toda la carpeta ni migración de partidas. [DEPLOYMENT.md](DEPLOYMENT.md).

## PROBADO AUTOMÁTICAMENTE

- 111 tests, cero errores/fallos: `build/tests/test_report.json` y `tests.log`.
- 12 escenarios del Java generado con doubles: spawns, diálogo, pasos, pickup, ausencia de duplicados, restore de GUID, flags, aborto, recompensa única, viaje y protección de cliente. `build/tests/campaign_java/harness.log`. No son una simulación completa del motor.
- Todas las acciones compilan contra Codex original; incluyen transforms/cajas con coordenadas y yaw negativos, referencias de inventario entre escenas y cámara/audio/AI. Clases finales 45.3.
- Aceptación GUI: ocho comprobaciones, demo creada con controles, colocación mediante raycast, integridad sin warnings, build desde GUI. `build/campaign/acceptance/report.json` y `campaign.png`.
- Cinco proyectos abiertos con OpenGL real y recompilados sin modificar sus fuentes: `research/phase4/final_regression.json`. EastLondon tiene 45927 triángulos y 109 materiales. Distribución de aceptación Fase 2 conserva SHA-256 `90b41cb0b203510fafadde9f08bef5afe484aaefcb2cc8aaafbc636b88ca86ab`.
- Roundtrip NOT, validación de estructuras corruptas/referencias, undo/recovery/backup de campaña completa, campos no confirmados, guard de deploy antiguo y límites de journal/flags.
- CLI Validate/Build y manifests. Deploy de demo auditado; 43 fuentes originales conservan hashes.

Integridad del proyecto: cero avisos. Compilador: cero errores, dos warnings en london y cuatro en west. Se revisaron: PrintStream marcado deprecated por la biblioteca histórica y helpers compartidos no utilizados en esas escenas (give/volume y vector sin triggers). No son métodos inventados ni errores omitidos; los logs completos están en `build/phase4_demo_s0/compiler.log` y `build/phase4_demo_s1/compiler.log`.

Checkpoint inicial: `research/checkpoints/phase3_before_phase4.zip`. Baseline previo: 84 tests y aceptación espacial histórica. La fuente Fase 3 fue restaurada desde checkpoint tras esa prueba que la reautoraba; la regresión final solo abre/recompila, sin reescribir fuentes.

## PROBADO DENTRO DE REDEMPTION

**Nada nuevo de Fase 4.** Se conserva la aceptación histórica del usuario de Fases 1/2: mapa, NPC próximo, conversaciones y decisiones recordadas. No prueba la nueva campaña. No se ha generado un log nativo falso ni equiparado compilación o doubles a ejecución real.

## NO PROBADO

Journal, recogida/entrega/traslado de libro, entradas y regreso entre ubicaciones, supervivencia de entidades tras viajes, combate y ciclo de cadáveres, audio/cámara/liberación, recompensa nativa, save/load del controlador y replicación de red. Control nativo de la aplicación no está disponible en este entorno para completar una partida.

Ensayo propuesto: partida nueva → Victoria → ¿Quién eres? → Cuenta conmigo → volver a hablar → Vamos al oeste de Londres → recoger libro → Contact/Continuar → Victoria/Seguimos juntos. Comprobar journal en cada paso, 500 XP y que entregar de nuevo no repita recompensa. Matar los tres enemigos y comprobar 100 XP/música. Probar guardar/cargar antes y después del viaje por separado. Conservar `RCM/phase4_demo/runtime_trace.log`; [EDITOR_GUIDE.md](EDITOR_GUIDE.md) detalla el recorrido.

## BUGS CONOCIDOS

No se conoce un fallo pendiente que haga fallar la suite local. Esto no acredita ausencia de bugs nativos. El muestreo puede perder una muerte si el cadáver/GUID desaparece antes de observar salud ≤0: en ese caso no se dispara Encounter Complete. Pickup/transiciones rápidas también pueden perderse. Se documentan como limitaciones, sin callbacks nativos inventados.

## LIMITACIONES

- Cada entidad tiene una creación propia por ciclo de controlador; retirar no habilita respawn de la misma identidad. Encounters no tienen oleadas repetibles.
- Pickup e inventario de jugador usan el jugador seleccionado local por el controlador; triggers agregan entrada de jugadores de la ubicación. No se promete multiplayer completo.
- Flags/namespaces se asignan según el orden de autoría. Reordenar escenas/quests/eventos puede invalidar saves anteriores. Sin migración ni reconciliación de versiones publicadas.
- Acciones de un evento se ejecutan en orden; no hay rollback de efectos anteriores si una acción posterior falla. Errores no consumen el marcador único, pero muestreo por flanco no garantiza reintento automático.
- XYZ editado no acredita collision/navmesh; entry 0, placement near_player y AI deben comprobarse por mapa/plantilla.
- Sin geometría nueva, exits físicos, paths, writer completo NOT/NSD, timeline, audio avanzado ni RPG/quest engine ajeno al juego.

## DEUDA TÉCNICA

Ensayos nativos y pruebas de persistencia antes de ampliar contratos; estabilizar asignación/migración de flags, versiones de campaña y save/load; investigar NQD con objetivos internos, NSD de entradas y ciclo de cadáveres. Ampliar pruebas GUI de referencias/borrado/duplicación y presentación de contexto global en propiedades. Medir rendimiento en campañas mayores antes de optimizar.

## CAMBIOS DE ARQUITECTURA

Schema 2 y CampaignDocument con raíz única y vista activa por referencias; snapshots/undo/save abarcan todos los mapas. Parseo de campaña reutiliza contratos anteriores de recursos/transforms/conversación. Generador agrega escenas mediante fábrica opcional de Java, conservando salida schema 1. ACTIONS compartida; grafo global derivado; source_map conserva contexto escena/evento/acción para diagnósticos. Fingerprint del fuente evita desplegar desde GUI un build anterior a las ediciones. Deployment mantiene separado el permiso excepcional RCM del guard de escritura de Workspace.

## PROPUESTA PARA FASE 5

**No iniciada.** Primero cerrar la aceptación nativa de esta aventura y resolver lo que revele. Después, si se autoriza otra fase: versiones/migración de campañas y partidas, quests con objetivos internos si se confirma el formato, entradas/exits/paths contrastados, secuencias más completas y automatización de pruebas apropiada. Mantener la geometría original inmutable y ninguna herramienta original de autoría en el workflow.
