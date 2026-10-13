# Quests de campaña

Fase 4 utiliza **CodexQuest.Load** y **Complete**, las mismas funciones que MP_CTDChronicle original. No necesita un editor de quests antiguo.

Campaña / Quests → + Quest: ID, título, descripción, pasos y XP al completar. Los eventos ofrecen Iniciar, Siguiente paso y Completar quest. Las condiciones permiten estado (sin iniciar, activa, completa) y paso activo, contado desde cero. Una respuesta se enlaza mediante un evento Termina conversación filtrado por su RETURN.

Cada quest produce un NQD de resumen y un NQD por paso, con `QUEST 0 0 <short> <long> QuestCheck.tga 0` y cadenas NLS propias. Se carga el resumen y primer paso al iniciar; avanzar completa la entrada del paso y carga la siguiente; completar exige todos los pasos y completa el resumen. XP se entrega explícitamente al jugador que dispara la acción. El reward del NQD es cero para evitar entregar dos recompensas.

**Límite explícito:** los pasos son entradas separadas del journal nativo. No se ha acreditado la gramática para varios objetivos con títulos distintos en un único NQD. No se ofrecen objetivos internos ficticios. El icono actual es QuestCheck.tga; no existe selector de iconos personalizado. Se rechazan campañas con más de 64 entradas incluyendo resumen y pasos, límite confirmado en Codex.

Los índices 0–255 son flags del autor. El compilador reserva 256–1023 para progreso/once y registra el contrato en build_report.json. Estado entre mapas deriva de esos Chronicle Flags; GUI y runtime usan el mismo orden de pasos. No editar el orden de quests/pasos de una campaña publicada si se pretende cargar partidas anteriores: todavía no hay migración de saves.

Compilación real y escenarios con doubles comprueban pasos, condiciones, aborto, recompensa única y restore. La presentación, persistencia y recompensa del journal dentro de Redemption siguen pendientes de partida nativa. Evidencia: research/phase4/api_and_original_bytecode.txt y build/tests/campaign_java/harness.log.
