# Checklist de experiencia de autoría · 0.9.0

YES indica capacidad de RCM comprobada en el alcance indicado, no aceptación nativa general. PARTIAL señala subconjunto o aceptación pendiente. NO identifica hueco de RCM; no implica imposibilidad del motor. No se usa NOT SUPPORTED BY ENGINE para funciones cuya ausencia sólo conocemos en nuestro editor.

| Capacidad | Estado | Alcance / evidencia |
|---|---|---|
| Nueva campaña sin conversión manual | YES | Qt desde diálogo vacío; formato 9, ID máximo 14 |
| Escenas independientes sobre geometría reutilizada | YES | NSC/NSD propios; circuito quay/return comparten EastLondon |
| NPC/objetos colocados en 3D | YES | Clic real sobre NIL, suelo, transforms y compilación; colisión nativa pendiente |
| Entradas nombradas, movibles y orientables | PARTIAL | GUI y lógica probadas; SetPosition tras Jump, no escritor de tablas nativas |
| Transición con escena y llegada elegidas | PARTIAL | Selectores, referencias, flags y compilación 45.3; prueba nativa pendiente |
| Conversaciones y ramas con decisiones | PARTIAL | Autoría existente, feedback y auto cámara; aceptación completa 0.9.0 pendiente |
| Quest, item, recompensa y estado | PARTIAL | Journal nativo generado y lógica con doubles; circuito curado listo, save/load nativo pendiente |
| Encuentros y combate | PARTIAL | Grupo de cuatro enemigos opcional; ataques/dificultad de esta revisión sin verificar |
| Triggers orientados / esfera | PARTIAL | Matemática y edge polling 150 ms; no sustituyen todos los callbacks de regiones |
| Paths con orden y loop | PARTIAL | Clic de waypoints, GUI, overlay, navegación Codex, save/restore de índice; pendientes colisiones y timing nativos |
| Movimiento de puertas existentes | PARTIAL | Frames/pivote diferenciados según scripts originales; requiere Cast ID real, script de clic no sustituido |
| Exits originales | PARTIAL | IsExitValid + OpenExit/CloseExit; sin editor completo de enlaces/llaves |
| Borrar/reemplazar selectivamente contenido estático | NO | Static NSD del NIL se carga aparte; no override fiable implementado |
| Inspector de originales | PARTIAL | Hints readonly, fuente/confianza; no parser completo de entidades estáticas |
| NOT propio sin NOT Editor | PARTIAL | Writer restringido, herencia/copia/readback, actor e item propios; prueba nativa B3 pendiente |
| AI legible | PARTIAL | NPC/enemy, pausa, presets sobre escalares reales de NAI; no árbol completo |
| Cámara narrativa | PARTIAL | Presets SDK: speaker/listener/OTS/two shot/medio/entero; encuadre nativo pendiente |
| Create Camera From View / Align View | NO | NCP investigado; layout completo y conversión de orientación sin cerrar |
| Sonido situado | PARTIAL | One-shot en waypoint, radios/volumen; sin loop espacial persistente |
| Música / ambiente de escena | PARTIAL | APIs reales y catálogo; audición del circuito pendiente |
| Perfil de entorno original | YES | Preserva bloque completo NSD; no controles opacos fog/lightmap |
| Generar/compilar/paquete sin autoría antigua | YES | NOB/NSC/NMF/NSD/NOT/NCO/NVO/NLS/NQD/WAV + Java45.3 |
| Logs → elemento editable | YES | Acción/conversación/quest y callbacks de persistencia identificados |
| Build/deploy repetible | YES | Fingerprints, readback, ownership, backup y rollback; archivos ajenos conservados |
| Save/load y reentrada jugables | PARTIAL | Firma versionada y lógica comprobadas; B2 nativo sigue abierto |
| Portable sin Python/JDK globales | PARTIAL | Rebuild 0.9.0 y prueba local aparte; VM/equipo independiente sigue pendiente |
| Una aventura completa creada por humano sólo GUI | PARTIAL | Proyecto básico creado con widgets/clic real. Circuito completo es fuente curada; ensayo humano completo pendiente |
| Multijugador real host/client | NO | Una sesión local Multiplayer no demuestra varios clientes |
| Geometría nueva | NO | Fuera de alcance por decisión del producto; no es una afirmación sobre límites del motor |

La herramienta aún no puede anunciar paridad completa ni versión 1.0. [Madurez y bloqueos](AUTHORING_MATURITY_REPORT.md).
