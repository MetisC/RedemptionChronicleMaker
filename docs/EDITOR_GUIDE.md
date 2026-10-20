# Usar el editor

**Bienvenida:** crea, abre o vuelve a un proyecto reciente. Tutorial y Showcase son copias de trabajo: crear una copia limpia conserva la anterior.

Para borrar una crónica, selecciónala en **Proyectos recientes** y pulsa **Eliminar crónica…**, Supr o la misma opción del menú contextual. La confirmación muestra la ruta exacta: elimina definitivamente el proyecto local y su carpeta de recursos. Si abriste un YAML suelto, sólo elimina ese archivo y su recuperación automática. Las crónicas instaladas y partidas guardadas se conservan. **Quitar de recientes** sólo oculta la entrada, sin borrar archivos. No se pueden eliminar proyectos abiertos en otro editor ni los ejemplos originales del programa.

**Espacio 3D:** coloca entradas, NPC, objetos y zonas en el suelo. Inicio enfoca la entrada del jugador. F enfoca la selección. La geometría original no se modifica.

**Historia / Recursos:** selecciona un actor, conversación, nodo o respuesta y edita Propiedades. Los textos completos aparecen en tooltips. El buscador de recursos filtra tipo, familia y procedencia; puedes guardar favoritos.

**Campaña / Vista global:** crea escenas, viajes, recorridos, quests, encuentros y secuencias. Asistente… crea relaciones normales, editables y deshacibles. Editar asistente lee los valores actuales al reabrirlo.

**Encontrar elementos:** Ctrl+F filtra el árbol del proyecto por nombre o ID en la escena activa. Ctrl+Shift+F busca en toda la crónica, incluidas otras escenas y los textos de conversación. Intro abre el resultado seleccionado o el primero. La × borra la búsqueda. Al abrir otro proyecto se limpian estas búsquedas; los filtros nunca ocultan contenido dentro del juego. Los grupos del árbol que hayas plegado siguen plegados al actualizar.

**Elegir recursos:** escribe y pulsa Intro para ir a los resultados; pulsa Intro de nuevo para elegir. Sólo puedes confirmar una selección válida. Si no aparece nada, **Restablecer filtros** limpia búsqueda, familia, procedencia y favoritos, conservando el tipo de recurso y las restricciones del inventario. La selección se conserva al actualizar si el recurso sigue coincidiendo.

Una propiedad incorrecta permanece visible si intentas seleccionar otro elemento. Corrígela antes de continuar; la navegación no descarta el valor pendiente. Los proyectos recientes de la bienvenida también se abren con Intro.

**Gráfico:** muestra ramas y enlaces de conversación o el orden de un evento. Selecciona una tarjeta para editarla. Ajustar vista encuadra el gráfico.

**Eliminar:** selecciona el elemento y pulsa Supr o Eliminar. Sus acciones básicas de aparición se retiran juntas. Si hay referencias cruzadas, el diálogo muestra dónde se usa y qué se borraría: puedes ir directamente al uso, cancelar o elegir «Eliminar y quitar referencias». Los eventos vacíos también se retiran; los usos independientes y puntos alternativos se conservan. Todo el borrado se deshace en una sola operación.

**Prueba / Depuración:** el registro procede del juego; no sustituye la comprobación visual. Al terminar una prueba iniciada por RCM, el editor refresca el registro.

**Guardar:** conserva versiones de cambios previos. Versiones guardadas permite abrir una copia o restaurar con confirmación. Si el archivo cambió externamente, elige recargar, copiar o sobrescribir; sobrescribir no es la opción por defecto. No se permite editar el mismo proyecto en dos ventanas sin aviso.

El idioma se cambia únicamente en Herramientas → Configuración. La disposición deja oculto el panel inferior al abrir; errores, construcción y referencias lo muestran cuando hace falta. Campaña / Vista global reúne escenas y narrativa de toda la crónica.

**Puertas y objetos pulsables:** haz clic derecho sobre la puerta o el objeto visible en 3D y elige **Objeto original / crear paso…** o **Superficie / interacción al hacer clic…**. Escribe el texto que verá el jugador al señalarlo, por ejemplo «Entrada al club». Elige cualquier acción en la lista: viajar, conversar, mostrar una nota, ejecutar otro evento, cambiar flags, iniciar una secuencia o controlar un objeto. Los botones + y − añaden y quitan acciones. No se crea una zona de proximidad.

La interacción queda en **Objetos**, y su evento en **Eventos**. Selecciona el objeto y **Editar acciones al hacer clic…**; allí puedes cambiar las acciones y añadir condiciones, por ejemplo poseer una llave. «Una sola vez» es opcional; de forma predeterminada se puede pulsar de nuevo. **Evento / Ejecutar** llama a otro evento de esta escena; usa «Desde otro evento» para que no se dispare automáticamente. Las llamadas recursivas se rechazan.

Los viajes y enlaces no admiten la propia escena como destino. Si quieres otro layout del mismo mapa, crea **otra escena** que reutilice ese level y una entrada en ella. Si sólo existe una escena, puedes crear notas y otras interacciones, pero el selector de viajes no tendrá un destino válido.

Para ajustar una puerta, selecciona su acción **Escenario original / Objeto o puerta**: elige objeto, operación, frame y velocidad; en pivotes, duración y dirección. Frame 0/1 es el patrón de Door original, no una garantía para cualquier modelo. Ocultar es reversible; retirar no recrea el objeto. Desmarcar una referencia del árbol sólo cambia el visor. Los muros fijos del NIL no se pueden retirar como objetos. Esta función requiere comprobación en Redemption; no cambia el tutorial aceptado.

**Within The Darkness (opcional):** Herramientas → Configuración → **Importar contenido de mod «Within The Darkness»…**. Elige tu NOB desde cualquier carpeta. La importación copia un paquete filtrado al workspace y directamente a `RCM/rcm_wtd_content.nob` en el juego; necesitas cerrar Vampire para sustituir contenido. La ruta original ya no hace falta después. La importación se aplica al terminar, independientemente de Guardar/Cancelar las demás preferencias.

Tras importar, Historia / Recursos ofrece **Clanes disponibles**, **Disciplinas disponibles** y las plantillas/modelos admitidos. En un actor usa **Clan y disciplinas…** para su configuración inicial. En los eventos, **Actor / Cambiar clan** y **Actor / Establecer disciplina** permiten actuar sobre un NPC o el jugador, por ejemplo como recompensa; nivel 0 retira el nivel de esa disciplina. **Penthouse · Within The Darkness** aparece como level base, con geometría original y objetos estáticos. No se añade su campaña demo ni el reskin de menús. Sin importar, las nuevas categorías/acciones permanecen ocultas y el comportamiento previo se conserva.

Una vez instalado en RCM, el paquete se aplica a todos sus directorios de lanzamiento administrados, independientemente de la crónica elegida o de que el workspace actual tenga una importación para autoría. Arrancar sin RCM conserva el juego base. El motor no hereda las carpetas de usuario superiores, por lo que el despliegue mantiene automáticamente copias verificadas en los directorios de lanzamiento aislados de RCM. El build sigue registrando las dependencias explícitas. Los ZIP de distribución de la crónica y del programa no incluyen el contenido del mod; quien reciba el proyecto debe importarlo también. Sus derechos siguen perteneciendo a sus autores y la importación local no concede permisos adicionales de redistribución. La apariencia y el comportamiento en Redemption requieren las pruebas WTD del checklist.

**Elegir objetos directamente en 3D:** haz clic derecho sobre el objeto. El menú muestra su material/modelo y plantilla; «Objeto original / crear paso» abre el asistente con ese objeto elegido. La selección usa sus triángulos reales, respeta paredes delante y no requiere activar los marcadores de referencias. La lista conserva «Localizar en 3D» para enfocar una entrada sin modificar la crónica.

**Puertas decorativas de Tenebrae:** las dos del fondo pertenecen al NIL. El clic derecho identifica la superficie y añade un prop pulsable con su aspecto original sobre ella; no cambia el NIL ni retira la pared. La salida original usa `tracker_thing` + `ClickExit`. La capa nueva utiliza el mismo mecanismo nativo de hover/clic, pero acciones de RCM. No implica disponer de una animación de apertura en una puerta decorativa.

Las zonas y eventos creados por la versión anterior no se convierten automáticamente: elimina aquel trigger/evento con el borrado conjunto y vuelve a crear la interacción por clic. Si el enlace antiguo apunta a su propia escena, la validación impedirá construirlo. Reconstruye y despliega antes de probar. Hover, clic, resaltado, guardado y red de esta nueva capa están pendientes de comprobación en Redemption (CLICK01–08).

Campaña → Secuencias → Crear/editar travelling captura la vista 3D actual. Añade/reordena puntos y aplica; puedes seguir navegando con la ventana abierta. Las acciones temporales usan el inspector normal. Propiedades de línea ofrece Acciones al comenzar. Consulta CINEMATIC_DIRECTOR.md y el ejemplo de aceptación en Ayuda.
