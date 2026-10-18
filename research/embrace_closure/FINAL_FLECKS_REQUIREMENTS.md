======================================================================
REDEMPTION CHRONICLE MAKER
FINAL EMBRACE AUTHORING CLOSURE
SURGICAL PASS — REMAINING NON-GEOMETRY GAPS
======================================================================

OBJETIVO

Estamos en el cierre real de Redemption Chronicle Maker.

ESTA NO ES UNA NUEVA FASE DE FEATURES.

NO utilizar esta tarea como permiso para añadir:

- nuevos subsistemas
- nuevas pestañas principales
- un nuevo project format
- editores genéricos
- abstracciones paralelas
- herramientas de geometría
- features “porque la API las permite”
- otro megaproyecto dentro de RCM

El objetivo final continúa siendo:

    CREAR UNA CRÓNICA SERIA DE
    VAMPIRE: THE MASQUERADE — REDEMPTION

    SIN NECESITAR EMBRACE PARA LA AUTORÍA NORMAL.

La geometría permanece deliberadamente FUERA DE SCOPE.

NO queremos:

- CSG
- brushes
- modificación estructural del NIL
- sectores
- portales
- paredes/suelos
- UV
- texturizado estructural
- lightmaps
- modelado
- un mini Blender
- recrear cada botón de Embrace

Queremos cerrar únicamente los últimos huecos NO GEOMÉTRICOS
materiales para crear una crónica.

======================================================================
0. REGLA CERO — AUDITAR HEAD ANTES DE TOCAR CÓDIGO
======================================================================

Antes de implementar nada:

1. Inspecciona el HEAD REAL actual del repositorio.
2. Revisa todos los cambios desde la última versión analizada.
3. No uses informes antiguos como fuente de verdad si contradicen HEAD.
4. Revisa:
   - código actual
   - SDK/manuales originales
   - Codex real
   - scripts originales
   - análisis del executable ya guardado
   - investigaciones previas
5. Reconfirma todas las cifras/callsites usadas en este prompt.

No reescribas sistemas ya funcionales sólo para “dejarlos más bonitos”.

Preservar:

- scenery click interactions
- fixed-surface click overlays
- original objects / doors
- WTD selective import
- dynamic encounters
- current Cinematic Director
- camera paths
- format 9
- format 10
- F5 workflow
- tutorial
- mini chronicle
- Dynamic Encounter Lab
- Showcase
- director_acceptance
- inventory compatibility
- deployment ownership
- Safe Delete
- References
- undo/redo
- custom Java escape hatch

Nunca modificar recursos originales del juego.

======================================================================
1. FILOSOFÍA DE PRODUCTO CONGELADA
======================================================================

El flujo debe seguir siendo:

    IDEA
      ↓
    AUTORÍA VISUAL
      ↓
    F5
      ↓
    REDEMPTION

RCM debe expresar INTENCIONES del autor.

No queremos que el usuario tenga que pensar como Nihilistic.

Reutilizar siempre que sea posible:

- Actions
- Events
- Conditions
- Sequences
- Resources
- Entries
- Waypoints
- References
- Safe Delete
- inspectors existentes

NO crear sistemas paralelos.

Una Sequence determina CUÁNDO.

Una Action determina QUÉ.

Una Conversation line puede lanzar las MISMAS Actions.

======================================================================
2. FLECO A
MUSIC STACK NATIVO — PushMusic / PopMusic
======================================================================

La auditoría anterior encontró aproximadamente:

    PushMusic → 55 clases originales
    PopMusic  → 53 clases originales

RECONFIRMAR estas cifras.

Esto es demasiado frecuente para considerarlo una curiosidad.

Actualmente RCM soporta:

    StartMusic
    StopMusic
    StartAmbient
    StopAmbient

Pero esto NO demuestra equivalencia con el music stack original.

----------------------------------------------------------------------
2.1 INVESTIGACIÓN
----------------------------------------------------------------------

Investigar:

    CodexSound.PushMusic
    CodexSound.PopMusic

Comprobar:

- firmas exactas
- parámetros
- volumen
- resource name
- nested pushes
- comportamiento de Pop
- ownership
- transición entre escenas
- save/load
- casos de error
- si el motor conserva automáticamente la música anterior
- cómo los scripts originales balancean Push/Pop

Buscar callsites representativos.

Clasificar evidencias:

    CONFIRMED IN API
    CONFIRMED IN ORIGINAL SCRIPT
    CONFIRMED IN SDK
    INFERRED
    NATIVE TEST REQUIRED
    NOT FOUND

NO deducir comportamiento sólo por el nombre del método.

Crear evidencia bajo:

    research/embrace_closure/

----------------------------------------------------------------------
2.2 IMPLEMENTACIÓN
----------------------------------------------------------------------

Si la semántica queda demostrada:

Añadir Actions normales, por ejemplo:

    Música / Reproducir música temporal
    Música / Restaurar música anterior

o nombres equivalentes más humanos.

Internamente pueden mapear:

    CodexSound.PushMusic(...)
    CodexSound.PopMusic(...)

si las firmas han sido demostradas.

NO crear:

- Music Manager paralelo
- nueva pestaña
- timeline propia
- stack editor falso

Estas acciones deben funcionar en cualquier sitio donde funcionen
Actions normales:

- eventos
- clic
- conversation line
- cinematic cue
- boss phase
- etc.

----------------------------------------------------------------------
2.3 VALIDACIÓN
----------------------------------------------------------------------

Validar únicamente lo demostrado:

- recurso musical válido
- volumen válido si existe
- parámetros reales

NO inventar parámetros.

NO crear un stack RCM si el stack ya pertenece al engine.

----------------------------------------------------------------------
2.4 OWNERSHIP / SAVE
----------------------------------------------------------------------

No inventar persistencia.

Si el stack es propiedad nativa del motor:

    dejarlo nativo

salvo que la evidencia demuestre que RCM debe guardar algo.

No hacer Pop automático sobre música que RCM no sabe que haya pusheado.

Si se necesita ownership:

- bounded
- explícito
- fail closed

----------------------------------------------------------------------
2.5 TESTS
----------------------------------------------------------------------

Añadir pruebas:

- validation
- UI action editing
- serialization
- generated Java
- compilation against real Codex
- cinematic cue usage
- regression StartMusic/StopMusic
- regression Ambient

Pruebas manuales:

EMB-MUSIC-01
    Música normal
    → Push música dramática
    → Pop
    → vuelve la música anterior

EMB-MUSIC-02
    Push/Pop dentro de Sequence.

EMB-MUSIC-03
    Save/load/travel según semántica demostrada.

NO marcar runtime verified automáticamente.

======================================================================
3. FLECO B
TRUE CONVERSATION STAGING / CONVSTARTS
======================================================================

El Embrace original expone:

    convstarts 0–15

La API real expone:

    CodexPlayer.TeleportPartyToConversation(player,index)

La auditoría anterior encontró aproximadamente:

    107 clases originales

que llaman a TeleportPartyToConversation.

RECONFIRMAR.

Esto es demasiado frecuente como para asumir que:

    TeleportPartyToEntrance

es automáticamente equivalente.

Actualmente RCM reutiliza Entry para Conversation Staging.

Es una solución elegante.

Pero debe demostrarse su equivalencia práctica.

----------------------------------------------------------------------
3.1 INVESTIGACIÓN
----------------------------------------------------------------------

Estudiar:

- Embrace manual
- cutscene manual
- CodexPlayer API
- original scripts
- original NSD data
- executable reader si existe evidencia suficiente
- TeleportPartyToEntrance
- TeleportPartyToConversation

Responder:

1. ¿playerstarts y convstarts son estructuras separadas?
2. ¿Qué almacena un convstart?
3. ¿posición?
4. ¿orientación?
5. ¿formación del grupo?
6. ¿party members distribuidos automáticamente?
7. ¿0–15 es un array nativo real?
8. ¿qué bloque NSD los almacena?
9. ¿RCM puede escribir ese bloque de forma segura?
10. ¿qué diferencia visual/runtime existe frente a Entrance?
11. ¿el sistema de cámara/dialogue depende de esa diferencia?

Crear evidencia reproducible.

----------------------------------------------------------------------
3.2 DECISIÓN
----------------------------------------------------------------------

CASO A
------

Si Entry staging produce de forma demostrable el resultado necesario:

    NO implementar otro sistema.

Clasificar:

    COVERED DIFFERENTLY

Documentar claramente:

    RCM named staging provides the required runtime placement.

Pero NO afirmar que Entrance y Conversation sean idénticos internamente.

Añadir prueba comparativa.

CASO B
------

Si native convstarts tienen comportamiento útil que Entry no reproduce:

implementar la mínima abstracción posible.

UX preferida:

    Conversación
      Puesta en escena:

        Automática
        Entrada RCM
        Punto de conversación nativo

No presentar:

    convstart 7

como UX principal.

Usar nombres humanos.

----------------------------------------------------------------------
3.3 REUTILIZAR INFRAESTRUCTURA ESPACIAL
----------------------------------------------------------------------

NO crear otro editor de marcadores desde cero.

Reutilizar:

- viewport
- capture position
- orientation
- transform widget
- gizmos si procede
- References
- Safe Delete
- Undo/Redo

Internamente puede tener storage distinto si el engine lo exige.

Pero para el usuario debe sentirse como otro marcador espacial normal.

----------------------------------------------------------------------
3.4 SEGURIDAD NSD
----------------------------------------------------------------------

Si native conversation starts requieren writer NSD:

- modificar únicamente NSD generado por RCM
- nunca original NSD
- preservar campos desconocidos
- validar counts
- validar índices
- fail closed
- roundtrip generado

NO declarar un codec NSD universal.

Si no se puede demostrar el formato suficientemente:

    NO ESCRIBIRLO.

Mantener Entry staging.

Documentar:

    native convstart unsupported because safe binary authoring
    could not be demonstrated

Custom Java continúa como escape hatch.

----------------------------------------------------------------------
3.5 API NATIVA
----------------------------------------------------------------------

Si se implementan native convstarts:

usar realmente:

    CodexPlayer.TeleportPartyToConversation(...)

NO sustituirlo por SetPosition manual si el engine ya proporciona
la operación semántica.

----------------------------------------------------------------------
3.6 ACCEPTANCE
----------------------------------------------------------------------

EMB-CONV-01
    Conversation staging usando Entry actual.

EMB-CONV-02
    Native conversation staging si se implementa.

Comparar:

- player position
- party position
- orientation
- formation
- camera framing
- collision
- conversation start

EMB-CONV-03
    Save/load antes y después.

EMB-CONV-04
    Fin/cancelación de conversación devuelve control correctamente.

EMB-CONV-05
    Travel / return / repeat sin drift ni acumulación.

======================================================================
4. FLECO C
NCP — STATIONARY ROTATION / HOLD KEYS
======================================================================

Durante la revisión del catálogo NCP apareció una diferencia relevante.

Hay NCP originales con:

    posición A == posición B

pero:

    orientación A != orientación B

También existen secuencias de keys repetidas.

Esto podría representar:

- pan en posición fija
- tilt en posición fija
- giro de cámara
- hold
- salto instantáneo
- comportamiento interno del spline original

Actualmente el writer RCM rechaza dos puntos consecutivos si tienen
la misma posición.

NO eliminar esta validación sin investigar.

----------------------------------------------------------------------
4.1 AUDITAR ORIGINALES
----------------------------------------------------------------------

Buscar todos los NCP con:

- XYZ iguales
- XYZ casi iguales
- Euler diferente
- Euler igual
- parameter igual
- parameter diferente

Clasificar.

Inspeccionar especialmente:

    oldtownday.ncp
    prague_3_3_bed.ncp

y cualquier otro caso relevante.

Analizar:

- parameter
- next parameter
- inverse span
- cubic coefficients
- orientation polynomial
- neighbouring segments

----------------------------------------------------------------------
4.2 ESTUDIAR EL EVALUADOR NATIVO
----------------------------------------------------------------------

Determinar qué hace el engine cuando:

    spatial distance = 0

pero la orientación cambia.

Comprobar:

- si orientation contribuye al path parameter
- si el native writer aplica minimum span
- si repeated parameter implica transición instantánea
- si son artefactos del writer original
- si representan hold frames
- si se saltan claves duplicadas
- si existe otro mecanismo temporal

NO inventar semántica temporal.

----------------------------------------------------------------------
4.3 DECISIÓN
----------------------------------------------------------------------

Si el comportamiento puede demostrarse:

permitir de forma segura:

    dos camera points en la misma posición
    con orientación distinta

y documentar exactamente qué significa.

UX natural:

    Punto 1
    Punto 2 — misma posición, orientación distinta

No añadir un botón especial “Stationary Rotate” si no hace falta.

Si el formato necesita un parameter span no derivable de la geometría:

NO inventar un número arbitrario.

Buscar primero el comportamiento del native writer.

Si no puede demostrarse de forma segura:

mantener la restricción actual.

Documentar explícitamente:

    RCM authored NCPs support translation + orientation changes,
    but not native stationary-rotation sequences.

Eso NO debe bloquear el producto.

----------------------------------------------------------------------
4.4 TESTS
----------------------------------------------------------------------

Automático:

- detectar ejemplos originales con position equality
- original NCP lossless roundtrip
- authored NCP validation
- invalid path rejection
- parameter validation
- NaN/Inf
- maximum 128 keys

Si se implementa:

EMB-NCP-01
    Static camera — 1 key.

EMB-NCP-02
    Translation.

EMB-NCP-03
    Translation + yaw.

EMB-NCP-04
    Same position + orientation change.

EMB-NCP-05
    Hold/repeated key behaviour si queda demostrado.

======================================================================
5. CLEANUP DOCUMENTAL
======================================================================

Esta fase es de cierre.

La documentación actual NO puede contradecir HEAD.

Buscar referencias obsoletas.

Comprobar específicamente:

    482 PASS

cuando la última closure delivery reportó:

    508 tests
    0 failures
    0 errors
    0 skipped

Pero NO copies 508 automáticamente.

Primero ejecutar la suite final.

Usar el resultado NUEVO.

Revisar:

- README.md
- RELEASE_NOTES.md
- docs/TESTING.md
- docs/MANUAL_RUNTIME_CHECKLIST.md
- docs/FINAL_PRODUCT_REPORT.md
- docs/EMBRACE_AUTHORING_PARITY.md
- docs/FORMAT_NOTES.md
- docs/ENGINE_NOTES.md

Buscar afirmaciones actuales como:

    NCP writer missing
    NCP writer incomplete
    camera XYZ not implemented
    482 tests
    RC4 current
    RC5 current
    old Cinematic Director limitations

Actualizar documentación ACTUAL.

NO reescribir documentos históricos si están claramente marcados como
históricos.

======================================================================
6. NO MENTIR SOBRE EL 100 %
======================================================================

Separar SIEMPRE:

    IMPLEMENTED

    OFFLINE VERIFIED

    COMPILED AGAINST REAL CODEX

    PACKAGED

    DEPLOYED

    MANUAL RUNTIME TEST REQUIRED

    RUNTIME VERIFIED

    RUNTIME FAILED

No decir:

    100% Embrace parity

porque la geometría está deliberadamente excluida.

No decir:

    fully runtime verified

sin prueba real del usuario.

Antes de las pruebas nativas, el máximo claim aceptable es:

    All material non-geometry authoring gaps identified in the
    Embrace closure audit have either been implemented using
    evidenced native mechanisms, covered by an existing RCM
    abstraction, or explicitly documented where the native
    behaviour could not safely be authored.

======================================================================
7. QUALITY GATE FINAL
======================================================================

Ejecutar:

- full test suite
- Ruff
- mypy scope configurado
- real Java compilation against Codex
- classfile 45.3 verification
- package build
- export/import
- Safe Delete
- References
- Undo/Redo
- project format 9
- project format 10
- tutorial regression
- mini chronicle regression
- Dynamic Lab regression
- Showcase regression
- director_acceptance build
- portable EN
- portable ES
- restricted PATH
- moved folder / spaces / unicode si pipeline lo soporta
- original resource hashes unchanged

Registrar nuevo resultado autoritativo:

    TESTS
    FAILURES
    ERRORS
    SKIPPED

Actualizar documentación usando ESOS números.

======================================================================
8. PROJECT FORMAT
======================================================================

NO subir project format.

Debe continuar:

    CURRENT_PROJECT_FORMAT = 10

salvo imposibilidad técnica real demostrada.

No parece necesario.

Music stack:

    normal Actions.

Conversation staging:

    9/10 si puede implementarse de forma segura.

Camera path:

    resources.camera_paths existente.

======================================================================
9. UI
======================================================================

NO nueva pestaña.

NO panel “Advanced Embrace”.

NO raw engine editor.

Ubicación natural:

    Push/Pop Music
        → Actions

    Conversation staging
        → Conversation properties

    Camera path improvements
        → existing Camera Path dialog

Mantener progressive disclosure.

======================================================================
10. FINAL FLECKS AUDIT
======================================================================

Crear:

    research/embrace_closure/FINAL_FLECKS_AUDIT.md

Para cada uno:

    PushMusic / PopMusic

    Native conversation staging

    Stationary NCP orientation

documentar:

- evidencia original
- estado previo RCM
- decisión
- implementación
- limitaciones
- native test required

======================================================================
11. PARITY MATRIX FINAL
======================================================================

Actualizar:

    docs/EMBRACE_AUTHORING_PARITY.md

Cada capacidad relevante debe quedar como:

    COVERED

    COVERED DIFFERENTLY

    PARTIAL

    OUT OF SCOPE — GEOMETRY

    NATIVE TEST REQUIRED

No inflar claims.

======================================================================
12. MANUAL ACCEPTANCE
======================================================================

Mantener:

    EMB01–24
    DYN01–12

Añadir los casos nuevos sin romper numeración histórica.

Por ejemplo:

    EMB-MUSIC-01..03
    EMB-CONV-01..05
    EMB-NCP-01..05

No ejecutar automáticamente Redemption.

El usuario realiza aceptación nativa.

======================================================================
13. FEATURE-CREEP KILL SWITCH
======================================================================

Durante la investigación aparecerán otras APIs.

NO IMPLEMENTARLAS salvo que TODAS estas condiciones sean ciertas:

1. Existe evidencia fuerte.
2. Tiene uso material para una crónica normal.
3. El juego original la usa significativamente.
4. RCM no tiene equivalente razonable.
5. Encaja en arquitectura existente.
6. No requiere interpretación binaria especulativa.
7. Puede probarse de forma segura.

Si no:

    DOCUMENTAR Y PARAR.

NO añadir sistemas por:

- curiosidad
- nostalgia
- nombres interesantes en la API
- debug commands
- unused methods
- editor-only geometry controls
- undocumented raw engine knobs
- lightmap tools
- obscure network internals
- unknown binary structures

======================================================================
14. FINAL PRODUCT TEST
======================================================================

Al terminar, comprobar si RCM puede representar desde UI esta escena:

    El jugador pulsa una puerta original.

    La party se coloca para una conversación.

    Elena habla.

    Cámara close-up.

    El guardia mira a Elena.

    Hace un gesto.

    Entra música dramática temporal.

    La cámara realiza un travelling creado por RCM.

    Suena audio espacial.

    Fade.

    Se restaura la música anterior.

    Aparecen enemigos.

    Se actualiza la quest.

    Se viaja a la siguiente escena.

TODO:

    SIN EMBRACE

    SIN EDITAR JAVA

    SIN EDITAR NCP A MANO

    SIN TOCAR GEOMETRÍA

Si esto puede hacerse mediante el flujo normal de RCM:

    EL OBJETIVO ESTÁ CUMPLIDO.

======================================================================
15. PREGUNTAS FINALES OBLIGATORIAS
======================================================================

El informe final debe responder explícitamente:

1. ¿Existe alguna capacidad MATERIAL no geométrica de Embrace,
   necesaria para crear una crónica normal, que RCM todavía no cubra?

2. Si sí:
      ¿cuál exactamente?

3. Si no:
      declararlo claramente,
      separando authoring coverage de runtime verification.

4. ¿Qué pruebas manuales siguen pendientes?

5. Informar:

      tests
      failures
      errors
      skipped

      Java class version

      original resource integrity

      portable verification

      native game verification

      independent machine verification

======================================================================
16. DEFINITION OF DONE
======================================================================

La fase acaba cuando:

- PushMusic/PopMusic ha sido investigado y resuelto.
- Conversation staging ha sido investigado y resuelto.
- Stationary NCP keys han sido investigadas y resueltas/documentadas.
- No quedan contradicciones actuales en docs.
- No se ha creado feature creep.
- No se ha tocado geometría.
- Formats 9/10 siguen compatibles.
- Suite completa pasa.
- Real Codex compilation pasa.
- Portable pasa.
- Original assets siguen intactos.
- Toda feature nueva conserva:
      References
      Safe Delete cuando corresponda
      Undo/Redo
      validation
      packaging
      trace
      fail closed
- Todo comportamiento nativo no probado continúa marcado:
      MANUAL RUNTIME TEST REQUIRED

======================================================================
17. CUÁNDO PARAR
======================================================================

Si después de esta auditoría los únicos huecos restantes pertenecen a:

    geometry
    CSG
    brushes
    structural sectors
    portals
    UV
    texturing
    lightmaps
    level construction

PARAR.

NO CREAR OTRA FASE.

NO BUSCAR MÁS FEATURES.

NO HACER “RC7 PORQUE YA QUE ESTAMOS”.

RCM estará terminado cuando permita CREAR LA CRÓNICA.

No cuando replique cada botón de Embrace.

======================================================================
MANTRA FINAL
======================================================================

NO REHAGAS EMBRACE.

HAZ QUE EMBRACE DEJE DE HACER FALTA.

CIERRA LOS HUECOS DEMOSTRADOS.

NO INVENTES COMPORTAMIENTO DEL MOTOR.

NO TOQUES GEOMETRÍA.

NO DECLARES RUNTIME VERIFIED
HASTA QUE EL USUARIO LO HAYA VISTO FUNCIONAR.

Y CUANDO LOS ÚNICOS HUECOS RESTANTES SEAN LEVEL DESIGN:

                         PARA.
======================================================================