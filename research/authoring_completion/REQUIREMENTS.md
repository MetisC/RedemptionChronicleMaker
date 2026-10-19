# REDEMPTION CHRONICLE MAKER — CIERRE DEFINITIVO DEL ALCANCE ORIGINAL

## MISIÓN

Trabaja sobre mi repositorio privado:

**MetisC/RedemptionChronicleMaker**

Todo el trabajo vigente está fusionado en `main`.

Quiero una última pasada exhaustiva de **investigación, implementación y corrección funcional** para completar el alcance ORIGINAL de Redemption Chronicle Maker.

**NO quiero otro informe que simplemente enumere limitaciones. Quiero que investigues y soluciones todo lo técnicamente viable.**

El objetivo original es crear crónicas completas de Vampire: The Masquerade — Redemption desde un editor moderno, visual, independiente y autónomo, sin necesitar Embrace, NOT Editor ni edición manual de archivos para las tareas habituales.

Se reutiliza la geometría original. La edición estructural de geometría, CSG, sectores, UV y lightmaps sigue FUERA DE ALCANCE.

## FUENTES OBLIGATORIAS

Antes de implementar, lee:

- `AGENTS.md`
- `docs/FINAL_PRODUCT_REPORT.md`
- `docs/EMBRACE_AUTHORING_PARITY.md`
- `docs/RC4_REQUIREMENTS.md`
- `docs/DYNAMIC_ENCOUNTERS.md`
- `docs/CINEMATIC_DIRECTOR.md`
- `docs/ADVANCED_LIMITATIONS.md`
- `docs/MANUAL_RUNTIME_CHECKLIST.md`
- `research/embrace_strict_parity/`
- `research/embrace_closure/`
- `research/API_SIGNATURES.txt`

Revisa también las investigaciones originales conservadas sobre Embrace, formatos binarios, APIs de Codex y scripts nativos.

**No aceptes automáticamente como definitivas las limitaciones declaradas en informes anteriores.** Comprueba si esas conclusiones son correctas, si las investigaciones fueron suficientes y si existe una alternativa real dentro del motor.

No inventes funciones, formatos ni capacidades.

## 1. SCRIPTS NATIVOS, REGIONES Y COMPORTAMIENTOS ORIGINALES

Este es uno de los principales huecos pendientes.

RCM permite asignar scripts originales y configurar parámetros, pero determinados scripts necesitan contextos regionales, enlaces o mecanismos especiales que aún no se reproducen completamente.

Quiero que:

1. Audites los scripts originales relevantes para la creación de crónicas.
2. Identifiques cuáles todavía no pueden configurarse normalmente desde RCM.
3. Investiges sus constructores, parámetros, callbacks, relaciones y contexto nativo.
4. Implementes los mecanismos necesarios cuando estén suficientemente demostrados.
5. Incorpores controles visuales y validaciones adecuados para que el usuario no tenga que editar Java/YAML.

Investiga también las regiones nativas y sus diferencias con los triggers existentes.

No crees un segundo sistema de triggers o eventos si es posible ampliar el actual.

El resultado debe ser un editor capaz de reutilizar los mecanismos originales de Redemption con el mínimo de limitaciones reales.

## 2. ENEMIGOS DINÁMICOS Y CONTROL CINEMATOGRÁFICO

El sistema RC4 permite generar enemigos, oleadas, refuerzos y jefes por fases.

Sin embargo, determinados controles de cámara, animación, inventario e IA siguen funcionando únicamente con actores colocados previamente.

Quiero que investigues e implementes, siempre que el motor lo permita:

- Referencias a enemigos generados mediante roles o identificadores de encuentro.
- Acciones que afecten al jefe activo o a enemigos concretos de una oleada.
- Animaciones, movimientos y cambios de comportamiento sobre esos enemigos.
- Cámaras y secuencias que puedan seguir al jefe generado dinámicamente.
- Acciones y condiciones de fase reutilizando el motor existente.
- Resolución segura de referencias después de guardar/cargar y volver a una escena.

No crees otro gestor de actores, otro runtime ni un sistema de combate paralelo.

Preserva GUID, propiedad, reconciliación, límites de generación y comportamiento de partidas existentes.

Cuando una acción no pueda aplicarse con seguridad, debe fallar de forma controlada y explicarse en la interfaz.

## 3. ENTORNO, SONIDO E ILUMINACIÓN

Investiga y completa la autoría de:

**EAX y propiedades ambientales:** actualmente se heredan características originales porque el entorno estático tiene precedencia. Investiga si existe alguna vía nativa real para establecerlas sin modificar la geometría.

**Soundboxes:** determina su formato y comportamiento originales. Comprueba si pueden representarse con seguridad o mediante un equivalente funcional que permita al autor establecer zonas sonoras.

**Lightboxes:** investiga su relación con la iluminación dinámica y los datos estructurales. Distingue lo que realmente funciona durante el juego de lo que depende de la compilación de geometría.

**Sonido y efectos espaciales:** verifica que las acciones visuales del editor permiten configurar los comportamientos necesarios para escenas narrativas complejas.

Si el motor no permite alguna función literal de Embrace, desarrolla un equivalente seguro cuando sea posible, sin venderlo falsamente como idéntico.

No incorpores sliders ni opciones que no tengan efecto real.

## 4. DIRECTOR CINEMATOGRÁFICO Y CÁMARAS

Completa las posibilidades de autoría cinematográfica pendientes.

Investiga especialmente:

- Rotaciones estacionarias temporizadas.
- Esperas y transiciones entre planos.
- Keyframes y orientación de cámara.
- Reproducción de NCP propios y originales.
- Sincronización de cámaras, actores, sonido, eventos y conversaciones.
- Cancelación, interrupción y recuperación del control.
- Persistencia y restauración de secuencias.

Si el formato NCP original no admite de forma demostrable un giro estacionario temporizado, analiza si puede expresarse mediante otras APIs reales de cámara, interpolaciones o planos controlados.

**El objetivo es la posibilidad cinematográfica, no reproducir obligatoriamente cada detalle interno de Embrace.**

No cambies los NCP originales ni dañes secuencias existentes.

## 5. MAPAS Y LOCALIZACIONES PROPIAS

Existe investigación previa en `research/embrace_strict_parity/MAPS.md` que identifica una vía para generar mapas NUI propios, imágenes, nombres y puntos de localización sin editar NIL.

Evalúa esta investigación e implementa un editor visual de mapas y localizaciones si la evidencia confirma que puede hacerse de forma segura.

Debe permitir, dentro de los límites reales del motor:

- Importar una imagen de mapa propia.
- Añadir, mover, editar y eliminar puntos.
- Asignar escenas a localizaciones.
- Configurar nombres y propiedades nativas demostradas.
- Gestionar visibilidad/descubrimiento cuando existan APIs verificadas.
- Integrar recursos, referencias, undo/redo y empaquetado.

No confundas el mapa informativo original con un sistema de viaje por clic. No añadas comportamientos no respaldados por el motor.

## 6. AUDITORÍA DE PARIDAD FUNCIONAL Y DE INTERFAZ

Esta parte es especialmente importante.

No te limites a los cinco apartados anteriores.

Recorre **todas las funcionalidades de autoría no geométrica del producto original**, contrastando:

1. Qué podía configurar un autor de crónicas usando Embrace y herramientas originales.
2. Qué puede configurar actualmente mediante la interfaz normal de RCM.
3. Qué operaciones siguen requiriendo editar YAML o escribir Java.
4. Qué comportamientos solo están parcialmente representados.
5. Qué operaciones carecen de alternativa funcional.

Incluye actores, objetos, plantillas, IA, inventarios, scripts, triggers, conversaciones, quests, escenas, cámaras, sonido, ambientación, puertas, efectos, encuentros y recursos.

**No basta con que el backend admita algo: debe poder utilizarse desde la interfaz si es una tarea habitual.**

Implementa los controles, asistentes y validaciones que falten para cerrar ese objetivo.

No crees pestañas innecesarias ni dupliques pantallas y sistemas ya existentes.

Las opciones avanzadas pueden seguir siendo avanzadas, pero deben ser accesibles.

## 7. REGLAS ESTRICTAS DE IMPLEMENTACIÓN

- Conserva las funcionalidades existentes.
- No rompas el tutorial aceptado ni la mini crónica.
- Mantén compatibles los formatos 9 y 10.
- No conviertas proyectos automáticamente.
- No alteres la geometría original.
- No inventes APIs de Codex.
- No introduzcas ejecutores paralelos para funciones que el runtime actual ya cubre.
- No generes código arbitrario donde existan funciones nativas verificadas.
- Mantén la protección de proyectos personales y recursos del usuario.
- No modifiques archivos originales de la instalación de Redemption.
- No introduzcas librerías o frameworks innecesarios.
- Las importaciones de mods con código binario desconocido no deben implementarse de forma insegura para aparentar compatibilidad universal.
- No cambies artificialmente tests o fixtures para hacerlos pasar.

## 8. CÓMO TRATAR LAS LIMITACIONES DEL MOTOR

Clasifica cada problema pendiente en una de tres situaciones:

**A. Implementable con evidencia:** investiga, programa, integra y prueba.

**B. Implementable mediante alternativa equivalente:** desarrolla una solución que consiga el resultado narrativo sin reproducir obligatoriamente el mecanismo original.

**C. Demostrablemente imposible o inseguro:** aporta evidencia técnica concreta, explica qué mecanismo del motor lo impide y conserva una alternativa práctica cuando exista.

No aceptes «no está documentado», «nadie lo ha hecho» o «es muy complicado» como demostraciones de imposibilidad.

Tampoco fuerces implementaciones especulativas que puedan corromper una partida.

## 9. VERIFICACIÓN Y REGRESIONES

Para cada funcionalidad modificada o añadida:

1. Implementa tests unitarios.
2. Implementa tests de integración de backend y generadores.
3. Comprueba la validez de formatos generados.
4. Compila el Java real contra Codex cuando corresponda.
5. Verifica transacciones del editor, referencias, undo/redo, guardado y reapertura.
6. Comprueba compatibilidad con proyectos anteriores.
7. Añade pruebas de casos límite y errores.
8. Ejecuta la batería completa, no únicamente el gate rápido de 28 pruebas.
9. Corrige las regresiones antes de finalizar.

Puedes preparar laboratorios de aceptación adicionales, siempre separados del tutorial original.

No declares probado en Redemption algo que solo se ha ejecutado contra mocks o mediante compilación.

Las pruebas manuales dentro del videojuego corresponden al usuario; debes dejar los escenarios preparados y las comprobaciones claramente especificadas.

## 10. ENTREGA Y CRITERIO DE FINALIZACIÓN

Quiero que el resultado final sea **RCM funcionalmente completo respecto al alcance original acordado**, no otra expansión inconexa.

No inviertas trabajo en publicar nuevas releases, actualizar marketing, cambiar versiones o mejorar aspectos estéticos que no bloqueen la autoría.

Prioriza cerrar funcionalidades reales.

Trabaja con el estado vigente de `main`. No dejes el resultado terminado abandonado en otra rama. Si tu entorno exige crear una rama y un PR, fusiónalo a `main` tras superar las comprobaciones correspondientes. No reescribas el historial ni hagas force-push.

Al terminar proporciona:

**A. Funcionalidades pendientes que has completado:** descripción, archivos modificados y forma de utilizarlas desde la interfaz.

**B. Alternativas funcionales implementadas:** para mecanismos de Embrace que no puedan reproducirse literalmente.

**C. Limitaciones inevitables:** únicamente las que puedas demostrar técnicamente, separadas de las que siguen siendo simples incógnitas.

**D. Resultados de calidad:** pruebas, compilación Codex, regresiones y comprobaciones automatizadas realmente ejecutadas.

**E. Matriz final de cobertura:** todas las capacidades de autoría relevantes, clasificadas como IMPLEMENTADA, IMPLEMENTADA MEDIANTE ALTERNATIVA, LIMITACIÓN DEMOSTRADA o PENDIENTE.

**F. Pruebas manuales para mí:** una lista corta, priorizada y concreta, centrada únicamente en aquello que no puedas certificar sin ejecutar Redemption.

### INSTRUCCIÓN FINAL

No te limites a producir otra auditoría o documentación diciendo que todo está parcialmente terminado.

**Investiga e implementa todas las funcionalidades técnicamente viables necesarias para completar el propósito original del editor.**

No declares el 100 % si todavía faltan funciones implementables.

Y no amplíes artificialmente el alcance hacia edición de geometría, sustitución del motor del juego o reproducción de herramientas originales que no aporten capacidades útiles de creación de crónicas.

Quiero cerrar el proyecto, no comenzar otro.