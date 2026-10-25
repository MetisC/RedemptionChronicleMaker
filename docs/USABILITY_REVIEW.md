# Usabilidad vigente del editor

Esta revisión se centra en encontrar contenido, elegir recursos, navegar sin
ratón, conservar el contexto y corregir errores de edición. Conserva los formatos, el tutorial aceptado y los contratos de runtime vigentes. No añade pestañas principales.

## Cambios aplicados

- El árbol del proyecto tiene búsqueda por nombre/ID con Ctrl+F, botón para
  limpiar y mensaje cuando no hay coincidencias. Intro selecciona un resultado.
  Filtrar sólo afecta al árbol; no cambia la visibilidad en el juego. Supr no
  elimina una selección que haya quedado oculta por la búsqueda.
- Los grupos plegados permanecen plegados al actualizar. Abrir otra crónica
  limpia las búsquedas para no ocultar accidentalmente su contenido.
- Ctrl+Shift+F busca en toda la crónica por contenido y escena, con detalles
  traducidos, recuento y navegación mediante Intro. Los flags abren su editor
  real; los elementos sencillos ya no muestran un segundo editor de ID
  incompatible en la vista global.
- El catálogo explica las listas vacías y ofrece restablecer filtros. Conserva
  el tipo de recurso y las restricciones del inventario. La selección sobrevive
  a una actualización si sigue siendo válida; nunca se confirma una fila vieja
  tras cambiar la búsqueda o el tipo de recurso.
- Intro en la búsqueda del catálogo lleva a los resultados; Intro sobre una fila
  la confirma. Aceptar, inspeccionar y marcar favorito requieren una selección
  válida para esa operación. Los proyectos recientes también se abren con Intro.
- Cambiar de elemento no descarta una propiedad pendiente incorrecta. Su campo
  permanece disponible para corregirlo. La selección de los árboles se restaura
  cuando la navegación no puede completarse.
- El acceso a encuentros dinámicos ocupa menos espacio y conserva el nombre
  completo en su ayuda. Las acciones sin selección de la vista global se
  desactivan. Los paneles vacíos explican cómo empezar.

## Comprobación y límites

`tests/test_usability.py` ejercita los recorridos con controles Qt reales y
teclado. `tools/editor_review_probe.py` comprueba ambos idiomas y conserva
capturas de búsqueda, catálogo y vista global a 1100×720 en
`build/tests/editor_review/`. El resto de la regresión sigue pasando por
`tools/quality.py`.

Estas comprobaciones son de interfaz sin OpenGL. No certifican navegación con
GPU física, todas las escalas de Windows ni comodidad en una sesión larga de
autoría. Las pruebas dentro de Redemption corresponden al usuario; estas pruebas
no ejecutan ni modifican la instalación real del juego. Evidencia de rc10: `research/authoring_completion/rc10_release.json`.

## Selección y edición espacial

- El selector muestra el modelo NOD con texturas originales antes de colocarlo; las flechas permiten verlo desde otros ángulos. Es una pose estática. La lectura y el render se hacen fuera del hilo de interfaz, con selección diferida, un trabajo activo por panel y rechazo de resultados obsoletos.
- Aceptar un actor mientras carga el escenario conserva la selección y activa la colocación al terminar. El mensaje explica que hay que hacer clic en el suelo. Esc, un fallo de carga o un cambio de proyecto/escena cancela la colocación pendiente.
- El giro es libre con ajuste angular 0; un valor mayor activa pasos de ese tamaño. Durante el arrastre se actualiza el modelo y los controles numéricos, sin serializar toda la crónica. Al soltar o perder el foco se registra una operación de deshacer y se reanuda la validación.
- El menú contextual del viewport y el árbol permite crear una conversación para actores/objetos propios. El actor queda vinculado directamente o por su evento de clic existente. Los objetos eligen el personaje que habla. Sustituir una nota, escena o viaje existente exige confirmación; las demás acciones se conservan. Las rutas condicionales existentes permanecen.
- La previsualización no ejecuta AI ni animaciones, no instancia entidades y no cambia archivos originales. Las superficies originales siguen usando su interacción al hacer clic; una vez creada, ese objeto propio admite el acceso contextual a conversación.


## Enlaces de autoría · rc10

El criterio de esta revisión es poder encadenar sistemas existentes desde su origen, sin exigir que el creador conozca filtros, callbacks ni números de RETURN. No introduce callbacks ficticios, nuevas pestañas principales ni cambios a la geometría. Los eventos generados siguen siendo datos normales, editables y deshacibles.

| Origen | Enlace disponible | Semántica y protección |
| --- | --- | --- |
| Respuesta RETURN | Acciones propias; volver hostil al hablante | Tras terminar y liberar el diálogo; cancelar no ejecuta efectos. GOTO conserva su contrato; la primera línea del nodo destino admite acciones. |
| Flag | Activación/desactivación y acceso a sus eventos | Transiciones booleanas observadas, no índice/valor ni condición continua. Conserva observación en save/restore. |
| Actor | Muerte; crear conversación desde propiedades o contexto | La muerte usa el muestreo existente. No sustituye una conversación por un callback de clic incompatible. |
| Objeto | Uso; posesión por el jugador si es un item | Las superficies/props no reciben opciones de pickup. El botón de conversación elige al hablante y abre inmediatamente el diálogo nuevo. |
| Zona | Entrada/salida | Sin flags elegidos arbitrariamente. Las regiones con script propio no ofrecen callbacks de RCM que ese script sustituye. |
| Conversación | Resultado final | Conserva filtros RETURN existentes y distingue varias rutas. La respuesta concreta tiene acciones propias. |
| Secuencia de planos/travelling | Finalización | Un plano simple sólo ajusta cámara; se explica cómo elegir un modo con evento final real. |
| Encuentro estático | Grupo derrotado | Conserva el muestreo de enemigos creados y muertos. No sustituye los encuentros existentes. |
| Encuentro dinámico, formato 10 | Inicio, inicio/final de oleada, final/parada | Conserva filtros de oleada/fase y sus callbacks reales. El asistente dinámico sigue disponible para salud del jefe y configuración del generador. |
| Misión | Activa, completa o paso activo | Condiciones `state_changed`, también evaluadas al entrar; no se anuncian como callbacks nativos de inicio/final. Pasos visibles desde 1, índices internos intactos. |
| Escena | Entrada y cierre de cualquier nota | Nota cerrada es global de la escena; no se promete identificar una nota concreta. |

### Flujo y consistencia

El selector ocupa una fila con Acciones y Ver evento; el resumen muestra los enlaces existentes. La ventana conserva acciones, filtros, condiciones y repetición. Las condiciones adicionales reutilizan el inspector ordinario y los grupos ALL/ANY/NOT. Las condiciones que identifican un estado de misión quedan vinculadas al origen. Reabrir sin cambios conserva incluso el orden original de las condiciones y no añade deshacer.

Si hay varias rutas, se elige un evento existente por ID, filtros y acciones. No se sobreescriben rutas vecinas. Borrar todas las acciones retira un evento sin usos; si otros elementos lo llaman, se remite al borrado normal con revisión de referencias. Cambiar un ID pendiente antes de abrir el acceso utiliza la identidad actual. Un cambio de documento durante una ventana no sobrescribe otro proyecto.

No se crean flags implícitos para una zona nueva. El botón de conversación del inspector de objetos usa el mismo flujo que el menú contextual; deja de escoger arbitrariamente la primera conversación existente. Se preservan los controles antiguos de documentos legacy y se muestra la autoría moderna sólo en formatos 9/10.

### Verificación y límites

`tests/test_linked_events.py` cubre creación y reutilización por origen, filtros/condiciones, cancelación, deshacer, borrado referenciado, cambio de ID pendiente, ventanas Qt reales, no-op, validación de drafts, formatos, compilación contra Codex y guardado/reapertura. `test_dialogue_effects.py` comprueba efectos RETURN, flags y AI; `test_text_commit.py` conserva el contrato de escritura diferida. La batería completa y el ejecutable empaquetado se verifican antes de publicar.

No se ejecuta Redemption automáticamente. Los casos DLGFX y QOL del checklist permanecen pendientes de observación nativa. No se equiparan los tests Qt/doubles, la compilación, el CI y una prueba real de juego, guardado o multijugador. El muestreo de flags/estados no garantiza observar un cambio transitorio que se deshaga antes del siguiente tick.

## Referencias con varios usos

El inspector, Buscar referencias y la revisión previa al borrado agrupan una relación repetida en una fila con su número de usos. Desplegarla muestra cada ubicación, por ejemplo el interlocutor general de una conversación y el hablante de una línea concreta. Cada uso permite navegar al registro editable; los textos completos también están en las ayudas emergentes. Las acciones usan sus nombres legibles en ambos idiomas.

Esta agrupación sólo afecta a la presentación: el grafo conserva todas las ubicaciones para renombrar y retirar referencias sin dejar usos ocultos. `tests/test_reference_view.py` comprueba ambas direcciones, navegación exacta, revisión de borrado, ausencia de cambios en los datos y traducciones.

Crear una conversación desde el botón o menú general con un actor seleccionado usa el mismo enlace que su menú contextual: se asigna en «Al hablar» y se abre el editor de diálogo. Elegir sólo el hablante de una conversación no constituye un enlace de interacción. Se conserva la creación de conversaciones sin asignar cuando no hay un actor seleccionado. La habilitación nativa depende del flag `THING_AF_TALKTO`, no de una lista de modelos humanos; la regresión incluye el actor original `alligator` y compilación contra Codex.

## Reanudar IA y cambiar hostilidad

`enable_ai` conserva su contrato: sólo retira `THING_AF_AIPAUSED`. El editor lo presenta como «IA / Reanudar (conserva bando)», explica el efecto y permite convertir esa acción al preset enemigo conservando el actor elegido. La nueva acción «Actor / Comportamiento hostil o neutral» comienza con el preset enemigo completo; las acciones avanzadas existentes no se reinterpretan. La conversión funciona en eventos y en los editores transaccionales de respuestas y reacciones a flags, y se puede deshacer.

`tests/test_ai_hostility.py` comprueba bando, neutralidad, pausa y conversación después del cierre del diálogo por respuesta, flag y ambas rutas, usando el actor original `alligator`. Conserva la semántica de reanudar, la AI original del recurso, la compilación contra Codex, las traducciones y el modo avanzado. Estas pruebas no sustituyen observar el combate dentro de Redemption.
