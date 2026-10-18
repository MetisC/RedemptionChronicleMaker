# Taller del Narrador

Este Showcase es una pequeña aventura con un laboratorio opcional. Sirve para ver cómo se combinan las herramientas de RCM y localizar sus ejemplos en el editor. Sigue el encargo o detente a experimentar; no tienes que visitar cada estación.

## Empieza aquí

1. Abre el Showcase y pulsa **F5** para prepararlo. En Redemption, entra manualmente en tu crónica.
2. Al llegar al taller, habla con [Anezka](rcm://quay/actors/victoria) y acepta el encargo. Puedes consultar la [conversación inicial](rcm://quay/conversations/intro) en el editor.
3. Habla con la [guía](rcm://quay/actors/guide), a su lado. Elige «Viajar al archivo» para seguir la historia; sus otras opciones pertenecen al laboratorio.
4. En el archivo, habla con la [archivera](rcm://archive/actors/archivist) y elige cómo conseguir el libro.
5. Con el libro y la llave, habla con la [custodia](rcm://archive/actors/keeper) para regresar.
6. Habla con el [testigo](rcm://return/actors/witness) y termina la entrega. La mensajera permite volver al comienzo.

## Ruta principal

El [taller](rcm://quay/scene/quay) usa EastLondon. El [archivo](rcm://archive/scene/archive) usa otra geometría. El [regreso](rcm://return/scene/return) reutiliza EastLondon con personajes y estado distintos: una escena es una capa de contenido, no una geometría nueva.

El [encargo del libro](rcm://quay/quests/ledger) permite seguir el progreso en el diario. La [decisión en el archivo](rcm://archive/conversations/ledger) cambia la respuesta del testigo. Ambas ramas llegan al final; volver al inicio permite revisar el estado que recuerda la historia. Las recompensas deben entregarse una sola vez.

## Laboratorio opcional

### Cámaras

La guía ofrece «Ver los planos uno a uno». Empieza en la [primera conversación de cámaras](rcm://quay/conversations/cam1) y avanza con Siguiente para comparar encuadres. En el editor, selecciona la conversación y cambia su cámara en Propiedades. La [secuencia de llegada](rcm://quay/sequences/sequence1) muestra un ejemplo independiente de película.

### Animaciones

La [conversación de gestos](rcm://quay/conversations/anim) muestra únicamente animaciones disponibles en el modelo de la guía. Selecciona un nodo o una línea para localizar su opción de animación. Cada modelo tiene su propio repertorio.

### Recorridos / Waypoints

Desde «Recorrido y sonido» puedes iniciar y detener el paseo de la guía. El [recorrido](rcm://quay/paths/guide_walk) enlaza [su primer punto](rcm://quay/waypoints/guide_a) con [el segundo](rcm://quay/waypoints/guide_b). La geometría permanece intacta; la navegación real se comprueba al jugar.

### Sonido

La misma [conversación del laboratorio](rcm://quay/conversations/lab) permite reproducir música, ambiente y un trueno desde [un punto de la calle](rcm://quay/waypoints/audio), y detener música y ambiente. En el editor puedes localizar las acciones en el [evento de sonido](rcm://quay/events/controls4).

### Objetos y notas

El [cartel](rcm://quay/objects/notice) muestra una nota al pulsarlo; cerrar la nota puede continuar un evento. El [atril](rcm://quay/objects/talkprop) inicia una conversación desde un objeto. El [libro del laboratorio](rcm://quay/objects/sample) muestra recogida y cambio de estado. La [llave de la guía](rcm://quay/objects/lab_key) pertenece a su inventario inicial.

### Combate opcional

La guía sólo activa [la rata](rcm://quay/actors/enemy1) si lo eliges expresamente. Es un enemigo básico y **no es obligatorio para completar la historia**. Puedes omitir el combate desde la conversación de la guía.

## Prueba de campo

El viaje al archivo y el regreso permiten comprobar cambios de localización, llegada y dos escenas sobre la misma geometría. La custodia ofrece una [prueba opcional de plano y sonido](rcm://archive/sequences/two_shot).

Prueba guardar y cargar, volver al comienzo y repetir una interacción. Comprueba que el diario, inventario, decisiones y recompensas conservan el estado esperado. Estas comprobaciones las realizas tú en Redemption: la compilación y los tests offline no equivalen a aceptación del recorrido real.

Los enlaces de la guía seleccionan elementos del proyecto en el editor. El índice siguiente conserva todos los enlaces de referencia; no necesitas leerlo para jugar la aventura.

### Encuentros dinámicos (opcional)

Habla con la Guía y elige el laboratorio de encuentros dinámicos. Puedes probar [dos ratas](rcm://quay/generators/dyn_rats), [el jefe por fases](rcm://quay/generators/dyn_boss) y [un refuerzo](rcm://quay/generators/dyn_add), o iniciar y detener [el continuo](rcm://quay/generators/dyn_portal). El encargo del libro no cambia. Guarda/carga a mitad y compara el grupo.

## Índice técnico completo

- [quay · safe](rcm://quay/entries/safe)
- [quay · victoria](rcm://quay/actors/victoria)
- [quay · guide](rcm://quay/actors/guide)
- [quay · enemy1](rcm://quay/actors/enemy1)
- [quay · notice](rcm://quay/objects/notice)
- [quay · sample](rcm://quay/objects/sample)
- [quay · talkprop](rcm://quay/objects/talkprop)
- [quay · lab_key](rcm://quay/objects/lab_key)
- [quay · arrival_zone](rcm://quay/triggers/arrival_zone)
- [quay · trigger1](rcm://quay/triggers/trigger1)
- [quay · guide_a](rcm://quay/waypoints/guide_a)
- [quay · guide_b](rcm://quay/waypoints/guide_b)
- [quay · audio](rcm://quay/waypoints/audio)
- [quay · guide_walk](rcm://quay/paths/guide_walk)
- [quay · sequence1](rcm://quay/sequences/sequence1)
- [quay · intro](rcm://quay/conversations/intro)
- [quay · pact](rcm://quay/conversations/pact)
- [quay · guide](rcm://quay/conversations/guide)
- [quay · cleared](rcm://quay/conversations/cleared)
- [quay · cam1](rcm://quay/conversations/cam1)
- [quay · cam2](rcm://quay/conversations/cam2)
- [quay · cam3](rcm://quay/conversations/cam3)
- [quay · cam4](rcm://quay/conversations/cam4)
- [quay · cam5](rcm://quay/conversations/cam5)
- [quay · cam6](rcm://quay/conversations/cam6)
- [quay · cam7](rcm://quay/conversations/cam7)
- [quay · cam8](rcm://quay/conversations/cam8)
- [quay · cam9](rcm://quay/conversations/cam9)
- [quay · cam10](rcm://quay/conversations/cam10)
- [quay · cam11](rcm://quay/conversations/cam11)
- [quay · cam12](rcm://quay/conversations/cam12)
- [quay · cam13](rcm://quay/conversations/cam13)
- [quay · lab](rcm://quay/conversations/lab)
- [quay · anim](rcm://quay/conversations/anim)
- [quay · arrival](rcm://quay/events/arrival)
- [quay · new](rcm://quay/events/new)
- [quay · remember](rcm://quay/events/remember)
- [quay · accept](rcm://quay/events/accept)
- [quay · to_archive](rcm://quay/events/to_archive)
- [quay · cleared_trip](rcm://quay/events/cleared_trip)
- [quay · combat](rcm://quay/events/combat)
- [quay · combat_done](rcm://quay/events/combat_done)
- [quay · arrival_trigger](rcm://quay/events/arrival_trigger)
- [quay · end1](rcm://quay/events/end1)
- [quay · event1](rcm://quay/events/event1)
- [quay · cam_next1](rcm://quay/events/cam_next1)
- [quay · cam_next2](rcm://quay/events/cam_next2)
- [quay · cam_next3](rcm://quay/events/cam_next3)
- [quay · cam_next4](rcm://quay/events/cam_next4)
- [quay · cam_next5](rcm://quay/events/cam_next5)
- [quay · cam_next6](rcm://quay/events/cam_next6)
- [quay · cam_next7](rcm://quay/events/cam_next7)
- [quay · cam_next8](rcm://quay/events/cam_next8)
- [quay · cam_next9](rcm://quay/events/cam_next9)
- [quay · cam_next10](rcm://quay/events/cam_next10)
- [quay · cam_next11](rcm://quay/events/cam_next11)
- [quay · cam_next12](rcm://quay/events/cam_next12)
- [quay · guide_lab4](rcm://quay/events/guide_lab4)
- [quay · guide_lab5](rcm://quay/events/guide_lab5)
- [quay · guide_lab6](rcm://quay/events/guide_lab6)
- [quay · guide_lab7](rcm://quay/events/guide_lab7)
- [quay · cleared_lab4](rcm://quay/events/cleared_lab4)
- [quay · cleared_lab5](rcm://quay/events/cleared_lab5)
- [quay · cleared_lab6](rcm://quay/events/cleared_lab6)
- [quay · cleared_lab7](rcm://quay/events/cleared_lab7)
- [quay · controls1](rcm://quay/events/controls1)
- [quay · controls2](rcm://quay/events/controls2)
- [quay · controls3](rcm://quay/events/controls3)
- [quay · controls4](rcm://quay/events/controls4)
- [quay · controls5](rcm://quay/events/controls5)
- [quay · sample_taken](rcm://quay/events/sample_taken)
- [quay · talk_prop](rcm://quay/events/talk_prop)
- [quay · read_notice](rcm://quay/events/read_notice)
- [quay · notice_closed](rcm://quay/events/notice_closed)
- [quay · left_zone](rcm://quay/events/left_zone)
- [quay · clock](rcm://quay/events/clock)
- [quay · rat_killed](rcm://quay/events/rat_killed)
- [quay · state_lab](rcm://quay/events/state_lab)
- [archive · safe](rcm://archive/entries/safe)
- [archive · archivist](rcm://archive/actors/archivist)
- [archive · keeper](rcm://archive/actors/keeper)
- [archive · book](rcm://archive/objects/book)
- [archive · key](rcm://archive/objects/key)
- [archive · arrival_zone](rcm://archive/triggers/arrival_zone)
- [archive · sound](rcm://archive/waypoints/sound)
- [archive · keeper_a](rcm://archive/waypoints/keeper_a)
- [archive · keeper_b](rcm://archive/waypoints/keeper_b)
- [archive · keeper_walk](rcm://archive/paths/keeper_walk)
- [archive · two_shot](rcm://archive/sequences/two_shot)
- [archive · ledger](rcm://archive/conversations/ledger)
- [archive · back](rcm://archive/conversations/back)
- [archive · arrival](rcm://archive/events/arrival)
- [archive · peace](rcm://archive/events/peace)
- [archive · force](rcm://archive/events/force)
- [archive · to_return](rcm://archive/events/to_return)
- [archive · camera](rcm://archive/events/camera)
- [archive · arrival_trigger](rcm://archive/events/arrival_trigger)
- [return · safe](rcm://return/entries/safe)
- [return · witness](rcm://return/actors/witness)
- [return · courier](rcm://return/actors/courier)
- [return · arrival_zone](rcm://return/triggers/arrival_zone)
- [return · courier_a](rcm://return/waypoints/courier_a)
- [return · courier_b](rcm://return/waypoints/courier_b)
- [return · courier_walk](rcm://return/paths/courier_walk)
- [return · peace](rcm://return/conversations/peace)
- [return · force](rcm://return/conversations/force)
- [return · final](rcm://return/conversations/final)
- [return · back](rcm://return/conversations/back)
- [return · arrival](rcm://return/events/arrival)
- [return · peace](rcm://return/events/peace)
- [return · force](rcm://return/events/force)
- [return · final](rcm://return/events/final)
- [return · back](rcm://return/events/back)
- [return · finish_peace](rcm://return/events/finish_peace)
- [return · finish_force](rcm://return/events/finish_force)
- [return · arrival_trigger](rcm://return/events/arrival_trigger)

## Laboratorio opcional de dirección

Desde la Guía elige los laboratorios y después el Director de escenas. Viajas al club: pulsa Refugio, habla con Elena, mira u omite la llegada, vence a la rata y vuelve con ella. El regreso conserva el encargo principal. La zona utiliza el mismo compilador y acciones normales; su aceptación dentro del juego sigue pendiente en EMB01–24.

## Colocar al grupo y cambiar música

En el refugio opcional, selecciona la bienvenida de Elena → Puesta en escena: verás cuatro puntos con nombre que puedes mover en Espacio 3D. La película cambia London_Hub por DA_Boss_1 y devuelve la música anterior antes de terminar; al cancelar sólo restaura su propia instantánea. Son cues normales editables en Campaña → Secuencia. Formación, encuadre y guardado/carga requieren prueba en el juego.
