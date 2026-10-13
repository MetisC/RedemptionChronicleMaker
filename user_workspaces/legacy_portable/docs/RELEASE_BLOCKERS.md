# Release blockers

**Beta privada lista: NO, hasta completar la aceptación nativa actual.** Esta lista no se vacía artificialmente porque pase unittest.

| Bloqueo | Criterio de cierre |
|---|---|
| B1 · CRITICAL · Diálogo/UI/cámara | En partida nueva: aceptar, rechazar primera respuesta, abortar, reabrir; cámara y cursor/UI recuperados en todos los casos. Corregido offline, pendiente en Redemption. |
| B2 · CRITICAL · Persistencia | Guardar/cargar antes y después de decisiones, inventario, quest y transición; GUIDs coherentes, sin duplicados ni recompensas repetidas. Firma capture contrastada; comportamiento nativo pendiente. |
| B3 · HIGH · NOT/AI propios | Template propio e item instanciados y utilizables; herencia/modelo/script/AI comprobados en motor. Reader lossless y writer parcial no equivalen a estabilidad runtime. |
| B4 · HIGH · Distribución limpia | Portable probado en equipo/VM sin Python/JDK globales, otra ruta y permisos normales. El ensayo local con workspace nuevo/PATH restringido no sustituye esa máquina. |
| B5 · HIGH · Red y repetición | Host/client, reentrada de mapa y ciclos repetidos sin actor duplicado ni UI bloqueada. No hay aceptación de red. |

Actualización 0.9.0: entradas/waypoints/recorridos y controles restringidos de puertas/exits se han implementado, compilado y probado offline. Su ejecución nativa sigue pendiente. AI completa, árbol de comportamiento, selección de estática y cámara desde vista/timeline completa siguen abiertos. La beta debe declarar el subconjunto real.

El usuario aplazó las pruebas nativas y autorizó continuar la implementación. B1–B4 siguen abiertos; B5 impide anunciar red y no bloquea por sí solo una futura beta explícitamente local. No se declara beta aceptada en esta entrega. El circuito sustituye las demos desplegadas; [matriz actual](RUNTIME_TEST_MATRIX.md) y [auditoría de madurez](AUTHORING_MATURITY_REPORT.md).

Antes de invitar usuarios: quality PASS, regresión de fuentes PASS, originales intactos, portable y paquete auditados, bugs CRITICAL nativos cerrados con evidencia, guía de primera ejecución ensayada. Publicación externa adicional requiere cerrar inventario/licencia propia y revisión de redistribución de dependencias; no se ha publicado nada.
