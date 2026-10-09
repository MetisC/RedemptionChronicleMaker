# AI original: subconjunto de Fase 4

## Confirmado en archivos originales

136 NAI de Resource.nob inventariados con hash, texto y plantillas que los heredan: research/phase4/ai_profiles.json. Incluyen attackType/Flags/Rate, moveType/Flags/Dist/Rate, chaseDist/Rate, searchDist/Rate, behaviorClass, wanderRadius, mindFlags y filas discipline. Encontrar sus nombres no demuestra la semántica de cada valor.

Codex confirma SetActorTeam, Set/ClearActorFlags, AISetTarget, SendActorToPos, ActorActionAttack, AIGetMode y más firmas. El bytecode y las constantes se conservan en api_and_original_bytecode.txt.

## Implementado

Actor: NPC neutral con AI pausada o Enemigo con TEAM_ENEMY0 y flags AIPAUSED/NEUTRAL desactivados. Se hereda el perfil NAI original mediante NOT propio; no se genera una AI nueva. Enable AI / Disable AI controla AIPAUSED. Encounter agrupa enemigos y expande creación/retirada a entidades normales.

Resource Browser → AI → Inspeccionar permite leer el archivo original; plantillas muestran el AI resuelto por herencia. Inspección es de lectura. No se ofrece un selector de perfiles que no se puedan aplicar correctamente.

## Inferido / pendiente

Team enemigo y AI nativa deberían producir combate con el jugador, pero requieren partida real. No se promete comportamiento idéntico al script de la plantilla original: nuestros hijos reemplazan su script por Passive para controlar callbacks propios. Algunas plantillas pueden depender de su script original; hay que verificarlas individualmente.

## No soportado

Autoría de NAI, equipos configurables completos, disciplinas, follow/guard/patrullas, waypoints y llegada. Firmas existentes de movimiento no equivalen a un editor de paths comprobado. No se ha creado un motor AI/RPG alternativo.
