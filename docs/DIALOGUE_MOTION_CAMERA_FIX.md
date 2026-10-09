# Conversación, animación y recorrido de cámaras — 0.9.9

La cámara predeterminada es `ots_speaker_close`: sobre el hombro del personaje
que escucha, mirando a quien habla. El editor la selecciona al crear una
conversación y la muestra cuando no hay un valor explícito en el YAML. El
generador aplica ese mismo valor a las conversaciones de formato 9 sin cámara.
Las elecciones explícitas se respetan. `native` permanece compatible, con la
etiqueta «Automática del motor (experimental)» y al final del selector.

Vera tiene una explicación breve y trece ejemplos separados. Cada respuesta
«Siguiente plano» termina el diálogo actual; su liberación diferida inicia el
ejemplo siguiente con su propio encuadre. No hay avance automático. Cada ejemplo
permite omitir los restantes y pasar a Otto. Los textos de profesores,
laboratorio y journal se han reescrito en un tono más conversacional.

## Regresión de animación

La revisión 0.9.8 llamó a `StopActorMotion` para detener interlocutores antes de
girarlos, y de nuevo al recibir una línea. El usuario observó pose en T tanto
en el PNJ como en su personaje. Fue una regresión de esa revisión.

La 0.9.9 usa `StopActorAction` únicamente antes de iniciar la conversación.
El callback de cada línea sólo gira con `LookAtThing` y coloca la cámara;
no cancela acciones ni borra animaciones. Las paradas de recorridos usan
también `StopActorAction`, sin forzar el modo de reposo desarmado.

### CONFIRMADO EN ARCHIVOS ORIGINALES

La tabla nativa de Vampire.exe enlaza `StopActorMotion` con `0x46c650`, que
llama a `0x4c83f0`. Esa rutina pone a cero los campos `[ecx]` y `[ecx+8]` si
el segundo estaba activo. `StopActorAction` se enlaza con `0x46c6a0`, llama a
`0x4c83d0`, limpia otros campos y continúa por `0x4c8ec0`.
Son operaciones distintas, no dos nombres para la misma parada.

Registro reproducible: `tools/research_actor_motion.py` y
`research/round0/dialogue_motion_camera_fix/native_motion_bindings.json`.
Sólo se lee el ejecutable, nunca se ejecuta una herramienta original de autoría.

### CONFIRMADO EN SDK/DOCUMENTACIÓN

El ejemplo original de cutscene usa `_Wilhem.StopActorAction()` al cambiar de
plano. También muestra giro recíproco con `LookAtThing`. Fuente:
`research/phase7/embrace/cutscene.htm.txt`, eventos de la conversación de balcón.
La API extraída contiene ambas funciones nativas.

### INFERIDO

La limpieza de la animación activa mediante StopActorMotion explica la pose en
T comunicada por el usuario. Conservar el control nativo de la animación al
girar, y detener acciones sin borrar su movimiento, debe evitar esa regresión.
No se atribuyen nombres definitivos a campos internos sólo por sus offsets.

### PENDIENTE DE VERIFICAR

La compilación usa la API real y las pruebas con doubles simulan la pérdida de
animación si se invoca StopActorMotion. Comprueban que los diálogos y los cambios
de línea no la provocan. La prueba recorre los trece encuadres y verifica que
cada uno espera una respuesta del usuario antes de cambiar.

Falta confirmar visualmente en Redemption la animación y la composición de
cada plano. Esta revisión conserva siete lecciones y los mismos objetos propios;
se recomienda una partida nueva para recorrer desde el principio los nuevos
ejemplos de Vera.


## Entrega

Editor y tutorial 0.9.9 actualizados. Pasan 233 regresiones y el ejecutable
portable carga y compila el tutorial en modo seguro. Los paquetes y clases
instalados coinciden con el build. La clase desplegada no contiene ninguna
llamada StopActorMotion. Las 43 fuentes originales comprobadas y el perfil del
personaje se conservan. Evidencia: research/round0/dialogue_motion_camera_fix/.
