# RCM — CIERRE DEFINITIVO DEL 100 % FUNCIONAL

## OBJETIVO

Trabaja directamente sobre el estado actual de `main` del repositorio privado:

**MetisC/RedemptionChronicleMaker**

Quiero completar definitivamente el alcance funcional original de Redemption Chronicle Maker.

El objetivo es disponer de un editor autónomo, moderno y visual capaz de crear crónicas complejas de Vampire: The Masquerade — Redemption, reutilizando los escenarios originales sin modificar su geometría y sin depender de Embrace, NOT Editor o edición manual de Java/YAML para las operaciones habituales.

**NO quiero otra fase de ampliación general del proyecto. Quiero cerrar los últimos huecos funcionales identificados en la auditoría.**

Actualmente la matriz de `docs/EMBRACE_AUTHORING_PARITY.md` registra:

- 35 capacidades implementadas directamente.
- 19 implementadas mediante alternativas.
- 2 pendientes de resolver.
- 2 limitaciones técnicas identificadas.

La batería automatizada más reciente registra 599 pruebas satisfactorias y siete ejemplos compilados contra Codex real.

Partimos de ese estado, sin rehacer funcionalidades que ya están resueltas.

## 1. PRIORIDAD ABSOLUTA: SCRIPTS NATIVOS CON CODEXPLAYER

La primera incógnita pendiente es la vinculación segura de scripts originales específicos de campaña que reciben `CodexPlayer` en sus constructores.

Lee obligatoriamente:

- `research/authoring_completion/player_contexts.json`
- `research/authoring_completion/script_contexts.json`
- `research/authoring_completion/EVIDENCE.md`
- `research/embrace_strict_parity/codex_linker_format.md`
- `research/API_SIGNATURES.txt`
- `src/rcm/native_scripts.py`
- `src/rcm/script_parameters.py`

### Investigación

Analiza los seis constructores identificados que utilizan CodexPlayer y sus contextos originales.

Investiga los registros NSD, los tipos de parámetros nativos, las referencias, el ciclo de vida del jugador y el funcionamiento en crónicas locales cargadas mediante Multiplayer/LAN.

Determina:

1. Cómo obtiene el motor la referencia válida a CodexPlayer.
2. Cuándo existe esa referencia durante la creación y carga de una crónica.
3. Cómo se conservan o reconstruyen los enlaces después de guardar/cargar.
4. Qué diferencia existe entre los constructores de scripts originales de campaña y los scripts reutilizables.
5. Qué dependencias internas de esos scripts impiden trasladarlos directamente a una crónica personalizada.

No basta con reconocer un tipo de parámetro en un NSD. Debes demostrar que el enlace corresponde a un jugador válido y seguro en el momento necesario.

### Implementación

Si existe un mecanismo real y verificable:

- Añade soporte tipado para CodexPlayer.
- Integra la selección del jugador en el editor visual.
- Resuelve correctamente la referencia en runtime.
- Gestiona ausencia temporal del jugador y restauración de partidas.
- Evita referencias inválidas, duplicaciones y fallos de inicialización.
- Conserva los callbacks y estado nativos sin duplicar la propiedad de las entidades.

Si algunos scripts dependen inevitablemente de CastIDs, quests u otros elementos exclusivos de la campaña original, distingue esas dependencias del problema de CodexPlayer.

No habilites scripts que solo funcionen accidentalmente por casualidad.

Para los comportamientos útiles que no puedan reutilizarse directamente, desarrolla alternativas mediante los eventos y acciones actuales de RCM.

**Resultado exigido: ningún comportamiento narrativo habitual debe quedar bloqueado por esta limitación.**

## 2. PRIORIDAD ABSOLUTA: SOUNDBOXES Y LIGHTBOXES

Segunda incógnita pendiente.

Ya disponemos de zonas activadoras de sonido y luz, pero no conocemos completamente el payload original de las cajas nativas ni su comportamiento de recorte por sectores.

Lee:

- `research/authoring_completion/native_regions_corpus.json`
- `research/embrace_strict_parity/SAFETY_DECISIONS.md`
- Investigaciones de bloques y tablas auxiliares NSD.
- `src/rcm/native_regions.py`
- `src/rcm/scene_zones.py`
- `src/rcm/audio.py`
- `src/rcm/world_effects.py`
- `src/rcm/formats.py`

### Investigación

Identifica mediante archivos originales, SDK y análisis del ejecutable:

- Estructura binaria de soundboxes y lightboxes.
- Límites, sectores y relaciones con la escena.
- Condiciones de activación.
- Diferencias entre sonido espacial, sonido ambiental y cajas.
- Diferencias entre iluminación dinámica y luz precalculada.
- Persistencia y comportamiento al salir y volver a una zona.

Distingue rigurosamente los datos de runtime de los dependientes de compilación de geometría y lightmaps.

### Implementación

**Opción A: implementación nativa.**

Si los formatos y su semántica quedan suficientemente demostrados, implementa su generación segura desde la interfaz.

**Opción B: equivalencia funcional completa.**

Si la representación nativa no es segura, mejora las zonas actuales hasta cubrir el uso narrativo práctico de estas cajas:

- Activación y desactivación por entrada/salida.
- Posicionamiento y radios.
- Compatibilidad con sectores cuando pueda obtenerse de forma segura.
- Sonidos en bucle, interrupciones y limpieza correcta.
- Luces puntuales, color, intensidad y comportamiento.
- Guardado, carga y reentrada sin duplicar handles.
- Convivencia con scripts y eventos existentes.

No implementes efectos que requieran recompilar lightmaps si están fuera del alcance original.

**Resultado exigido: poder construir escenas con ambientación sonora e iluminación interactiva desde la interfaz sin recurrir a Embrace.**

La solución alternativa puede sustituir al mecanismo original, pero sus diferencias deben quedar claramente especificadas.

## 3. REVISAR LAS DOS LIMITACIONES RECONOCIDAS

No quiero ampliar artificialmente el proyecto, pero tampoco aceptar límites anteriores sin revisarlos.

### A. FOV por keyframe de cámara

El formato NCP original no incluye FOV individual por punto.

Investiga si las APIs reales de CodexCamera permiten cambiar la lente o el encuadre durante una secuencia sin modificar el formato NCP.

Si es viable:

- Añade la opción visual correspondiente.
- Integra el cambio con los cues y secuencias actuales.
- Garantiza liberación y recuperación correcta de la cámara.
- Añade pruebas.

Si no es viable, confirma la limitación mediante evidencia y conserva el sistema actual de planos, presets y transiciones.

No inventes propiedades NCP inexistentes.

### B. Importación de mods con código externo

Comprueba que el sistema actual permite importar todos los recursos de datos que pueden utilizarse con seguridad.

No necesito ejecutar indiscriminadamente clases binarias de terceros.

Si existen recursos reutilizables que se rechazan innecesariamente, mejora el importador y sus validaciones.

Si requieren código ejecutable desconocido, conserva la restricción.

**La compatibilidad universal con ejecutables arbitrarios NO es un requisito para declarar terminado RCM.**

## 4. AUDITORÍA FINAL DE INTEGRACIÓN

Después de resolver los puntos anteriores, realiza una auditoría técnica cruzada de las 58 capacidades.

No vuelvas a escribir otra matriz basada únicamente en declaraciones de funcionalidad.

Comprueba cada ruta relevante:

**Interfaz → modelo → validación → generador → formatos nativos/Java → compilación → persistencia.**

Da especial atención a:

- Scripts nativos y regiones.
- Zonas de sonido, luz y EAX.
- Cámara NCP y temporización.
- Objetivos dinámicos por GUID/rol.
- Encuentros, jefes y dificultad.
- Mapas propios y flags de localización.
- Conversaciones, eventos, quests y viajes.
- Recursos compartidos.
- Guardado, carga, reentrada y cambios de escena.

Investiga incompatibilidades entre funcionalidades avanzadas que funcionan aisladamente, pero podrían fallar al combinarse en una misma crónica.

No crees más subsistemas donde ya existen herramientas equivalentes.

## 5. PRUEBAS Y CALIDAD

Realiza una validación completa después de implementar.

Obligatorio:

1. Ejecutar la batería completa de pruebas, no solo las 28 del CI rápido.
2. Corregir todos los fallos encontrados.
3. Ejecutar Ruff y el alcance configurado de mypy.
4. Compilar los siete ejemplos actuales contra Codex real.
5. Crear tests de las nuevas funciones y sus interacciones.
6. Comprobar compatibilidad con formatos 9 y 10.
7. Verificar que el tutorial y la mini crónica no cambian.
8. Probar creación, edición, deshacer, guardar y reapertura desde Qt.
9. Comprobar que no se generan referencias inválidas o clases Java incompatibles.
10. Auditar persistencia y propiedad de GUID, actores y recursos compartidos.

Cuando sea posible, utiliza harnesses que ejerciten el bytecode Java generado, además de inspeccionar su texto.

No modifiques fixtures para ocultar regresiones.

No conviertas una prueba con mocks en evidencia de funcionamiento real dentro de Redemption.

## 6. REGLAS INNEGOCIABLES

- No tocar geometría NIL, CSG, UV ni lightmaps.
- No modificar archivos originales de Redemption.
- No alterar proyectos personales.
- No romper los tutoriales aceptados.
- No cambiar las reglas ni mecánicas del videojuego.
- No introducir dependencias innecesarias.
- No crear otro runtime de eventos o encuentros.
- No duplicar mecanismos de persistencia.
- No inventar APIs ni datos binarios.
- No esconder errores con excepciones capturadas indiscriminadamente.
- No marcar funcionalidades como implementadas simplemente porque compilan.
- No rebajar tests ni modificar expectativas para obtener resultados verdes.
- No publicar releases ni invertir tiempo en versiones o marketing.
- No crear otra documentación gigantesca de investigación sin utilidad práctica.

Mantén una interfaz sencilla y coherente con los paneles actuales.

## 7. CRITERIO REAL DEL 100 %

Consideraré una capacidad funcionalmente completa cuando:

1. Su propósito narrativo esté cubierto directamente o mediante una alternativa adecuada.
2. Pueda configurarse desde el editor sin programación manual habitual.
3. El backend valide correctamente los datos.
4. Se generen los recursos y el Java necesarios.
5. Compile con las herramientas reales del proyecto.
6. Supere las pruebas automatizadas aplicables.
7. No introduzca regresiones ni riesgos conocidos sin controlar.

**No exijo paridad binaria literal con Embrace cuando existe una alternativa funcional suficiente.**

Tampoco exijo compatibilidad universal con scripts exclusivos de la campaña original cuyos presupuestos internos no se cumplan en una crónica personalizada.

Pero NO puedes declarar completada una funcionalidad relevante si sigue faltando una operación habitual y técnicamente implementable.

La aceptación final dentro de Vampire corresponde al usuario y se mantiene separada de la finalización del desarrollo.

## 8. TRABAJO AUTÓNOMO

No te detengas después de investigar un problema.

Investiga, implementa lo viable, añade tests, ejecuta las verificaciones, corrige los errores y continúa con el siguiente problema.

Puedes organizar el trabajo internamente como necesites.

Trabaja con el estado actual de `main`. Si necesitas una rama temporal, fusiónala después de validar. No hagas force-push ni reescribas el historial.

No dejes una rama sin fusionar como resultado final.

## 9. ENTREGA FINAL: BREVE Y CONCRETA

Quiero solamente:

**A. Qué has solucionado realmente:** funcionalidades nuevas y correcciones, con rutas de código.

**B. Qué no has podido implementar:** causa técnica concreta, evidencia y alternativa funcional existente.

**C. Estado de las 58 capacidades:** implementadas, equivalentes, limitaciones justificadas y pendientes reales.

**D. Pruebas:** cifras exactas, resultados y compilaciones.

**E. Pruebas manuales restantes:** únicamente las que necesariamente requieren iniciar Redemption, priorizadas.

**F. Veredicto:** si el desarrollo del alcance funcional original puede considerarse cerrado. Si no, indica exactamente qué función implementable sigue faltando y por qué.

### INSTRUCCIÓN FINAL

**Quiero TERMINAR Redemption Chronicle Maker, no seguir investigándolo indefinidamente.**

Resuelve los dos pendientes técnicos, revisa las dos limitaciones reconocidas, corrige los problemas de integración y completa cualquier funcionalidad habitual que siga sin cubrirse.

No cambies la definición del objetivo para declarar artificialmente el 100 %.

Pero tampoco mantengas eternamente como «pendiente» una diferencia interna con Embrace cuando ya existe una alternativa funcional plenamente válida.

**Al finalizar, el único trabajo restante debería ser mi aceptación manual dentro del videojuego y la corrección de los errores concretos que pueda descubrir.**