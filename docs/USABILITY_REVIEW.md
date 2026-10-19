# Usabilidad vigente del editor

Esta revisión se centra en encontrar contenido, elegir recursos, navegar sin
ratón, conservar el contexto y corregir errores de edición. Mantiene rc7, los
formatos, el tutorial aceptado y el runtime. No añade pestañas principales.

## Cambios aplicados

- El árbol del proyecto tiene búsqueda por nombre/ID con Ctrl+F, botón para
  limpiar y mensaje cuando no hay coincidencias. Intro selecciona un resultado.
  Filtrar sólo afecta al árbol; no cambia la visibilidad en el juego. Supr no
  elimina una selección que haya quedado oculta por la búsqueda.
- Los grupos plegados permanecen plegados al actualizar. Abrir otra crónica
  limpia las búsquedas para no ocultar accidentalmente su contenido.
- Ctrl+Shift+F busca en toda la crónica por contenido y escena, con detalles
  traducidos, recuento y navegación mediante Intro. Los flags abren su editor
  real; los elementos sencillos ya no muestran un segundo editor de ID
  incompatible en la vista global.
- El catálogo explica las listas vacías y ofrece restablecer filtros. Conserva
  el tipo de recurso y las restricciones del inventario. La selección sobrevive
  a una actualización si sigue siendo válida; nunca se confirma una fila vieja
  tras cambiar la búsqueda o el tipo de recurso.
- Intro en la búsqueda del catálogo lleva a los resultados; Intro sobre una fila
  la confirma. Aceptar, inspeccionar y marcar favorito requieren una selección
  válida para esa operación. Los proyectos recientes también se abren con Intro.
- Cambiar de elemento no descarta una propiedad pendiente incorrecta. Su campo
  permanece disponible para corregirlo. La selección de los árboles se restaura
  cuando la navegación no puede completarse.
- El acceso a encuentros dinámicos ocupa menos espacio y conserva el nombre
  completo en su ayuda. Las acciones sin selección de la vista global se
  desactivan. Los paneles vacíos explican cómo empezar.

## Comprobación y límites

`tests/test_usability.py` ejercita los recorridos con controles Qt reales y
teclado. `tools/editor_review_probe.py` comprueba ambos idiomas y conserva
capturas de búsqueda, catálogo y vista global a 1100×720 en
`build/tests/editor_review/`. El resto de la regresión sigue pasando por
`tools/quality.py`.

Estas comprobaciones son de interfaz sin OpenGL. No certifican navegación con
GPU física, todas las escalas de Windows ni comodidad en una sesión larga de
autoría. Las pruebas dentro de Redemption corresponden al usuario; esta revisión
no modifica lógica ni recursos del juego. Evidencia del ejecutable y resultados
actuales: `research/usability/verification.json`.
