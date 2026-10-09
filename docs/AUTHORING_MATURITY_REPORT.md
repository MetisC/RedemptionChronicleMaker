# Madurez de autoría · Fase 9 / 0.9.0

## CURRENT STATE

Implementación técnica ampliada y circuito único preparado. El usuario ha aplazado las pruebas nativas para hacerlas manualmente después; esa decisión permite avanzar y no convierte los casos pendientes en PASS. Auditoría de 59 apartados conservada, baseline 188 tests; la suite ampliada pasó 198, sin fallos/errores/skips. Gate de calidad PASS. Evidencia: `research/phase9/`, `build/tests/quality_report.json` y `build/rcm_circuit/build_report.json`.

## RESOLVED CONCERNS

Nueva crónica crea campaña directamente; escena y geometría se cuentan por separado; IDs admitidos desde el diálogo. Entradas y waypoints son capas propias con colocación real en 3D, transforms, referencias, undo y selectores de viaje. Recorridos tienen lista ordenada y loop; generación usa navegación original. Save contract incluye las nuevas estructuras. Eventos once conservan checkpoints por acción y progreso para reintentar fallos sin repetir experiencia ni perder un evento cuando sus propias acciones cambian sus condiciones. Deploy retira únicamente obsoletos con ownership verificable y conserva archivos ajenos/modificados. Se miden límites reales de métodos/constant pool. Logs se enlazan a acciones, diálogos y quests.

## OPEN CONCERNS

No hay eliminación ALL/NONE/SELECTIVE fiable del contenido estático. Puertas/exits no son un sistema completo de conexiones y cerraduras. NCP/cámara desde vista siguen abiertos. Audio espacial persistente, presentación por línea y AI avanzada son parciales. No existe migrador de saves entre builds. Los métodos enormes pueden ser rechazados por ECJ; se compila por escena y mide Code/pool, pero no se ha implementado partición automática general de un evento ilimitado. Falta la aventura completa creada por un humano sólo mediante GUI y su aceptación de principio a final.

## RUNTIME VERIFIED

Históricamente: usuario aceptó NPC, diálogo a pantalla completa y decisiones de Fase 2; fondo gris original aceptado. En 0.7.0 informó tres NPC, conversaciones y viaje con enemigos que le mataban. Evidencia limitada en `research/phase9/phase7_user_observation.json`. No acredita todos los abortos, guardados ni la revisión nueva.

## RUNTIME NOT VERIFIED

Todo el circuito 0.9.0. Llegadas nuevas, patrullas, presets de cámara, audio situado, puertas/exits, actor/item propios, quests, rewards, save/load, tres ciclos de reentrada y red quedan pendientes. Ni Code45.3 ni un log de callback prueban controles, colisión o apariencia.

## PLAYER ENTRY STATUS

Entradas lógicas nombradas, XYZ/pitch/roll/yaw, default por escena y destino por viaje. Tras Jump(alias,0) se aplica transform con SetPosition/SetOrientation; la carga no recoloca al jugador. No se alteran tablas de entrances/portal/revive del NIL. El circuito coloca la llegada a 156 unidades de Victoria en suelo comprobado por raycast. Colisión/transitabilidad pendientes.

## DOORS/EXITS STATUS

OpenExit/CloseExit comprueban IsExitValid. Movimiento existente usa MoveToFrame o RotatePivot conforme a Door/PivotDoor; valida existencia local y frames. El Cast ID y frames reales deben conocerse. No sustituye su script ni su estado interno bOpen, ni implementa bloqueo/desbloqueo por llave. No se ha incluido una puerta ficticia en el recorrido obligatorio: la paridad completa de puerta sigue abierta.

## PATHS STATUS

Dos recorridos opcionales al rendimiento de navegación, cercanos a la llegada. SendActorToPos emplea un parámetro de 90 como ejemplos originales; escala exacta por verificar. Índice, espera y activación persistidos. Se detiene con timeout/fallo y se pausa durante diálogo; no crea navmesh. Comprobados lógica con doubles, compilación, GUI y overlay real; caminabilidad nativa pendiente.

## STATIC SCENE STATUS

NSD static del mismo stem que NIL puede permanecer. No se anuncia geometry-only completo ni se borra decoración por suponer que no forma parte del paquete. Inspector muestra confianza del hint y esta limitación. El archivo usa GunHaven; puede conservar armas/props originales de su static NSD.

## SAVE/LOAD STATUS

Callbacks reales save(int), restore(int), restored(int); flags para once/quest/arrival/acción y arrays para GUIDs/recorridos. Checkpoints evitan repetir acciones ya completadas dentro de un evento once, incluso si sus condiciones han cambiado. No son una transacción nativa atómica: efectos nativos y flag de checkpoint no tienen commit conjunto, especialmente si se guarda dentro de un callback reentrante. Hay firma y aviso de partida nueva, no migración. B2 sigue abierto.

## .NOT RUNTIME STATUS

Subconjunto read/write conocido con conservación de opacos. Circuito incluye template propio de Victoria y libro heredado de ledger, AI propia y clase propia. Readback/compilación/paquete comprobados; herencia efectiva y uso en Redemption pendientes B3. No se requiere NOT Editor.

## PORTABLE STATUS

Distribución reconstruida con versión 0.9.0, dependencias/JVM propias y sin activos originales. Ver `build/portable_build_report.json` y prueba local satisfactoria en `research/phase9/portable_probe.json`: proyecto válido, compilación 45.3 y OpenGL real sin Python/JDK globales en PATH. La prueba en esta máquina con otro workspace no equivale a equipo/VM independiente: B4 continúa abierto.

## AI STATUS

NPC neutral, enemigo, pausa/activación y recorridos controlados. Presets legibles de NAI ajustan sólo campos presentes; preservan líneas desconocidas. No hay comportamiento completo de escolta/facción/árbol AI. Parámetros y resultados deben probarse en combate.

## CAMERA STATUS

Auto diálogo en formato9 emplea speaker/listener y MS/ángulo medio. Secuencias admiten siete presets derivados del SDK SetShot con A=speaker, C=listener. Two Shot usa ANGULAR_B, no PROFILE_A que el propio manual considera incierto. Restaurar libera cámara del jugador aunque el nuevo controlador no conserve cameraPlayer. NCP desde vista no se ofrece como exportación operativa.

## AUTHORING PARITY STATUS

[Checklist Aurora](AURORA_PARITY_CHECKLIST.md) distingue YES/PARTIAL/NO. Proyecto básico creado desde diálogo, clics sobre suelo, inspector y paneles; guardado/reapertura/build probados con OpenGL real, sin modificar YAML. El circuito completo se generó desde una fuente curada reproducible; no se presenta como aventura completa hecha en GUI. Una capa de geometría compartida no obliga a compartir historia/actores.

## BLOCKERS FOR 1.0

B1/B2/B3 nativos; B4 máquina independiente; control fiable de estática y puertas/conexiones; autoría humana y juego completo; límites de proyectos grandes; documentación del subconjunto real. B5 impide anunciar red, pero no bloquea por sí mismo una futura beta explícitamente local.

## RECOMMENDED PRIORITIES

Completar manualmente [el circuito](PHASE9_PLAYTEST.md) y corregir casos reproducibles; después static/puertas y máquina limpia. Mantener NCP/audio persistente como investigación con evidencia. No ampliar geometría ni iniciar otra fase para eludir bloqueos. Esta entrega no declara beta aceptada ni 1.0.
