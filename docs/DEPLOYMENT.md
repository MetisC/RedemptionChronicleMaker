# Probar y compartir

Pulsa F5 para guardar, validar, construir cuando haga falta, preparar y abrir tu crónica. Se usa una carpeta independiente dentro de RCM para cada aventura. No necesitas crear un acceso al juego. El directorio de trabajo del juego se configura al lanzarlo.

Los personajes multijugador pueden conservar objetos entre crónicas. Sus definiciones deben cargarse antes de elegir personaje. RCM añade una biblioteca de compatibilidad al preparar carpetas individuales o compartidas y la actualiza al terminar la prueba desde el editor. Conserva las definiciones propias verificadas; no edita el personaje. Un lanzamiento externo con el editor cerrado no permite detectar inmediatamente objetos recién recogidos: si una carpeta antigua falla al arrancar, cierra Vampire y usa `python tools/repair_profile_libraries.py --game "ruta de instalación"` desde el workspace. La herramienta sólo actualiza carpetas administradas dentro de RCM y guarda una copia de lo sustituido.

Para compartir: Paquetes → Exportar proyecto crea una copia editable con sus recursos propios; Crear paquete de crónica crea una aventura jugable después de construir. Instalar requiere revisar los archivos y cualquier código propio. Retirar sólo afecta archivos registrados sin modificar; tus partidas y archivos ajenos se conservan.

