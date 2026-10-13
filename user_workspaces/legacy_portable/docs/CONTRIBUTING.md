# Criterio de calidad para cambios

El workspace contiene las fuentes y la evidencia. La instalación original es de lectura; sólo RCM admite despliegue autorizado. Ninguna herramienta original de autoría puede introducirse en el flujo. La geometría no se genera ni modifica.

Antes de cambiar generadores o contratos, conserva la reproducción concreta del fallo. Añade una prueba que falle con el comportamiento anterior y que observe datos, referencias o salida relevantes; no una copia del algoritmo. Ejecuta `python tools/quality.py --fast` para lógica sintética y `python tools/quality.py` cuando intervengan modelos, formatos, Java, Qt o compilación.

El resultado debe separar pruebas de modelo/controlador, compilación contra Codex real, viewport OpenGL y observación nativa. Mantén `FEATURE_MATRIX`, `KNOWN_ISSUES` y `RUNTIME_TEST_MATRIX` acordes con esa evidencia. Un fallo nativo no queda cerrado por pasar un double. No declares estable el writer NOT ni compatible un save sin probarlo en Redemption.

`chronicles/golden/expected.json` fija la salida determinista de referencia. Los generadores de fixtures no reemplazan esa huella. Si cambia justificadamente, revisa diferencias de formatos y clases, comprueba el contrato, documenta la razón y modifica el baseline de forma explícita. No actualices expected para silenciar una regresión desconocida.

Revisa pérdidas de datos: Cancelar no debe guardar ni mutar; eliminación y renombrado deben conservar referencias o bloquearse; Save debe incluir buffers pendientes; fallo de build/deploy debe dejar un resultado reconocible y recuperable. No empaquetes cache, assets originales, configuraciones personales ni logs privados para distribución. Conserva avisos de las dependencias.

Antes de reconstruir el portable, conserva cualquier `workspace/` de usuario fuera de la carpeta reemplazada. La herramienta de build se detiene si encuentra uno. El EXE necesita su carpeta completa; su prueba local no sustituye un ensayo independiente en otro equipo.
