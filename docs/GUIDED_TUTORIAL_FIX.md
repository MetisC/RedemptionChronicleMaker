# Tutorial guiado — revisión inicial 0.9.8

La revisión 0.9.9 sustituye la parada de animación y la cámara automática de
esta entrega. Véase [DIALOGUE_MOTION_CAMERA_FIX.md](DIALOGUE_MOTION_CAMERA_FIX.md)
para el comportamiento actual y el diagnóstico de la pose en T.

El tutorial tiene siete lecciones consecutivas. En cada momento aparece un solo
docente junto al punto inicial y el journal indica el objetivo actual. Cada
lección tiene una acción principal y «Omitir»: omitir entrega también los
requisitos necesarios para continuar, incluida la llave. Las pruebas opcionales
están en un laboratorio separado, al sur, fuera del recorrido principal.

| Lección | Demostración |
| --- | --- |
| 1 | Punto inicial, conversación y ubicación de sus datos en el editor |
| 2 | Cámara automática y ejemplo de primer plano sobre el hombro |
| 3 | Paseo de un personaje con tres planos durante ocho segundos |
| 4 | Inventario de un PNJ y entrega de una llave |
| 5 | Cambio de layout conservando la geometría de EastLondon |
| 6 | Aparición de una sola rata, combate y condición de muerte |
| 7 | Flags, guardado de partida y diferencia entre YAML y build |

Los docentes usan LonCiv3, gothGirl1, Otto, LonCiv2 y Bobbie. Los puntos del
recorrido principal se han contrastado con la geometría original. El barril es
decoración: aparece en la lección 5, separado del docente, y se retira antes del
cambio de layout. En el layout siguiente un guía explica cómo crear la rata,
que aparece cerca del punto de llegada. No se presenta el barril como una puerta.

## Correcciones de runtime

- Los dos interlocutores reciben `LookAtThing` antes de ejecutar el diálogo y
  al establecer su cámara. La cámara automática usa `SetupCutscene(who,target,0)`.
- Los clics no abren conversaciones mientras una secuencia temporizada está
  activa. El recorrido del actor sigue avanzando durante la secuencia; al parar
  vuelve a `MOTION_IDLE`.
- El evento `sequence_ended`, disponible en formato 9 y en el editor, permite
  avanzar cuando termina una timeline o un recorrido de cámara. Cancelar una
  secuencia no emite este evento.
- Un traslado entre layouts que reutilizan el mismo level selecciona
  explícitamente el NSD de destino con `ChangeScene` antes de `Jump`.
- El registro propio crea su carpeta bajo RCM si no existe. No escribe fuera
  de esa carpeta en la instalación del juego.

## Evidencia y límites

`tests/test_guided_tutorial.py` recorre todas las lecciones y, por separado,
omite todas. Sus motores simulados verifican objetivos, requisitos, orientación,
bloqueo de clics, avance del recorrido durante la película, tres planos,
liberación de la cutscene, selección del NSD y aparición de la rata. La
compilación usa la API real de Codex y genera clases 45.3.

Estos ensayos no prueban el aspecto de las cámaras, animaciones, colisión ni
la carga visual del layout en Redemption. El usuario confirmó que LAN vuelve
a funcionar tras la reparación de carga inicial de NOT; eso no certifica estas
modificaciones del tutorial.

Para probar esta revisión hay que crear una **partida nueva**, seleccionando
**RCM · Tutorial paso a paso**. Cambian los objetivos y la asignación de flags;
una partida guardada del tutorial anterior no sirve como prueba de este flujo.
Se conservan las plantillas de sus objetos para que el personaje persistido
pueda seguir cargándose en LAN.

La guía del editor está en `chronicles/tutorial/README.md`. Los resultados y
respaldos están en `research/round0/guided_tutorial/` y
`build/tests/guided_tutorial/`.


## Entrega verificada

El ejecutable 0.9.8 carga y compila el tutorial en su workspace portátil. El
visor 3D y los paneles se comprobaron con Qt/OpenGL reales en el código fuente;
el ensayo del ejecutable distribuido se hizo en modo seguro sin OpenGL.
La suite completa pasó 230 pruebas; posteriormente pasaron las cuatro pruebas
específicas de tutorial, incluidas las 20 posiciones sobre suelo y su altura
libre. Ruff, mypy y las pruebas de seguridad también pasan.

El paquete y las siete clases instalados en `RCM/east_demo` coinciden con el
build actual y con el compilado por el ejecutable. Las 43 fuentes originales
comprobadas y el perfil del personaje conservan sus hashes. La copia de
recuperación del tutorial anterior se archivó en el workspace para impedir
que reemplazara por accidente las nuevas lecciones; no se perdió su contenido.
Registro completo: `research/round0/guided_tutorial/delivery.json`.
