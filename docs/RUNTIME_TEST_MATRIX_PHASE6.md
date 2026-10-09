# Aceptación en Redemption · RCM System Test

Fuente `chronicles/system_test/project.yaml`, paquete `build/rcm_system/rcm_system.rcmpack`. **Cada casilla necesita observación en el juego.** El estado actualizado del intento está en `research/phase6/native_status.json`, si existe. No convertir resultados de doubles en PASS nativo.

Abrir exactamente el acceso `Vampire.exe - Acceso directo.lnk` del escritorio, con su carpeta y `-user RCM\east_demo`. Multiplayer → New Game → **RCM System Test**. Siempre partida nueva después de actualización estructural.

| Prueba | Resultado esperado | Estado actual |
|---|---|---|
| Chronicle/menu/título | RCM System Test y título legible de escena | NOT TESTED versión actual |
| Escenario y entorno | EastLondon, fondo gris original, sin halo | NOT TESTED actual; fondo aceptado históricamente |
| Victoria propia | Template T_rcm6_victoria y clase RCM6Actor | NOT TESTED |
| Witness/Guía | Hablar y volver al juego, repetir | NOT TESTED |
| Rechazar al primer diálogo | Cursor y HUD vuelven; próxima interacción disponible | NOT TESTED · B1 |
| Aceptar alianza / deshacerla | Flag cambia; conversación posterior refleja elección | NOT TESTED |
| Abortar conversación | Cámara y controles liberados, sin aplicar RETURN | NOT TESTED · B1 |
| Cámara de escena | Plano temporizado y liberación | NOT TESTED |
| Quests | Journal muestra títulos/pasos; sólo avance válido | NOT TESTED |
| Inventario | Libro recogible, entrega/quitar controlados | NOT TESTED |
| WestLondon | Viaje y regreso, Contact/Keeper interactivos | NOT TESTED |
| Encuentro | Guards creados una vez; combate y fin de grupo | NOT TESTED |
| Audio | Música y ambiente identificables, detener | NOT TESTED |
| Save/load durante recorrido | Restaurar actores/flags/objetos sin duplicar ni premiar dos veces | NOT TESTED · B2 |
| Save/load con conversación/cámara | Recuperar controles, no conservar conversación activa inválida | NOT TESTED · B2 |
| Reentrada y repetición | 3 ciclos de viaje, conversación y recarga | NOT TESTED |
| Host/client | Estado y callbacks coherentes en red | NOT TESTED · B5 |

Save/load: guardar antes de alianza; rechazar; recargar y aceptar; guardar con libro; cambiar mapa y recargar; completar quest; guardar/cargar y verificar que XP y objetos no se repitan. Registrar partida, revisión, acción y log; resultado PASS/FAIL/NOT TESTED por caso.

Prueba XYZ independiente: fuente `chronicles/editor_acceptance/project.yaml`; observar altura, posición y yaw, suelo y colisión. El viewport mide coordenadas reales pero no prueba la colisión del motor. Los triggers son muestreo en Java cada 150 ms y orientación yaw para cajas; probar borde, reentrada y `once`.

Copiar únicamente logs propios desde RCM al workspace como evidencia. No leer memoria ni inventar un inspector de estado en vivo. `runtime_trace.log` es observación de callbacks, no prueba por sí sola de HUD, cámara, audio o journal visible.
