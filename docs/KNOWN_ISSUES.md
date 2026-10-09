# Problemas conocidos · Fase 6

## Revisión de Fase 7

- RCM-701, corregido offline: el scanner interpretaba NSS como asociación location/NSD. Ahora usa NSC y la pareja estática documentada; no genera nombres desde claves de descripción.
- RCM-702, corregido offline: entorno elegido implícitamente sin opción de autoría. Nuevo selector por escena, validación de asociación/hash, roundtrip y undo. Fog/EAX/ZClip individuales siguen pendientes.
- RCM-703, corregido offline: diagnósticos y paquetes fijaban una versión distinta de la aplicación. Ahora consultan `rcm.__version__`.
- RCM-704, límite visible: 1 referencia NSD inicial no existe en el catálogo original. Se muestra no disponible; no se convierte silenciosamente en un perfil vacío.
- RCM-705, pendiente: ampliar asociaciones de NSD desde scripts, entradas numeradas, static base, paths, luces y audio espacial. [Comparación](EMBRACE_COMPARISON.md).

B1–B5 continúan abiertos; las correcciones offline no resuelven por sí solas la aceptación nativa comunicada por el usuario.

| ID | Severidad | Reproducción / estado | Evidencia / regresión |
|---|---|---|---|
| RCM-601 | CRITICAL, verificación pendiente | Fase 5: rechazar la primera conversación dejó cursor/UI ausentes y cámara sin cambio. Corrección: feedback activo antes de Execute, fallback de speaker en primera línea, liberar cámara en todos los finales. Falta repetir en motor. | test_campaign_callbacks; reporte del usuario; no declarar solución nativa |
| RCM-602 | CRITICAL, verificación pendiente | Callbacks save/restore de campaña habían usado firma sin capture. Corregidas a `(int)` según Codex real. Offline save/restore pasa; persistencia nativa todavía sin aceptación. | tests Java y signatures originales |
| RCM-603 | HIGH, corregido | Fuente identificable inválida tras build válido podía dejar manifest anterior disponible. Backend, CLI y botón Build invalidan intento. | test_invalid_build_invalidates_previous_distribution, test_build_failure_invalidates_known_id |
| RCM-604 | HIGH, corregido | Escritura fallida a mitad de Deploy/Install/Uninstall dejaba cambios parciales. Preflight total, backup, reemplazos y rollback; manifest último. | fault injection de replace_files, publicación fallida y eliminación obsoleta |
| RCM-605 | HIGH, corregido | Java visible editado sin guardar no contaba como cambio pendiente. Ahora Save/Build/switch/close consideran ese buffer y conservan backup. | test_pending_java_is_committed_before_save, cancel_close |
| RCM-606 | HIGH, corregido | Un script propio podía pisar un controlador generado; se rechaza su namespace y sources dentro del build propio. | test_generated_java_namespace_collision_blocked |
| RCM-607 | HIGH, corregido | Borrar nodos, actores, quests o escena de entrada rompía referencias. Ahora se preflightan enlaces y nuevos errores sin mutar fuente; se cancela si quedan referencias. | delete_candidate y tests GUI/quest/entry/GOTO |
| RCM-608 | HIGH, corregido | Java/texturas cambian sin cambiar YAML: huella anterior no lo detectaba. Se incluyen bytes propios y se comprueba modificación durante build. | test_own_file_edits_invalidate_build_fingerprint |
| RCM-609 | HIGH, corregido | Un manifest de clean con `build/id/../otro` escapaba de la carpeta del build. Se rechaza antes de borrar. | test_clean_internal_traversal_cannot_delete_another_build |
| RCM-610 | MEDIUM, corregido | El gráfico declaraba destinos de `jump` como no alcanzables al buscar solamente objetos en lugar de strings del schema real. | test_story_graph_real_transitions_cycles_dead_and_orphan |
| RCM-611 | MEDIUM, corregido | Índices/configuración inválidos bloqueaban inicio. Recovery preserva datos; fallback seguro sin OpenGL. | fresh scan/repair, corrupt settings/cache, portable smoke |
| RCM-612 | MEDIUM, mitigado | Runtime puede producir logs repetidos ante error. Campañas rotan al superar 1 MiB, conservando una copia; logs con fallos de I/O se reflejan en consola. | Java real compilado; límite no probado dentro del juego |
| RCM-613 | HIGH, limitación | Reordenar/cambiar quests/events/entidades puede cambiar índices de flags/capture. Firma del contrato avisa de partida nueva. No hay migración de saves entre builds. | test_save_contract_change_is_reported |
| RCM-614 | MEDIUM, limitación | SpawnNear con radio cero puede juntar actores y dificultar distinguirlos. System Test etiqueta Witness/Keeper y añade diálogo; no garantiza separación espacial. | Confirmación previa del usuario, no precisión de colisión verificada |
| RCM-615 | MEDIUM, limitación | UI visual no tiene cobertura completa; panel NOT/AI y gráfica siguen con caminos manuales. Fase 5 no estaba completa al empezar esta auditoría. | FEATURE_MATRIX, coverage, aceptación específica |

Los corregidos se consideran cerrados sólo en el ámbito de sus pruebas. RCM-601/602 siguen bloqueando aceptación de beta porque sus cambios no tienen todavía prueba nativa actual. Los informes antiguos son evidencia histórica, no aceptación de la versión 0.6.0.

RCM-616 (HIGH, corregido en ensayo portable): tools/rcm.py ocultaba el package y producía ModuleNotFoundError; entry de empaquetado trasladado a build. RCM-617 (HIGH, corregido en ensayo portable): PATH global hacía incluir ICU de Poppler incompatible con Qt; búsqueda aislada y análisis de imports/exports. La prueba de arranque con workspace vacío, GL y compilación regresiona ambos errores.
RCM-618 (HIGH, corregido): validación de catálogo rechazaba archive:null de recursos sueltos originales; test_loose_resource_catalogue_accepts_null_archive conserva ese contrato y rechaza tipos corruptos.
# Estado actual de 0.9.0

Consulta [AUTHORING_MATURITY_REPORT.md](AUTHORING_MATURITY_REPORT.md) para los huecos reales y [RELEASE_BLOCKERS.md](RELEASE_BLOCKERS.md) para la aceptación pendiente. Llegadas y recorridos ya tienen implementación; siguen sin verificarse dentro de Redemption. Continúan abiertos control selectivo de estática, puertas/conexiones completas, cámara desde vista, portable en máquina independiente y aceptación nativa de diálogo, persistencia y NOT/AI. Las notas históricas siguientes no constituyen resultados de esta revisión.

