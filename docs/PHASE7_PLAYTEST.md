# Prueba nativa de Fase 7

Fuente: `chronicles/phase7_demo/project.yaml`. Paquete: `build/rcm_stable/rcm_stable.rcmpack`. Nombre visible: **Londres: prueba de estabilización**. No usar saves de versiones previas. Esta guía describe resultados esperados; ninguno se declara observado por haber pasado los tests offline.

Abrir exactamente el acceso directo del escritorio ya utilizado por el usuario. En **Multiplayer → New Game**, seleccionar el nombre anterior. El despliegue de esta fase añade el NOB y sus clases dentro de `RCM/east_demo`, carpeta utilizada por ese acceso, con backup previo. La crónica `RCM System Test` permanece disponible.

1. Al aparecer en EastLondon, hablar con Victoria, Witness y Guía. Rechazar en la primera respuesta y repetir. Comprobar que cursor/HUD/cámara regresan y que el jugador vuelve a moverse.
2. Aceptar el pacto de Victoria; comprobar el diálogo posterior y el Journal. Probar las opciones de salida y las secuencias de cámara.
3. Recoger el libro del encargo y seguir sus condiciones de entrega. Verificar pasos y recompensa una sola vez.
4. Viajar al oeste mediante el diálogo. Hablar con Contact/Keeper y usar su regreso: ahora lleva a **Londres: el regreso**, otra escena sobre EastLondon. Su testigo debe mencionar el pacto si el flag sigue activo.
5. Con el testigo elegir regresar al inicio. Repetir el ciclo; comprobar actores, flags e inventario. La geometría del este se comparte; su contenido narrativo se define por separado.
6. Guardar/cargar antes y después de decisiones, libro, quest y viajes. Guardar también con cámara/conversación activa y comprobar recuperación. Probar tres ciclos y, por separado, host/client.
7. Comparar fondo gris del este con la referencia histórica. Los perfiles de las tres escenas son explícitos y conservan todos los bytes de entorno; la demo no añade skyboxes.

Registrar cada caso como PASS, FAIL o NOT TESTED con revisión, partida, acción y observación. Copiar sólo nuestros logs de RCM a `research/phase7/runtime/`. El log no sustituye la comprobación visual de cursor, HUD, cámara, Journal, sonido o colisión.

Los controles de fog/ZClip/EAX individuales, playerstarts nuevos, waypoints, luces y puertas no se ofrecen como funcionales en esta revisión. Están descritos en `EMBRACE_COMPARISON.md`. B1–B5 de `RELEASE_BLOCKERS.md` continúan abiertos hasta su evidencia correspondiente.
