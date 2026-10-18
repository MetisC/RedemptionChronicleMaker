# Usar el editor

**Bienvenida:** crea, abre o vuelve a un proyecto reciente. Tutorial y Showcase son copias de trabajo: crear una copia limpia conserva la anterior.

**Espacio 3D:** coloca entradas, NPC, objetos y zonas en el suelo. Inicio enfoca la entrada del jugador. F enfoca la selección. La geometría original no se modifica.

**Historia / Recursos:** selecciona un actor, conversación, nodo o respuesta y edita Propiedades. Los textos completos aparecen en tooltips. El buscador de recursos filtra tipo, familia y procedencia; puedes guardar favoritos.

**Campaña / Vista global:** crea escenas, viajes, recorridos, quests, encuentros y secuencias. Asistente… crea relaciones normales, editables y deshacibles. Editar asistente lee los valores actuales al reabrirlo.

**Gráfico:** muestra ramas y enlaces de conversación o el orden de un evento. Selecciona una tarjeta para editarla. Ajustar vista encuadra el gráfico.

**Eliminar:** selecciona el elemento y pulsa Supr o Eliminar. Sus acciones básicas de aparición se retiran juntas. Si hay referencias cruzadas, el diálogo muestra dónde se usa y qué se borraría: puedes ir directamente al uso, cancelar o elegir «Eliminar y quitar referencias». Los eventos vacíos también se retiran; los usos independientes y puntos alternativos se conservan. Todo el borrado se deshace en una sola operación.

**Prueba / Depuración:** el registro procede del juego; no sustituye la comprobación visual. Al terminar una prueba iniciada por RCM, el editor refresca el registro.

**Guardar:** conserva versiones de cambios previos. Versiones guardadas permite abrir una copia o restaurar con confirmación. Si el archivo cambió externamente, elige recargar, copiar o sobrescribir; sobrescribir no es la opción por defecto. No se permite editar el mismo proyecto en dos ventanas sin aviso.

El idioma se cambia únicamente en Herramientas → Configuración. La disposición deja oculto el panel inferior al abrir; errores, construcción y referencias lo muestran cuando hace falta. Campaña / Vista global reúne escenas y narrativa de toda la crónica.

**Puertas y objetos pulsables:** haz clic derecho sobre la puerta o el objeto visible en 3D y elige **Objeto original / crear paso…** o **Superficie / interacción al hacer clic…**. Escribe el texto que verá el jugador al señalarlo, por ejemplo «Entrada al club». Elige cualquier acción en la lista: viajar, conversar, mostrar una nota, ejecutar otro evento, cambiar flags, iniciar una secuencia o controlar un objeto. Los botones + y − añaden y quitan acciones. No se crea una zona de proximidad.

La interacción queda en **Objetos**, y su evento en **Eventos**. Selecciona el objeto y **Editar acciones al hacer clic…**; allí puedes cambiar las acciones y añadir condiciones, por ejemplo poseer una llave. «Una sola vez» es opcional; de forma predeterminada se puede pulsar de nuevo. **Evento / Ejecutar** llama a otro evento de esta escena; usa «Desde otro evento» para que no se dispare automáticamente. Las llamadas recursivas se rechazan.

Los viajes y enlaces no admiten la propia escena como destino. Si quieres otro layout del mismo mapa, crea **otra escena** que reutilice ese level y una entrada en ella. Si sólo existe una escena, puedes crear notas y otras interacciones, pero el selector de viajes no tendrá un destino válido.

Para ajustar una puerta, selecciona su acción **Escenario original / Objeto o puerta**: elige objeto, operación, frame y velocidad; en pivotes, duración y dirección. Frame 0/1 es el patrón de Door original, no una garantía para cualquier modelo. Ocultar es reversible; retirar no recrea el objeto. Desmarcar una referencia del árbol sólo cambia el visor. Los muros fijos del NIL no se pueden retirar como objetos. Esta función requiere comprobación en Redemption; no cambia el tutorial aceptado.

**Within The Darkness (opcional):** Herramientas → Configuración → **Importar contenido de mod «Within The Darkness»…**. Elige tu NOB desde cualquier carpeta. La importación copia un paquete filtrado al workspace y a `RCM/_content/within_the_darkness` en el juego; necesitas cerrar Vampire para sustituir contenido. La ruta original ya no hace falta después. La importación se aplica al terminar, independientemente de Guardar/Cancelar las demás preferencias.

Tras importar, Historia / Recursos ofrece **Clanes disponibles**, **Disciplinas disponibles** y las plantillas/modelos admitidos. En un actor usa **Clan y disciplinas…** para su configuración inicial. En los eventos, **Actor / Cambiar clan** y **Actor / Establecer disciplina** permiten actuar sobre un NPC o el jugador, por ejemplo como recompensa; nivel 0 retira el nivel de esa disciplina. **Penthouse · Within The Darkness** aparece como level base, con geometría original y objetos estáticos. No se añade su campaña demo ni el reskin de menús. Sin importar, las nuevas categorías/acciones permanecen ocultas y el comportamiento previo se conserva.

El build conserva la dependencia y el despliegue copia el paquete local a la carpeta de la crónica en RCM. Los ZIP de distribución de la crónica y del programa no incluyen el contenido del mod; quien reciba el proyecto debe importarlo también. Sus derechos siguen perteneciendo a sus autores y la importación local no concede permisos adicionales de redistribución. La apariencia y el comportamiento en Redemption requieren las pruebas WTD del checklist.

**Elegir objetos directamente en 3D:** haz clic derecho sobre el objeto. El menú muestra su material/modelo y plantilla; «Objeto original / crear paso» abre el asistente con ese objeto elegido. La selección usa sus triángulos reales, respeta paredes delante y no requiere activar los marcadores de referencias. La lista conserva «Localizar en 3D» para enfocar una entrada sin modificar la crónica.

**Puertas decorativas de Tenebrae:** las dos del fondo pertenecen al NIL. El clic derecho identifica la superficie y añade un prop pulsable con su aspecto original sobre ella; no cambia el NIL ni retira la pared. La salida original usa `tracker_thing` + `ClickExit`. La capa nueva utiliza el mismo mecanismo nativo de hover/clic, pero acciones de RCM. No implica disponer de una animación de apertura en una puerta decorativa.

Las zonas y eventos creados por la versión anterior no se convierten automáticamente: elimina aquel trigger/evento con el borrado conjunto y vuelve a crear la interacción por clic. Si el enlace antiguo apunta a su propia escena, la validación impedirá construirlo. Reconstruye y despliega antes de probar. Hover, clic, resaltado, guardado y red de esta nueva capa están pendientes de comprobación en Redemption (CLICK01–08).
