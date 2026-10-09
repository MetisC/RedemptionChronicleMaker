# Inicio del tutorial — revisión 0.9.3

## Observado en el motor

El usuario comunica que el tutorial 0.9.2 comienza en un punto sin poder hacer clic sobre el suelo ni desplazarse. El log nativo contiene ARRIVAL workshop/safe y sólo la primera acción de spawn del evento arrival, sin confirmación de creación. Copia preservada en research/round0/spawn_fix/native_failed_092.log. No es aceptación del tutorial; se registra FAIL para inicio/transitabilidad y preparación de NPC.

## Confirmado en archivos originales

EAST_28_1.nsd coloca un bobbie en [-176,-768,384], sector119, con script WalkCycleLawmen. l1_east.nil tiene suelo en ese punto; raycasts verticales por el centro y alrededor no encuentran obstáculos dentro de los 110 puntos superiores. Las estaciones cercanas se apoyan sobre la malla. Evidencia de candidatos: research/round0/start_anchor_candidates.json. Esto no equivale a consultar la navegación/collision nativa del jugador.

## Corrección preparada

Se mueve el tutorial completo a ese entorno, conservando tres layouts y distancias entre estaciones. La mini crónica compartía la llegada anterior: también se trasladan sus dos layouts de EastLondon; su archivo de GunHaven no cambia. La rata se coloca en suelo verificado de la misma calle. No se altera NIL. El editor añade Espacio 3D → Inicio para localizar la llegada por defecto de la escena inicial y Ayuda → Tutorial del proyecto para acceder a la guía aunque la pestaña esté fuera de la barra visible.

Runtime formato9 libera la cámara al completar una llegada propia y registra posición antes y después de la llegada y el fallo de spawn, incluyendo plantilla, GUID y ubicación actual. No se cambia la API de creación ni se atribuye todavía el fallo a un formato NOT concreto.

Los marcadores, nombres y gizmos se componen en una capa Qt transparente por encima de OpenGL, conservando el control del ratón en el viewport. La revisión visual mostró que antes no aparecían sobre la geometría; ahora la llegada seleccionada se distingue en amarillo. La captura y comprobación automática de esos píxeles quedan en research/round0/spawn_fix.

## Pendiente

La causa nativa precisa del bloqueo anterior sigue sin aislarse. SetPosition devolvió éxito, lo que no certifica un punto navegable. La falta de confirmación de spawn puede tener otra causa; las nuevas trazas ayudan a distinguirla. La revisión 0.9.3 debe probarse en una partida nueva; restore conserva posición y no recoloca guardados antiguos. No se inicia el juego automáticamente.

Confirmación posterior del usuario: la llegada 0.9.3 permite caminar, pero no crea PNJ; su log muestra GUID 0. La revisión siguiente se documenta en [TUTORIAL_NPC_JOURNAL_FIX.md](TUTORIAL_NPC_JOURNAL_FIX.md).
