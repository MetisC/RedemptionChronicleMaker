# Crear tu aventura

Empieza con el level, una entrada y un NPC. **Campaña → Asistente…** ofrece diez tareas: NPC que habla; NPC te manda a un lugar; trigger con acciones; trigger cinematográfico; objeto recogible; quest; encuentro; viaje con entrada; nota/carta; objeto que inicia conversación.

Los asistentes crean elementos normales. **Crónica → Editar asistente** vuelve a abrir una configuración guardada. Lee sus textos, posiciones y planos actuales, incluidos los cambios hechos en Propiedades. No conserva copias paralelas. Cancelar no modifica; Aplicar se puede deshacer. Si falta una referencia, el asistente informa **Configuración incompleta**: reparar explícitamente, elegir otro recurso o desvincularlo conservando la aventura.

En **NPC te manda a un lugar**, la primera respuesta debe terminar con RETURN 1 para armar su trigger. Los eventos answer/event/end y sus flags están en el proyecto, no en un runtime separado. La segunda respuesta no lo arma. Modifica las ramas más complejas en Historia o en el gráfico; el asistente edita la primera línea y las dos respuestas de entrada sin borrar el resto.

**Trigger con acciones** permite varias acciones frecuentes, ordenadas como se muestran, condiciones y once. Para lógica compuesta o acciones avanzadas usa Eventos / Propiedades. El wizard conserva condiciones complejas cuando no cambias el selector sencillo. Las condiciones se comprueban al entrar, no continuamente mientras permaneces dentro.

**Cámara:** la conversación usa hombro por defecto. Las secuencias preguntan Plano / Secuencia de planos / Travelling original. Player se permite como sujeto de una secuencia de planos. Una referencia NPC orienta su línea de acción; evita referencias demasiado cercanas o lejanas. Los presets usan constantes reales. Ajusta tiempos, transición y ángulos en la ficha. Cambiar tipo avisa y permite deshacer. NCP reutiliza recursos originales; no hay writer.

**Quest:** un título, descripción, pasos y XP. Eventos Iniciar / Avanzar / Completar controlan su journal. Completar exige todos los pasos. **Encuentro:** el asistente crea una Rat básica y un grupo; modifica sus enemigos y su evento de aparición con los paneles normales. Se entrega el premio cuando todos están muertos. Para retrasar el spawn, cambia su evento a Objeto en inventario o Flag con condición.

**Viaje:** crea la escena destino antes. El asistente coloca una entrada allí y un trigger de viaje aquí. Cambiar destino conserva la entrada anterior y crea otra, sin borrados ocultos. En el destino, su llegada sólo mueve al jugador al entrar; cargar conserva el pose guardado.

**Notas:** usa un objeto interactuable; su evento Mostrar nota genera NTX y ejecuta el cuadro nativo. La conversación de un objeto necesita un hablante real colocado en escena. Tras la nota usa Cuando cierran una nota para continuar con cámara, conversación o viaje; no mezcles dos ventanas modales en el mismo evento.

**Once y guardado:** los checkpoints previenen repeticiones lógicas y premios duplicados en los doubles. No hay transacción atómica entre un efecto nativo y su checkpoint. Prueba guardar/cargar alrededor de los efectos en Redemption. No cambies IDs/estructura de una partida en curso; comprueba el aviso de partida nueva del Build.

**Probar en Redemption (F5):** guarda y valida, construye sólo si hay cambios, prepara tu carpeta de crónica y abre el juego. Cierra Redemption antes de actualizar. Las funciones separadas de construcción y diagnóstico siguen disponibles.

Abre chronicles/mini_chronicle/project.yaml para ver una aventura completa de ejemplo, editable con los mismos paneles y asistentes.
