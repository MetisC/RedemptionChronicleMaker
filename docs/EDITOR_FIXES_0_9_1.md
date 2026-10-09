# Correcciones del editor · 0.9.1

Incidencias comunicadas por el usuario el 8 de octubre de 2026, con seis capturas de su primera sesión real del editor. Esta revisión modifica la experiencia de autoría, sin cambiar el runtime de la crónica ni abrir Redemption.

## Cambios

- **Ratón:** mover a la derecha con botón derecho gira a la derecha; mirar arriba conserva el sentido vertical habitual. El cálculo de cámara usa una base ortonormal explícita para evitar la pérdida de precisión de `lookAt(pos, pos + forward)` cerca de la vertical. La órbita mantiene distancia y limita su elevación. Los eventos generados al recentrar el cursor no se cuentan como movimiento.
- **Colores:** fondo, texto, filas alternas, selección y controles usan una paleta consistente clara u oscura. Las tarjetas y respuestas del gráfico tienen un color de texto explícito y contrastado. Se retiró el fondo alterno blanco fijo que hacía ilegible el texto blanco.
- **Pestañas:** título, explicación y botones específicos de Historia ahora pertenecen a esa página. La barra de modos conserva su posición al cambiar de pestaña o de selección.
- **Añadir actor:** todas las entradas de «+ Actor» piden una plantilla del catálogo. Cancelar no crea contenido. En Espacio 3D, tras elegir plantilla se coloca con clic sobre suelo.
- **Eliminar:** Supr funciona con foco en viewport, árbol de proyecto, lista de contenido y lista de campaña; también hay botón Eliminar en Espacio 3D. Siempre pide confirmación. No interfiere con Supr mientras editas un campo de texto.
- **Referencias de aparición:** borrar un actor/objeto retira sus acciones `spawn` y los eventos de inicio que queden vacíos, dentro del mismo paso de Deshacer. Las dependencias narrativas reales —speaker, quest, recorrido, trigger utilizado— siguen protegidas y requieren reasignación previa.

## Actualización y recuperación

El ejecutable permanece en `build/portable/RedemptionChronicleMaker/RedemptionChronicleMaker.exe`. La actualización se construye aparte y reemplaza únicamente componentes de la distribución con el editor cerrado. Se conserva íntegro su `workspace/`, incluidos proyectos guardados, catálogos y preferencias. Los componentes anteriores quedan en `build/portable_backups/`; el inventario de comprobación está en `research/phase9/editor_fixes/portable_update.json`.

Si guardaste un «Nuevo personaje» con plantilla vacía, selecciónalo y pulsa Supr o Eliminar: ahora puede retirarse junto con su aparición automática. No se reescribe tu proyecto para ocultar el problema.

## Comprobación

`tests/test_editor_fixes.py` cubre los defectos comunicados: plantilla obligatoria/cancelación, eliminación y undo/redo, evento automático vacío, Supr con foco y edición de texto, protección de dependencias, contraste en ambas paletas, posición fija de pestañas, dirección de cámara, recentrado y órbita. El ensayo de Qt/OpenGL real y sus capturas quedan en `research/phase9/editor_fixes/gui/`; la regresión completa y el ensayo del portable actualizado quedan en esa carpeta de investigación.

La suite completa pasó **208 tests sin fallos, errores ni omisiones**, además de los controles de calidad. Las comprobaciones de cámara usan eventos Qt sintéticos y pruebas numéricas: el entorno automatizado no entrega de forma fiable movimientos físicos de Windows a esta ventana. El recentrado con el ratón físico y la sensación del movimiento requieren la comprobación manual del usuario; no se presenta ese ensayo como realizado.

Estos resultados verifican el editor. No convierten en PASS las pruebas de guardado/carga, cámara o quests dentro de Vampire que el usuario aplazó.
