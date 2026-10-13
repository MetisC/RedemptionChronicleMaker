# Auditoría del código y de las promesas

Inventario AST de todos los módulos Python de src/tools/tests: `research/phase6/code_inventory.json`, con SHA-256, clases, funciones y líneas. Constructos sospechosos: `suspicious_constructs.json`. Ruff y mypy tienen reportes reproducibles. La búsqueda automática es un inventario para revisión, **no certifica semánticamente cada función**.

Revisión de focos: modelo/shape/encoding/IDs; referencias y borrados; roundtrip/autosave/undo; generación por scene; callbacks/saves/conversaciones/cámaras; recursos propios y namespaces; build válido frente a fallo; publicación/rollback; rutas/junctions/hardlinks; catálogos/primer arranque; paquete y confianza; buffers Java; renderer/caches; CLI y doc histórica.

Constructos `pass`: catalogue omite del conjunto de roundtrip escenas con bloques variables que el codec no comprende; no las reescribe. Window omite referencias visuales a una selección antigua tras refresh, o preserva error original si falla el log. Service/build_transaction toleran fallo secundario de diagnóstico o report inexistente; el error real no se convierte en éxito. Fuzz de NOT acepta ValueError para bytes malformados. No se encontraron `NotImplementedError` usados como feature presentada al creador.

El `*_Passive extends Codex {}` generado es deliberado: evita ejecutar la lógica narrativa original heredada y recibe comportamiento por el controlador/click proxy. No es una implementación falsa de AI. El WAV de silencio sí es un recurso PCM generado para soporte de subtítulos, no voz sintetizada ni doblaje. Debug muestra logs observados; no lee estado vivo ni journal del motor.

Se eliminaron 47 imports sin uso y seis variables/cálculos sin efecto. No se aplicó formateo masivo. Static gate comprueba errores sintácticos/nombres/imports/locals; tipado limitado a tres módulos críticos nuevos, no a Qt completo. No se declaró la suite exhaustiva porque creció su número.

Huecos admitidos: storyboard derivado sin edición libre de grafo; NOT sólo tags contrastados y estructura contigua; AI sólo campos escalares conocidos; sin paths/waypoints; cámaras por actor/tipo/ángulo/duración sin timeline XYZ; puertas fuera del modelo; transiciones sin entrada espacial propia; objetivos de quest abstractos sobre flags/journal; release debug desactivado quita nuestra instrumentación de campaña, no controla logging de Java propio; no migración de saves nativos ni cancelación de compilación activa. Ver FEATURE_MATRIX y RELEASE_BLOCKERS.

La Fase 5 carecía de packaging/distribución y pruebas nativas completas. Se cubrieron esos huecos técnicos necesarios para comprobar Fase 6, sin iniciar nuevos editores ni Fase 7. Reader lossless, compilación de API y prueba simulada siguen separados de aceptación real del engine.
