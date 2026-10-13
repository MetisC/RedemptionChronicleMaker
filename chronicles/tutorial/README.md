# Una carta al amanecer

Tutorial breve sobre dos layouts de EastLondon. La misma geometría se conserva en ambos.

1. La entrada te deja en la calle. Anezka está delante. El diario contiene un único encargo, con el siguiente objetivo visible.
2. Habla con Anezka y acepta. La conversación termina con RETURN 1; el evento activa go_to_square. Rechazar o abortar no activa la flag.
3. Acércate al barril que está solo en la zona ancha de la calle, cerca del punto de inicio. No hay que pulsarlo: caminar junto a él activa la prueba. El volumen es trigger1 en el editor. Entrar sin aceptar no produce la película: hay que salir del volumen y volver a entrar después de aceptar.
4. Con la flag activa empieza una película de seis segundos sobre **tu personaje**: plano amplio en picado y transición a primer plano. Al acabar se libera cámara/control, se activa square_reached y avanza el diario. Es una transición de SetShot, no un dolly XYZ continuo.
5. Aparecen el libro que representa la carta y Tomás. Recoge el libro, que en el inventario se llama Carta para Elena. No tienes que abrirlo ni usarlo. Una sola rata básica aparece. Mátala, o habla con Tomás y elige omitir el combate. El camino queda abierto; omitir no entrega el premio de combate.
6. Habla de nuevo con Anezka. Después de matar la rata u omitir el combate, te ofrece «Llévame a Elena». Elige esa respuesta: viajas al segundo layout y su entrada propia. Allí está Elena. Entrega la carta; el journal se completa y recibes la recompensa una sola vez.
7. En el editor, guarda, valida, construye y actualiza la prueba con el juego cerrado.

Guardar a mitad de la nueva película la reinicia al cargar, después de recuperar la posición del jugador. La finalización se entrega una sola vez. Las películas antiguas de NPC conservan su contrato de cancelar al cargar. Cambios estructurales exigen partida nueva; no hay migración de saves del motor.

En Tutorial / Ayuda tienes enlaces para seleccionar cada elemento o abrir el asistente equivalente. Los experimentos antiguos se conservan en examples/advanced_tutorial, fuera de la historia principal.

## En el editor

[Entrada del jugador](rcm://square/entries/start)

**NPC te manda a un lugar** — [Muéstramelo en el tutorial](rcm://square/actors/actor1) · [Haz esto en mi crónica](rcm://wizard/go_to_place/new) · [Editar configuración](rcm://wizard/go_to_place/go_to_place1)

**Quest sencilla** — [Muéstramelo en el tutorial](rcm://square/quests/quest1) · [Haz esto en mi crónica](rcm://wizard/quest/new) · [Editar configuración](rcm://wizard/quest/quest1)

**Objeto recogible** — [Muéstramelo en el tutorial](rcm://square/objects/object1) · [Haz esto en mi crónica](rcm://wizard/pickup/new) · [Editar configuración](rcm://wizard/pickup/pickup1)

**Encuentro de enemigos** — [Muéstramelo en el tutorial](rcm://square/actors/enemy1) · [Haz esto en mi crónica](rcm://wizard/encounter/new) · [Editar configuración](rcm://wizard/encounter/encounter1)

**Viaje a otra escena** — [Muéstramelo en el tutorial](rcm://square/triggers/trigger2) · [Haz esto en mi crónica](rcm://wizard/travel/new) · [Editar configuración](rcm://wizard/travel/travel1)

**Viaje desde el diálogo** — [Respuesta «Llévame a Elena»](rcm://square/conversations/to_elena) · [Evento que realiza el viaje](rcm://square/events/talk_travel). Anezka usa esta conversación alternativa cuando el encuentro está terminado. La carta se entrega después hablando con Elena.

**NPC que habla** — [Muéstramelo en el tutorial](rcm://square/actors/actor2) · [Haz esto en mi crónica](rcm://wizard/talk/new) · [Editar configuración](rcm://wizard/talk/talk1)

**NPC que habla** — [Muéstramelo en el tutorial](rcm://home/actors/actor1) · [Haz esto en mi crónica](rcm://wizard/talk/new) · [Editar configuración](rcm://wizard/talk/talk2)

## Más tareas

[Trigger que ejecuta acciones](rcm://wizard/trigger_actions/new)

[Trigger cinematográfico](rcm://wizard/trigger_cinematic/new)

[Nota / carta](rcm://wizard/note/new)

[Objeto que inicia conversación](rcm://wizard/object_conversation/new)

[Arrival film](rcm://square/sequences/sequence1) · [Arrival trigger](rcm://square/triggers/trigger1) · [Quest](rcm://square/quests/quest1)

Después de entregar, puedes volver al barril visible en la calle de Elena: viajarás de regreso a Anezka para comprobar reentrada sin repetir la película ni los premios.
