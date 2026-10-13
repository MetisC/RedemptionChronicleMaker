# Prueba manual · 1.0.0-rc4

**MANUAL RUNTIME TEST REQUIRED.** RCM no automatiza Redemption. La historia del tutorial ya fue aceptada; esta lista comprueba el nuevo producto.

1. **SETUP01/02:** descomprime el ZIP de usuario en otra carpeta. Abre el EXE, selecciona Vampire.exe y comprueba la bienvenida y tus proyectos fuera del programa.
2. **PLAY01/TUTOR01:** abre Tutorial rápido y pulsa F5. En Multiplayer → LAN → New Game elige Una carta al amanecer; completa el encargo. Si el personaje llevaba objetos RCM de antes, comprueba especialmente que LAN abre sin error.
3. **SHOW01–04:** abre Showcase completo y pulsa F5. Prueba diálogo/cámaras, nota/objeto, libro/llave/diario y una zona de activación. Las estaciones se pueden cerrar u omitir.
4. **SHOW02/05–08:** prueba la película, animaciones, recorrido, rata básica, sonido y viaje al archivo/regreso. Anota cualquier posición, encuadre o colisión incorrectos.
5. **SHOW09:** guarda/carga antes y después de recoger, completar y viajar. Vuelve a las escenas: sin premios, actores u objetos duplicados, y sin cámara/UI atrapadas.
6. **PLAY02:** cambia una frase en el editor, guarda y pulsa F5 con el juego cerrado. Comprueba la frase nueva y repite F5 sin cambios; no debería reconstruir.

Pendiente adicional: portable en un PC/VM independiente y revisión visual a 100/125/150/200%. No se afirma esa aceptación por las pruebas de este equipo.

## Encuentros dinámicos · DYN01–12

Abre chronicles/dynamic_lab/project.yaml, guarda y pulsa F5 con el juego cerrado. En LAN → New Game elige **RCM · Dynamic Encounter Lab**. Usa una partida nueva. Anota PASS/FAIL y conserva el trace; todos están pendientes de observación nativa.

| Caso | Prueba y resultado esperado |
|---|---|
| DYN01 | Anezka → preparar oleadas → barril. Entrar en su zona crea tres ratas. Sin aceptar no empieza. |
| DYN02 | Mata las tres; tras dos segundos aparecen dos. No avanza si queda una viva. |
| DYN03 | Inicia el continuo desde Anezka: una cada cinco segundos, máximo tres vivas. Mata una y comprueba reposición. |
| DYN04 | Detén el continuo: no aparecen más; las vivas permanecen. Prueba también pausa/reanudación. |
| DYN05 | Tras las oleadas aparece la rata jefe. Cruza 50%: dos refuerzos, una vez. Evita matarla de un golpe. |
| DYN06 | Cruza 25%: sonido espacial una vez, sin repetir por seguir por debajo. |
| DYN07 | Mata al jefe: termina encuentro/quest y se detienen refuerzos/continuo. Sin repetir premio. |
| DYN08 | Guarda con dos ratas vivas a mitad de oleada y carga: conserva grupo/cantidades, sin duplicar. |
| DYN09 | Guarda tras 50%, carga y espera: no duplica refuerzos. Comprueba 25%, muerte, carga y premio. |
| DYN10 | En copia del Showcase activa estación opcional, viaja/regresa activo y completo. Prueba Una vez/Continuar; después pruebas independientes de Reiniciar al volver/Cooldown. Roster perdido debe detener con error, jamás duplicar. Anota si el motor conserva/restaura records entre instancias. |
| DYN11 | En copia cambia cantidad/plantilla en el asistente, guarda/F5 y empieza nueva partida si cambia contrato. Comprueba edición/undo/reabrir. |
| DYN12 | En copia usa puntos incompatibles que el motor realmente rechace, con pocos intentos. Reintento/rotación acotados, traza GENERATOR_SPAWN_FAILED/ERROR y juego respondiendo. Coordenada mala no garantiza fallo de factory: sin reproducir rechazo marca PENDIENTE, no PASS. |

El laboratorio no certifica colisión/pathfinding. Enemigos normales Rat original; sólo boss x10 vida para ver umbrales. Showcase conserva encargo principal y ofrece laboratorio desde la Guía. Tutorial rápido no añade encuentros.
