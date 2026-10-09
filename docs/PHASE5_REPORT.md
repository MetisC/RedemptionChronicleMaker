# Estado de Fase 5 al comenzar Fase 6

Fase 5 quedó interrumpida y parcialmente implementada. No se considera validada dentro de Redemption; la introducción del nuevo encargo no acredita capacidades ausentes.

Implementado: NOT lossless con corpus de cuatro originales, writer restringido, project_format 5, templates derivados/copias, AI limitada, Java propio 45.3 e importación a TGA. GUI Templates/AI, Playtest/Debug e instrumentación opcional; proyección gráfica del mismo modelo sin aceptación completa. Demo phase5_demo creada con GUI, compilada y desplegada; evidencia en build/phase5_acceptance/report.json. Los 120 tests pasaban tras corregir callbacks de conversación y firmas de persistencia.

El usuario observó crónica, mapa, NPC y conversación, pero reportó Witness sin interacción, cámara sin cambio y desaparición de cursor/UI al rechazar. La corrección guardada aún no estaba desplegada ni probada nativamente. El writer NOT permanece experimental; AI, inventario y save/load nativos no tienen aceptación. El control automático del ratón no coincide con el cursor interno del juego.

No terminado: rcmpack/rcmproject administrados, instalador/desinstalador con ownership, aplicación portable, primera ejecución y diagnóstico robusto; timeline cinematográfico, XYZ/frustum, paths y presets AI amplios; aceptación graph/tree y documentación final de recursos.

Tags NOT de salud, clan, stats y disciplinas desconocidos no se exponen como funcionales. Items derivados pueden generarse, pero pickup nativo no se probó. La AI preserva líneas desconocidas y edita sólo escalares conocidos. Importar una textura no crea un material/modelo propio. Debug observa logs y flags del controlador, no memoria en vivo ni journal nativo.

Los ZIP/NOB con clases ya existían. No había paquete administrado ni ejecutable portable. Guardado/carga y red siguen pendientes. Fase 6 debe auditar y cubrir huecos críticos; las capacidades amplias no necesarias para estabilizar una crónica completa quedan documentadas como backlog. Sin herramientas originales ni edición de geometría.
