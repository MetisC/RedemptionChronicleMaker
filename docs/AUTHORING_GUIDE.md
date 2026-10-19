# Crear tu aventura

Empieza con el level, una entrada y un NPC. **Campaña → Asistente…** ofrece diez tareas: NPC que habla; NPC te manda a un lugar; trigger con acciones; trigger cinematográfico; objeto recogible; quest; encuentro; viaje con entrada; nota/carta; objeto que inicia conversación.

Los asistentes crean elementos normales. **Crónica → Editar asistente** vuelve a abrir una configuración guardada. Lee sus textos, posiciones y planos actuales, incluidos los cambios hechos en Propiedades. No conserva copias paralelas. Cancelar no modifica; Aplicar se puede deshacer. Si falta una referencia, el asistente informa **Configuración incompleta**: reparar explícitamente, elegir otro recurso o desvincularlo conservando la aventura.

En **NPC te manda a un lugar**, la primera respuesta debe terminar con RETURN 1 para armar su trigger. Los eventos answer/event/end y sus flags están en el proyecto, no en un runtime separado. La segunda respuesta no lo arma. Modifica las ramas más complejas en Historia o en el gráfico; el asistente edita la primera línea y las dos respuestas de entrada sin borrar el resto.

**Trigger con acciones** permite varias acciones frecuentes, ordenadas como se muestran, condiciones y once. Para lógica compuesta o acciones avanzadas usa Eventos / Propiedades. El wizard conserva condiciones complejas cuando no cambias el selector sencillo. Las condiciones se comprueban al entrar, no continuamente mientras permaneces dentro.

**Cámara:** la conversación usa hombro por defecto. Las secuencias preguntan Plano / Secuencia de planos / Travelling original. Player se permite como sujeto de una secuencia de planos. Una referencia NPC orienta su línea de acción; evita referencias demasiado cercanas o lejanas. Los presets usan constantes reales. Ajusta tiempos, transición y ángulos en la ficha. Cambiar tipo avisa y permite deshacer. NCP reproduce originales y genera rutas lineales o temporizadas propias desde el Director.

**Quest:** un título, descripción, pasos y XP. Eventos Iniciar / Avanzar / Completar controlan su journal. Completar exige todos los pasos. **Encuentro:** el asistente crea una Rat básica y un grupo; modifica sus enemigos y su evento de aparición con los paneles normales. Se entrega el premio cuando todos están muertos. Para retrasar el spawn, cambia su evento a Objeto en inventario o Flag con condición.

**Viaje:** crea la escena destino antes. El asistente coloca una entrada allí y un trigger de viaje aquí. Cambiar destino conserva la entrada anterior y crea otra, sin borrados ocultos. En el destino, su llegada sólo mueve al jugador al entrar; cargar conserva el pose guardado.

**Notas:** usa un objeto interactuable; su evento Mostrar nota genera NTX y ejecuta el cuadro nativo. La conversación de un objeto necesita un hablante real colocado en escena. Tras la nota usa Cuando cierran una nota para continuar con cámara, conversación o viaje; no mezcles dos ventanas modales en el mismo evento.

**Once y guardado:** los checkpoints previenen repeticiones lógicas y premios duplicados en los doubles. No hay transacción atómica entre un efecto nativo y su checkpoint. Prueba guardar/cargar alrededor de los efectos en Redemption. No cambies IDs/estructura de una partida en curso; comprueba el aviso de partida nueva del Build.

**Probar en Redemption (F5):** guarda y valida, construye sólo si hay cambios, prepara tu carpeta de crónica y abre el juego. Cierra Redemption antes de actualizar. Las funciones separadas de construcción y diagnóstico siguen disponibles.

Abre chronicles/mini_chronicle/project.yaml para ver una aventura completa de ejemplo, editable con los mismos paneles y asistentes.

**Encuentros dinámicos:** Campaña → + Encuentro dinámico…, Asistentes o botón derecho sobre suelo 3D. Elige Emboscada/Oleadas/Continuo/Refuerzos/Jefe, enemigos/cantidad, puntos/cuándo y acciones finales. Advanced queda plegado. [Guía y laboratorio](DYNAMIC_ENCOUNTERS.md). El primer uso en formato 9 guarda backup y opta por formato 10; abrir el tutorial no lo convierte.


## Propiedades avanzadas del escenario y de sus objetos

En **Level base > Entorno de escena** puedes heredar o elegir audio, volumen,
niebla, distancia visible y cielo. Las unidades son las del motor. EAX conserva
la escena original salvo override room_type mediante el comando nativo roomtype. No se modifican geometría ni lightmaps.

En un actor u objeto, **Propiedades de esta instancia** cambia AI/Foley,
animaciones compatibles y texto al señalar sólo para ese elemento. Los
contenedores ofrecen botín heredado, ninguno o una clase del GAME.NTT original.

**Script nativo · avanzado** permite elegir una clase original, rellenar
parámetros y seleccionar entidades por nombre. Frames nativos usa la posición
inicial como frame 0 y waypoints como destinos. El script posee los callbacks;
no mezcles esa misma entidad con creación dinámica, inventarios o conversaciones
RCM. Algunos scripts requieren regiones/datos de la campaña original.

Un waypoint puede ser además punto de interés nativo, grupo 0..9. La AI debe
estar activa y tener el mismo interestNum; esto no crea un recorrido.

En Ajustes, **Importar biblioteca de plantillas**, selecciona un NOT o NOB y
las plantillas nuevas. Se importan sus padres y datos necesarios, no menús,
crónicas ni código. Los archivos importados permanecen como dependencia local;
los ZIP de exportación no incluyen recursos ajenos. Un recurso con código
externo obligatorio se rechaza claramente. No es un importador universal de mods.

El ejemplo opcional **Cargo at the refuge** muestra estas propiedades sin cambiar
el tutorial. Los nuevos comportamientos nativos necesitan las pruebas EMB de la
lista manual. Mapas y localizaciones está disponible en las propiedades de la crónica y Campaña → Añadir…. Véase AUTHORING_COMPLETION.md.
Consulta Límites avanzados y la lista de comprobaciones manuales.


## Dificultad de combate de la crónica

Selecciona la crónica en el árbol y elige Fácil, Normal, Difícil o Pesadilla en
Propiedades. Normal conserva el comportamiento original. El ajuste es opcional;
las crónicas antiguas siguen en Normal y no cambian de formato.

| Ajuste | Vida y máximo | Fuerza | Resistencia |
|---|---|---|---|
| Fácil | ×0,80 | ×0,90 | ×0,90 |
| Normal | ×1 | ×1 | ×1 |
| Difícil | ×1,20 | ×1,10 | ×1,10 |
| Pesadilla | ×1,50 | ×1,20 | ×1,20 |

Fuerza y Resistencia modifican los atributos nativos, no multiplican directamente
cada golpe. El motor conserva sus límites de clan y resistencias. Se aplica a
nuevos enemigos RCM declarados enemigos, incluidos oleadas y jefes; respeta equipos
aliados/neutrales. No altera al jugador ni a personajes de conversación normales.
En encuentros dinámicos se aplica primero la vida personalizada y después la
dificultad. Los umbrales porcentuales usan el máximo resultante; los absolutos no
cambian. Los enemigos de una partida guardada conservan sus valores. Para cambiar
la dificultad de forma uniforme, empieza una partida nueva después del build.

En Ajustes > Bibliotecas importadas puedes retirar una biblioteca. Se comprueban
las referencias de la crónica abierta y de otras bibliotecas. Sólo se eliminan
copias locales verificadas; se conserva el mod original y lo instalado en el
juego. Otros proyectos pueden necesitar que la importes otra vez. La
compatibilidad de inventarios conserva bibliotecas completas y sus dependencias.
Los actores controlados por scripts nativos conservan su inicialización original;
la dificultad afecta a nuevas creaciones del runtime RCM, no a actores originales.
