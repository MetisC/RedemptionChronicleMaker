# Mapas y localizaciones del juego — investigación

CONFIRMADO EN SDK: NSC.htm describe por localización un NUI, un nombre de elemento dentro de ese NUI y flags. 0x8 muestra la localización; 0x10 la indica como refugio. Estos datos no son geometría del level.

CONFIRMADO EN ARCHIVOS ORIGINALES: Local_Eng.nob contiene ocho mapas NUI. Cada uno compone una imagen lógica de 640×480 en doce TGA de dimensiones potencia de dos. Los puntos son `element imagearray name=... size=16,16 flags=0x08 pos=X,Y`; nombres/posiciones y tiles están en map_catalogue.json. Hay un textbox `mapLocations` y un botón `MapCloseButton`. Londres oeste contiene mapClubTenebrae en (373,293). Cada NSC enlaza las escenas correspondientes con ese identificador.

CONFIRMADO EN EJECUTABLE: 0x410d89..0x410dc0 busca los controles de cierre/texto. 0x410e62..0x410e9e compara el nombre de cada imagearray con el map_label de las localizaciones y prueba SHOWINMAP. 0x4112bd..0x4112d2 resuelve el nombre del elemento mediante la tabla de strings y actualiza el texto al señalar. El mapa normal no implementa viaje al pulsar un destino; sus callbacks gestionan hover y cierre. No confundir mostrar una localización con teletransportarse a ella.

VIABILIDAD: podemos generar NUI propios con nombre separado, teselas TGA a partir de una imagen del autor y puntos con claves NLS propias. Se referenciarían desde el NSC generado; habría que ofrecer asignación escena/punto y visibilidad/refugio en UI, con rename/references/undo y empaquetado de la imagen propia. No hace falta Embrace ni cambiar un NIL. Las imágenes originales se reutilizan por referencia, no se redistribuyen. Un mapa personalizado no se obtiene al editar el level: es una ilustración 2D independiente.

ESTADO ACTUAL: implementado en chronicle_maps.py y editor/maps.py: importación
transaccional de imagen propia, puntos arrastrables, nombres/visible/refugio,
asignación de escenas, undo/referencias y empaquetado. Genera NUI/TGA/NLS/NSC.
La visibilidad usa las APIs Get/Set/ClearLocationFlags. No se ofrece viaje por
clic en el mapa. Las pruebas offline de formato/UI/paquete no certifican el
render nativo; COMP04 permanece pendiente del usuario.

El catálogo original ahora se obtiene de las referencias NSC y los NUI/TGA reales
mediante original_maps.py. El editor muestra la asociación del nivel activo por
defecto y permite elegir cualquier fondo original para un layout propio. Los
proyectos guardan `original: mapLondonEast.nui` en lugar de `source` de imagen;
ambos son excluyentes. Se genera NUI/NLS propio referenciando las teselas nativas,
sin redistribuir imágenes del juego. Exportar/importar conserva sólo esa referencia.
Las referencias MP `foobar.nui` no prueban una asociación de mapa: por ejemplo,
P1_INN4.nil se reutiliza en MossyHearth (Temesvar) e Inn4Stags (Praga). No se
deduce una ciudad a partir del NIL; el autor puede elegir el fondo explícitamente.
