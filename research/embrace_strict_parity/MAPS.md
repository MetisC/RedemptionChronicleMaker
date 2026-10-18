# Mapas y localizaciones del juego — investigación

CONFIRMADO EN SDK: NSC.htm describe por localización un NUI, un nombre de elemento dentro de ese NUI y flags. 0x8 muestra la localización; 0x10 la indica como refugio. Estos datos no son geometría del level.

CONFIRMADO EN ARCHIVOS ORIGINALES: Local_Eng.nob contiene ocho mapas NUI. Cada uno compone una imagen lógica de 640×480 en doce TGA de dimensiones potencia de dos. Los puntos son `element imagearray name=... size=16,16 flags=0x08 pos=X,Y`; nombres/posiciones y tiles están en map_catalogue.json. Hay un textbox `mapLocations` y un botón `MapCloseButton`. Londres oeste contiene mapClubTenebrae en (373,293). Cada NSC enlaza las escenas correspondientes con ese identificador.

CONFIRMADO EN EJECUTABLE: 0x410d89..0x410dc0 busca los controles de cierre/texto. 0x410e62..0x410e9e compara el nombre de cada imagearray con el map_label de las localizaciones y prueba SHOWINMAP. 0x4112bd..0x4112d2 resuelve el nombre del elemento mediante la tabla de strings y actualiza el texto al señalar. El mapa normal no implementa viaje al pulsar un destino; sus callbacks gestionan hover y cierre. No confundir mostrar una localización con teletransportarse a ella.

VIABILIDAD: podemos generar NUI propios con nombre separado, teselas TGA a partir de una imagen del autor y puntos con claves NLS propias. Se referenciarían desde el NSC generado; habría que ofrecer asignación escena/punto y visibilidad/refugio en UI, con rename/references/undo y empaquetado de la imagen propia. No hace falta Embrace ni cambiar un NIL. Las imágenes originales se reutilizan por referencia, no se redistribuyen. Un mapa personalizado no se obtiene al editar el level: es una ilustración 2D independiente.

ESTADO ACTUAL: RCM hereda map_ui/map_label del level original y no tiene todavía un editor normal de mapas/localizaciones. El análisis demuestra una ruta de implementación; no se presenta como función ya implementada o probada dentro del juego. El texto del adjunto principal se audita aparte. Un eventual viaje desde el mapa sería comportamiento adicional y no se promete por conservar el mapa original.

API CONFIRMADA: CodexSequence.GetLocationFlags(String), SetLocationFlags(String,int)
y ClearLocationFlags(String,int) permiten cambiar descubrimiento/visibilidad
(flags SHOWINMAP=8/HAVEN=16) en ejecución. API_SIGNATURES.txt contiene sus firmas.
El generador actual elimina SHOWINMAP del NSC generado: conservar una imagen no
equivale a ofrecer edición de puntos o descubrimiento. Esta función sigue siendo
una propuesta demostrada técnicamente, no una interfaz implementada.
