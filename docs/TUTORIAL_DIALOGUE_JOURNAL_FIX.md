# Tutorial 0.9.5: journal y cierre de conversaciones

## Confirmado por el usuario en Redemption 0.9.4

El inicio permite moverse, aparecen PNJ y se puede hablar con la mentora. El journal tiene dos entradas: resumen completo y primer objetivo. Durante el diálogo automático se puede caminar. Tras preguntar dónde se edita y elegir Volver, desaparecen interfaz y cursor. El log registra menu/result=2, help/result=1 y ningún regreso a menu. Se conservan log, fuente y estado en research/round0/dialogue_journal_fix. Esto sustituye la incertidumbre anterior sobre aparición de actores, pero no acredita save/load ni recorridos; sigue apareciendo PATH_FAILED route=0.

## Confirmado en archivos originales

CodexCamera.SetupCutscene(client,target0,target1) entra en modo de cutscene. La implementación JNI llama a 0x431e10, que llama a BeginCutscene interno 0x42f580. CodexCamera.Release y Codex.EndCutscene convergen en 0x42f6d0: devuelve cámara y controles al juego. Firmas originales: research/API_SIGNATURES.txt. Investigación sobre la copia del PE original: native_methods.txt y native_lifecycle.txt, en el directorio de evidencia de esta revisión. No se ejecuta el juego ni herramientas de autoría para obtenerla.

La rutina nativa de limpieza de conversación 0x458e40 retira recursos/estados de actores y pone el puntero global de conversación a cero al final. Esta implementación y el ejemplo SDK con SetTimer para encadenar conversaciones justifican evitar una nueva ExecuteConversation dentro de convended. No se añaden métodos supuestos para forzar el cursor.

## Confirmado en SDK/documentación

research/phase7/embrace/CodexCamera.htm.txt documenta SetupCutscene y Release. cutscene.htm.txt contiene UNIV_7_7: convended programa la siguiente conversación mediante SetTimer, incluso con tiempo cero; al terminar usa Release. Los modos de planos siguen procediendo de la API real.

## Corrección implementada

- Cámara automática: SetupCutscene(who,target,who) establece el modo de conversación y su encuadre predeterminado sin SetShot. Los presets conservan sus planos propios. La alternativa anterior `case native: return` omitía también el bloqueo de controles.
- convended guarda resultado/jugador/aborto como estado transitorio. El siguiente timer libera la cámara, reanuda recorridos y procesa acciones. No inicia diálogo, cutscene o viaje durante la limpieza del diálogo anterior. Se ignoran callbacks de otro jugador, cierres repetidos y clics mientras está pendiente el cierre. Restore descarta esa operación transitoria y libera controles.
- Ayuda/Volver vuelve al menú de la mentora; plano propio/Volver vuelve al cineasta. Cerrar y abortar no abren otro diálogo.
- Formato 9 carga sólo la entrada NQD del paso actual; la ficha general con todos los objetivos no se añade al journal. Al avanzar se completa el paso previo y se carga el siguiente. Completar la quest usa sus flags y recompensa sin cargar una fila adicional de resumen. Formatos históricos mantienen sus bytes y comportamiento.
- El tutorial presenta sólo «Habla con 01 Mentora» al llegar. Aceptar completa esa indicación e inicia la lección; los objetivos siguientes aparecen al avanzar. La guía exhaustiva de edición continúa en Tutorial / Ayuda del editor.

## Inferido y pendiente de verificar

La omisión del modo cutscene explica el movimiento durante el diálogo. Ejecutar un diálogo nuevo dentro del callback puede interferir con la limpieza nativa; no se atribuye todo fallo de UI a una única instrucción sin nueva prueba. La corrección y el orden se comprueban con Java/doubles, compilación contra Codex original y el editor empaquetado. La recuperación efectiva de HUD/cursor en Redemption 0.9.5 requiere prueba manual.

Empezar **una partida nueva** de RCM · Tutorial de creación: no cargar un guardado 0.9.4. Hablar con 01 Mentora → ¿Dónde se edita todo esto? → Volver → Cerrar. Durante el diálogo no debe caminar; Volver debe presentar el menú principal; Cerrar debe devolver interfaz y cursor. Repetir ayuda y probar abortar. El journal inicial debe contener una sola indicación; aceptar debe revelar el siguiente objetivo. El despliegue conserva paquetes anteriores en el workspace y sólo cambia RCM. No se lanza el juego automáticamente.
