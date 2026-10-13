# Las voces de Londres — mini crónica

Revisión 0.9.4: conserva el circuito y la llegada de la revisión anterior; recibe la corrección común de referencias AI a archivos y recuperación del spawn. Sus quests narrativas siguen iniciándose al aceptar el encargo de Victoria.

En el juego selecciona **Las voces de Londres · Mini crónica**, partida nueva. Hay dos geometrías (EastLondon y GunHaven) y tres escenas: muelle, archivo y regreso al muelle. El último layout reutiliza el primer mapa con otros personajes.

1. [Victoria](rcm://quay/actors/victoria), frente al inicio: acepta el encargo. También puedes rechazar y volver a hablar; recuerda el pacto.
2. [Guía](rcm://quay/actors/guide), a la izquierda: viaja al archivo. El combate es separado y opcional, **una rata básica**, sin punkis.
3. [Archivera](rcm://archive/actors/archivist): negocia o intimida. Recibes un libro y una llave; sólo una vez. La decisión afecta al diálogo final.
4. [Custodia](rcm://archive/actors/keeper): ofrece regreso cuando llevas libro y llave. La opción de cine lanza una cutscene de siete segundos con tres planos, movimiento de la custodia y trueno situado; devuelve el control.
5. [Testigo](rcm://return/actors/witness): recibe el libro, completa las dos quests y entrega el premio una vez. La mensajera vuelve al principio para probar reentrada.

## Examinar y modificar

- **Campaña / Quests** selecciona escenas, quests, encuentros y cámara. `+ Escena` crea nuevos layouts, incluyendo los que reutilizan un mapa.
- [Cámara del archivo](rcm://archive/sequences/two_shot) y [recorrido de custodia](rcm://archive/paths/keeper_walk) enseñan cómo combinar desplazamiento y cambio de planos.
- [Viaje al regreso](rcm://archive/events/to_return): ambas condiciones de inventario restringen la salida lógica.
- **Historia / Recursos** edita eventos, flags y diálogos; **Gráfico de historia** muestra decisiones; **Templates / AI propios** muestra los recursos de Victoria/libro y su Java.
- Usa el **Tutorial** para instrucciones detalladas de cada capacidad; esta crónica combina las funciones como una aventura corta.

## Prueba pendiente

Guardar/cargar antes y después de entregar; volver al comienzo; rechazar y abortar cada diálogo; comprobar suelo/collision y que no se duplican actores, objetos o premios. Las coordenadas tienen comprobación de malla y Java está compilado; eso no confirma comportamiento dentro del juego. Las cámaras nuevas y save/load necesitan esa prueba. Usa partidas nuevas con esta revisión; no hay migrador de saves anteriores.

No hay puertas físicas inventadas ni travelling propio exportado; esas funciones continúan pendientes. El combate opcional utiliza la plantilla original Rat, una sola por encuentro.


Revisión 0.9.3: Espacio 3D → Inicio selecciona y enfoca el punto de aparición. Las dos llegadas de EastLondon se trasladan a la calle del bobbie original con WalkCycleLawmen, tras el bloqueo observado en el tutorial que compartía el punto anterior. Inicia una partida nueva; la navegación de esta revisión aún requiere ensayo nativo.


Película de llegada: [Player](rcm://quay/sequences/sequence1) · [Trigger](rcm://quay/triggers/trigger1) · [Editar asistente](rcm://wizard/trigger_cinematic/trigger_cin1)
