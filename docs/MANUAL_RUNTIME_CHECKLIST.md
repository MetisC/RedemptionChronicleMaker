# Prueba manual · 1.0.0-rc7

**MANUAL RUNTIME TEST REQUIRED.** RCM no automatiza Redemption. La historia del tutorial ya fue aceptada; esta lista comprueba el nuevo producto.

1. **SETUP01/02:** descomprime el ZIP de usuario en otra carpeta. Abre el EXE, selecciona Vampire.exe y comprueba la bienvenida y tus proyectos fuera del programa.
2. **PLAY01/TUTOR01:** abre Tutorial rÃ¡pido y pulsa F5. En Multiplayer → LAN → New Game elige Una carta al amanecer; completa el encargo. Si el personaje llevaba objetos RCM de antes, comprueba especialmente que LAN abre sin error.
3. **SHOW01–04:** abre Showcase completo y pulsa F5. Prueba diÃ¡logo/cÃ¡maras, nota/objeto, libro/llave/diario y una zona de activaciÃ³n. Las estaciones se pueden cerrar u omitir.
4. **SHOW02/05–08:** prueba la pelÃ­cula, animaciones, recorrido, rata bÃ¡sica, sonido y viaje al archivo/regreso. Anota cualquier posiciÃ³n, encuadre o colisiÃ³n incorrectos.
5. **SHOW09:** guarda/carga antes y despuÃ©s de recoger, completar y viajar. Vuelve a las escenas: sin premios, actores u objetos duplicados, y sin cÃ¡mara/UI atrapadas.
6. **PLAY02:** cambia una frase en el editor, guarda y pulsa F5 con el juego cerrado. Comprueba la frase nueva y repite F5 sin cambios; no deberÃ­a reconstruir.

Pendiente adicional: portable en un PC/VM independiente y revisiÃ³n visual a 100/125/150/200%. No se afirma esa aceptaciÃ³n por las pruebas de este equipo.

## Encuentros dinÃ¡micos · DYN01–12

Abre chronicles/dynamic_lab/project.yaml, guarda y pulsa F5 con el juego cerrado. En LAN → New Game elige **RCM · Dynamic Encounter Lab**. Usa una partida nueva. Anota PASS/FAIL y conserva el trace; todos estÃ¡n pendientes de observaciÃ³n nativa.

| Caso | Prueba y resultado esperado |
|---|---|
| DYN01 | Anezka → preparar oleadas → barril. Entrar en su zona crea tres ratas. Sin aceptar no empieza. |
| DYN02 | Mata las tres; tras dos segundos aparecen dos. No avanza si queda una viva. |
| DYN03 | Inicia el continuo desde Anezka: una cada cinco segundos, mÃ¡ximo tres vivas. Mata una y comprueba reposiciÃ³n. |
| DYN04 | DetÃ©n el continuo: no aparecen mÃ¡s; las vivas permanecen. Prueba tambiÃ©n pausa/reanudaciÃ³n. |
| DYN05 | Tras las oleadas aparece la rata jefe. Cruza 50%: dos refuerzos, una vez. Evita matarla de un golpe. |
| DYN06 | Cruza 25%: sonido espacial una vez, sin repetir por seguir por debajo. |
| DYN07 | Mata al jefe: termina encuentro/quest y se detienen refuerzos/continuo. Sin repetir premio. |
| DYN08 | Guarda con dos ratas vivas a mitad de oleada y carga: conserva grupo/cantidades, sin duplicar. |
| DYN09 | Guarda tras 50%, carga y espera: no duplica refuerzos. Comprueba 25%, muerte, carga y premio. |
| DYN10 | En copia del Showcase activa estaciÃ³n opcional, viaja/regresa activo y completo. Prueba Una vez/Continuar; despuÃ©s pruebas independientes de Reiniciar al volver/Cooldown. Roster perdido debe detener con error, jamÃ¡s duplicar. Anota si el motor conserva/restaura records entre instancias. |
| DYN11 | En copia cambia cantidad/plantilla en el asistente, guarda/F5 y empieza nueva partida si cambia contrato. Comprueba ediciÃ³n/undo/reabrir. |
| DYN12 | En copia usa puntos incompatibles que el motor realmente rechace, con pocos intentos. Reintento/rotaciÃ³n acotados, traza GENERATOR_SPAWN_FAILED/ERROR y juego respondiendo. Coordenada mala no garantiza fallo de factory: sin reproducir rechazo marca PENDIENTE, no PASS. |

El laboratorio no certifica colisiÃ³n/pathfinding. Enemigos normales Rat original; sÃ³lo boss x10 vida para ver umbrales. Showcase conserva encargo principal y ofrece laboratorio desde la GuÃ­a. Tutorial rÃ¡pido no aÃ±ade encuentros.

## Objetos originales y puertas · pendiente de prueba nativa

En una copia de una campaÃ±a, usa AÃ±adir… → Objeto original / crear paso…; no modifiques el tutorial aceptado.

| Caso | Prueba y resultado esperado |
|---|---|
| ORG01 | Elegir un prop visible de la escena estÃ¡tica. Ocultarlo al entrar: desaparece y deja de bloquear paso/cÃ¡mara. Los objetos parecidos no cambian. |
| ORG02 | Restaurarlo desde otro evento: recupera su aspecto y colisiÃ³n originales. Guardar oculto/cargar y viajar/regresar conservan el estado deseado. |
| ORG03 | Retirarlo: desaparece. Restaurar despuÃ©s falla con diagnÃ³stico; no lo recrea. Guardar/cargar y reentrada no lo resucitan. |
| ORG04 | Puerta original con frames: abrir frame 1, cerrar frame 0 despuÃ©s de moverla. Comprobar velocidad; en pivote, ambas direcciones y duraciÃ³n. Comprobar ademÃ¡s interacciÃ³n con el script original y save/load: no se certifican por compilaciÃ³n. |
| ORG05 | Crear zona editable y viaje, aÃ±adir condiciÃ³n de llave/flag; acercarse sin/con requisito. Verificar llegada y que no se altere la geometrÃ­a original. |
| ORG06 | Objeto ausente, ambiguo o puerta sin frames: se registra ORIGINAL_FAILED y no se mueve ni retira un objeto alternativo. Las acciones siguientes del evento siguen su orden normal. |

Estos casos permanecen pendientes; catÃ¡logo, compilaciÃ³n Codex y doubles no son observaciÃ³n del motor. La tolerancia de identidad es de ocho unidades y exige un Ãºnico prop local de la plantilla. No habilita borrar superficies fijas del NIL ni reconstruye el estado interno de Door/PivotDoor.

## WTD importado · pendiente de prueba nativa

| Caso | Prueba y resultado esperado |
|---|---|
| WTD01 | Sin importar, abrir tutorial y mini: mismo comportamiento; no aparecen clanes/disciplinas opcionales ni sus acciones. |
| WTD02 | ConfiguraciÃ³n → Importar NOB desde fuera del juego. SÃ³lo contenido disponible; menÃºs originales, sin crÃ³nica demo. Reiniciar editor y conservar catÃ¡logo. |
| WTD03 | Crear crÃ³nica sobre Penthouse y colocar entrada en suelo vÃ¡lido. Visor, entorno, suelo y puertas estÃ¡ticas; no confundir compilaciÃ³n con navegaciÃ³n nativa verificada. |
| WTD04 | Actor con clan y disciplina elegidos; conversaciÃ³n y animaciones normales. Enemigo con AI original: comprobar la disciplina, efecto, audio y objetivo concreto. |
| WTD05 | Evento concede disciplina al jugador y despuÃ©s cambia nivel/clan. Guardar/cargar y volver de escena sin duplicar premio ni reiniciar datos. |
| WTD06 | Inventario con item propio heredado de WTD; volver a otra crÃ³nica desde LAN tras cerrar playtest. Bibliotecas/paquete disponibles antes de restaurar Crypt. No editar el perfil. |
| WTD07 | DistribuciÃ³n de la crÃ³nica sin assets WTD. En otro workspace sin importar, validaciÃ³n/despliegue explica la dependencia; tras importar y reconstruir, se puede desplegar. |

Todos permanecen pendientes dentro de Redemption. La importaciÃ³n selecciona recursos con dependencias resueltas, no acredita cada combinaciÃ³n grÃ¡fica/AI, ejecuciÃ³n de poderes ni red multijugador.

ORG07 pendiente: en Tenebrae, identificar la salida real por clic derecho, ocultar/restaurar y comprobar el paso; las dos puertas fijas del fondo ofrecen transiciÃ³n, conservan su aspecto y ofrecen una interacciÃ³n por clic con etiqueta; no deben viajar al acercarse.


CLICK01–08 — PENDING / PENDIENTE (new native brush layer):

| Case | Manual check |
|---|---|
| CLICK01 | One-scene project: self travel/jump cannot build; destination excludes current scene. No native launch is needed to test rejection. |
| CLICK02 | Tenebrae: right-click each back door, distinct selectable patch and editable hover label. Build/deploy; hover shows the authored label. |
| CLICK03 | Approach/walk past door: nothing happens. Click: exactly one configured action. Check selection/highlight against original geometry and collision near the edge. |
| CLICK04 | Two scenes on same/different NIL: click travel reaches chosen entry once; no repeated transition. Return and click again. |
| CLICK05 | Click note, conversation with NPC speaker, flag, quest, sequence and Event / Run. Conditions/key guard exact selected action; note/dialogue restores UI/cursor. |
| CLICK06 | Save/load with the clickable prop: same label, capture and one-time/repeatable state; no duplicated mesh or callback. |
| CLICK07 | Remove a click prop during gameplay and revisit; check intended lifecycle and no invisible blocking volume. Editor deletion/cascade and undo preserve unrelated events. |
| CLICK08 | Multiplayer: client selection reaches server once, target belongs to the correct scene; no duplicate action or transition. Not certified by doubles. |

CLICK09 / ARRIVAL01 — USER CONFIRMED for the tested new-game clicks and initial movement; load/re-entry remain PENDING: In «Mi nueva crónica» (RaveClub), start a new game, issue one nearby floor click immediately after arrival and verify the direct route; repeat after travel and save/load. Hover/click Salida: first note. Hover/click second prop: NOTA 11 and 1000 XP, exactly once per click. Walking past must not run either action. Inspect CLICK_BOUND/CLICK_RECEIVED and absence of repeated SPAWN_FAILED in RCM/new_chronicle/runtime_trace.log.

CLICK10 / ARRIVAL02 — USER CONFIRMED for the tested new-game clicks and initial movement; load/re-entry remain PENDING: «Mi nueva crónica», new game after native NSD entry build. Hover all three click props and invoke each authored action. First floor click after entry must use the correct route; repeat after travel and load. Expected trace: CLICK_BOUND and CLICK_RECEIVED; ARRIVAL_AFTER must match the authored native entry. In editor, create a fourth drippyCandle interaction: click_drippyCandle_4, editable. Right-click an unbound fixed door: temporary bounds remain during menu/dialog and disappear on cancel, without new data.

# Cierre del Director de escenas · EMB01–24

**PENDIENTE DE PRUEBA DENTRO DEL JUEGO.** Usa una copia nueva de Ayuda → Crónica de prueba: el refugio y copias del Showcase para los casos específicos. No cambies el tutorial aceptado. Anota resultado, huella del build, guardado y traza. Validación, compilación real y doubles son evidencias distintas.

| Caso | Procedimiento y resultado esperado |
|---|---|
| EMB01 | Pulsa la salida original del club con etiqueta Refugio. Tiene hover; acercarse no dispara nada; el clic inicia la conversación una vez. La aceptación anterior del usuario se conserva para aquel escenario/build. |
| EMB02 | En copia usa una puerta original con frames/pivote conocidos. Abre/cierra, guarda/carga y regresa. Comprueba colisión y script original. La salida del refugio se oculta: no demuestra animación de puerta. |
| EMB03 | Crea interacción sobre otra superficie fija. Sólo se ilumina y responde el parche elegido; los bytes NIL no cambian. |
| EMB04 | Habla con Elena: plano sobre hombro, interlocutores visibles y orientados, sin pose T. Al terminar/cancelar vuelven GUI, ratón y movimiento. En copia prueba una entrada de puesta en escena nombrada. |
| EMB05 | En copia añade tres acciones temporales de cambio de plano, variando sujeto/referencia e incluyendo al jugador. Se ejecutan en orden y conservan el control de la película. |
| EMB06 | El guardia mira y gesticula durante la llegada; no desaparece y recupera una pose válida. Prueba otro gesto ofrecido para su NMS real. |
| EMB07 | El guardia camina durante la película. Terminar/cancelar detiene el recorrido iniciado por ella y libera la cámara. Los recorridos anteriores mantienen su política. |
| EMB08 | Elige un NCP original conocido para esa geometría. Se reproduce y termina. Un travelling de otro escenario no sirve para juzgar el encuadre. |
| EMB09 | Captura un único punto de cámara y reprodúcelo como plano fijo. Comprueba XYZ/orientación y devolución del control. No se ofrece FOV por punto. |
| EMB10 | Captura tres puntos distintos. Comprueba orden, extremos, orientación y giro corto. Evita paredes: el preview no simula el clipping del motor. |
| EMB11 | Repite a velocidades 15, 30 y 60. Más velocidad debe reducir tiempo sin cambiar extremos. El parámetro no son segundos. |
| EMB12 | Fundido desde negro al entrar y a negro al terminar; limpia efectos. Cancelar/cargar no deja pantalla negra permanente. |
| EMB13 | En copia añade flash blanco y filtro blanco breves, después limpia efectos. Comprueba intensidad/duración reales. No hay presets de color inventados. |
| EMB14 | Oye el sonido situado una vez durante la escena. Comprueba volumen y distancia al waypoint; no se repite cada tick. |
| EMB15 | Al terminar la llegada se libera el control, cambia el journal y aparece una rata débil. Esperar/repetir clic/poll no duplica el evento. |
| EMB16 | Guarda durante una película con cues, carga y espera: se cancela, vuelve GUI y no repite efectos ya ejecutados. La mentora permite continuar. Comprueba aparte la política anterior de reanudación de películas antiguas del jugador. |
| EMB17 | Omite/cancela; en otra copia retira un actor requerido antes de su cue. Fallo acotado y control recuperado, sin traza de fallo cada tick. Intenta iniciar otra película/conversación mientras una tiene el control. |
| EMB18 | Dos líneas con acciones de mirar, plano y sonido: se ejecutan en la línea correcta y GOTO/RETURN sigue funcionando. Se rechazan interacciones modales desde una línea, también mediante run_event. |
| EMB19 | En copia inicia bucle espacial al entrar en trigger y detén al salir. Guarda activo/carga, viaja/regresa y repite. Un único sonido propio se recrea; Detener lo termina. |
| EMB20 | En copia luz dinámica sobre prop propio: estilo/color/radio, retirar, guardar/cargar y reentrar. Prueba llovizna, lluvia ligera/intensa y nieve por separado. Comprueba aspecto/estado; no cambia iluminación horneada. |
| EMB21 | Con importación local WTD usa actor/gesto compatibles y clan/disciplina durante secuencia. Guarda/carga. Sin WTD los ejemplos ordinarios funcionan y los paquetes públicos no contienen assets del mod. |
| EMB22 | Completa Llegada al refugio: clic → diálogo → película u omitir → rata débil → mentora → fundido/viaje → epílogo. Repite desde inicio y guardado; sin premio duplicado. |
| EMB23 | Edita punto/cue/acción de línea, undo/redo, guarda, cierra/reabre y F5. El travelling acompaña al proyecto e invalida build. Exporta/importa proyecto y paquete; borrar recurso usado ofrece cascade validado. |
| EMB24 | PC/VM Windows independiente, sin Python/JDK del sistema: portable EN/ES, instalación propia, abrir/construir/ejecutar ejemplo manualmente. Anota GPU/DPI físico, cámara y audio. Mover carpeta y usar offscreen no lo certifica. |

Esta batería nueva queda pendiente de observación del usuario. El primer desplazamiento y los clics reparados ya fueron confirmados en su prueba anterior; no acredita cinematics nuevas, cargas, reentrada o red. EMB02 depende del recurso: no anima caras fijas del NIL.

LOAD-META-01 — Tras actualizar el editor, abrir Taller del Narrador → Probar en Redemption → crear partida nueva y elegir el módulo. Debe terminar la carga y aparecer la escena inicial. Repetir entrando al laboratorio opcional y regresando. El usuario confirmó la carga inicial corregida el 18/10/2026: «Funciona bien y abre». Viaje/regreso al laboratorio y comportamientos nuevos siguen pendientes de sus casos manuales. Comprobar aparte que tutorial y mini siguen cargando.

## Cierre quirúrgico: casos manuales nuevos

Los casos siguientes siguen MANUAL RUNTIME TEST REQUIRED. El usuario sólo confirmó la carga inicial del Showcase el 18/10/2026.

| Caso | Comprobación |
|---|---|
| EMB-MUSIC-01 | Música normal → pista temporal a volumen 50 → restaurar. Vuelven pista y volumen anteriores. |
| EMB-MUSIC-02 | Ejecutar cues de música temporal/restaurar; terminar, cancelar y repetir. Una única restauración propia. Push anidado se rechaza. |
| EMB-MUSIC-03 | Guardar/cargar durante música temporal y viajar/regresar. Al cargar se descarta propiedad sin Pop desconocido. Establecer música normal explícitamente si hace falta. No retirar música reemplazada por otro script. |
| EMB-CONV-01 | Usar la puesta en escena anterior por Entrada RCM. Comparar posición, orientación, party y cámara antes/después. |
| EMB-CONV-02 | Elegir Punto de conversación nativo y tres marcadores de compañeros. Verificar cuatro posiciones, giro Z, suelo/colisión e inicio del diálogo. |
| EMB-CONV-03 | Guardar/cargar antes y después de la puesta nativa. Sin movimiento duplicado ni desplazamiento acumulado. |
| EMB-CONV-04 | Terminar y abortar conversaciones colocadas. Regresan GUI, cursor y movimiento. |
| EMB-CONV-05 | Viajar, regresar y repetir en SP; comparar iniciadores reales de MP aparte. Las APIs de teleport no son internamente idénticas. |
| EMB-NCP-01 | Reproducir oldtownday/prague_3_3_bed originales en su geometría. Observar qué hace con claves repetidas. |
| EMB-NCP-02 | Un punto propio mantiene plano fijo durante la secuencia y devuelve el control. |
| EMB-NCP-03 | Trasladarse entre puntos distintos cambiando orientación. Comprobar extremos, giro corto y encuadre. |
| EMB-NCP-04 | En modo por distancia, posiciones consecutivas iguales se rechazan; en Tiempo por tramo probar giro y espera estacionarios con duración explícita (COMP01). |
| EMB-NCP-05 | Comparar velocidades, cancelar/terminar y repetir. Registrar clipping y devolución del control; el preview no acredita el render nativo. |


## Strict non-geometry authoring acceptance

All cases below: **MANUAL RUNTIME TEST REQUIRED**. Use a new game in the optional
`chronicles/strict_acceptance/project.yaml` (Cargo at the refuge). Automated
compilation, readback and Qt tests do not certify any native result.

- EMB-ENV-01: change initial music/ambient volume, silence, linear fog RGB/range,
  ZClip and a compatible paired sky through Level > Environment. Reopen project;
  test initial scene, re-entry and save/load. EAX inherits unless an optional roomtype override is selected; see COMP03 and compatible provider requirement.
- EMB-TEMPLATE-01: edit Elena's instance hover/Foley; verify other instances keep
  their template values. Undo/redo, save/reopen/export. Use model-compatible NMS.
- EMB-TREASURE-01: break/open class-230 supply barrel and inherited comparison;
  repeat random rolls. Save/re-enter before and after looting; no duplicate loot.
- EMB-CODEX-01: cargo moves with original ClassBobbing. Edit scalar speeds/delay
  and linked target/frame through Native script; no custom Java or raw YAML.
- EMB-CODEX-02: save/reload while cargo moves; verify handles and callbacks remain
  with the original script and there is no duplicate entity or reset loop.
- EMB-CODEX-03: rename linked object/waypoint, inspect References and cascade
  delete with undo; missing frame must not silently retarget native indices.
- EMB-INTEREST-01: configure a compatible active AI with interestNum 8 and matching
  waypoint group; observe native idle interest selection, not an imposed route.
- EMB-LIBRARY-01: import a data-only NOT/NOB through Settings, select new templates,
  build/deploy and use one in a scene. Export ZIP must contain references only;
  absent/changed local dependency must fail clearly. No arbitrary mod code import.


## DIFF — optional combat difficulty

MANUAL RUNTIME TEST REQUIRED. Use a disposable new chronicle/game and compare the
same weak enemy in Normal, Easy, Hard and Nightmare; do not overwrite your saves.

- DIFF01: default/Normal retains familiar combat, NPC conversations and movement.
- DIFF02: compare melee enemies and equipped enemies at each setting; confirm
  Easy does not break their equipment/AI and harder modes retain relative roles.
- DIFF03: spawn manual enemies and dynamic waves/bosses; allies and neutral NPCs
  stay unchanged. With custom HP50, Nightmare starts at75; percent phases track
  the scaled maximum while absolute thresholds stay absolute.
- DIFF04: wound an enemy, save/load and re-enter; no healing, repeated scaling or
  duplicate enemy, phase or reward. Check subsequent genuinely new spawns too.
- DIFF05: change difficulty, rebuild and load a disposable existing save: old
  enemies keep old values; new enemies use the new setting. Inspector/build warn
  to start a new game for consistent balance; no save migration is promised.
- DIFF06: if testing multiple clients, verify host-only initialisation and native
  stat replication. Offline doubles do not certify network combat/persistence.


## Prioridad actual: laboratorio de autoría

COMP01–06 en AUTHORING_COMPLETION.md son las seis comprobaciones cortas nuevas.
Siguen pendientes hasta observación del usuario. No sustituyen los casos DYN/EMB
ni acreditan red, restore nativo o GPU/DPI a partir de Qt/doubles/compilación.
