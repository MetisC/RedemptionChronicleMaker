# Objetos e inventario

Resource Browser → Objetos reutiliza las familias originales items, weapons y armour para inventario; props siguen siendo objetos de escenario y no pueden añadirse a inventario. El selector consulta la familia del catálogo automáticamente. Los modelos y transforms siguen usando el viewport de Fase 3.

Actor → Editar inventario inicial: seleccionar objetos ya declarados en esa escena. Cada objeto debe tener un único propietario de creación: inventario, spawn directo o grupo. Desactivar su spawn inicial antes de incluirlo en inventario. No se exponen slots, equipo o belt cuya semántica no está implementada.

Acciones: Dar al jugador, Quitar del jugador, Crear entidad, Retirar entidad y XP. AddToActorInventory, GetActorFirstInventoryItem, GetNextInventoryItem, RemoveItemFromInventory y Remove son firmas originales. Dar reutiliza una instancia de mundo si existe, o la crea junto al destinatario. Inventarios creados reciben flags SAVEALWAYS. La búsqueda está acotada a 4096 enlaces.

Para Quitar o Tiene objeto se puede elegir un objeto de otro mapa: el selector muestra `west / Libro de Victoria`; el fuente conserva `west.book`. Es una referencia de autoría que el compilador traduce al nombre real de plantilla, sin pedir GUID. Rename de objeto/escena actualiza esas referencias. Dar/crear siguen trabajando con entidades de la escena actual.

Picked Up significa que el objeto aparece en el inventario del jugador local muestreado por el controlador. No se inventa un callback de pickup: se detecta cada 0,15 s; se dispara una vez por evento por defecto. Con Cada vez detecta nuevas transiciones de ausencia a presencia. No cubre todos los destinatarios ni todos los jugadores de red.

Quest Item es una clasificación de autoría y validación; no añade inmunidad a vender, soltar o destruir ni estadísticas nuevas. La demo comprueba que el jugador conserve el libro al entregar la quest y después lo retira.

Pruebas locales cubren validación, referencias entre mapas, generación, inventario inicial y escenarios de pickup. Pickup, traslado de inventario entre ubicaciones, iconos y guardado nativo necesitan ensayo en Redemption.
