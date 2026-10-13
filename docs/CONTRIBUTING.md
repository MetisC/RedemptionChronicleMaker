# Criterio de calidad para cambios

Conservar el comportamiento aceptado y reproducir cada fallo antes de corregirlo. Añadir regresiones que observen resultados relevantes, sin copiar el algoritmo. Ejecutar tools/quality.py --fast para lógica sintética y la suite completa cuando cambien formatos, modelos, Java o Qt.

Separar análisis estático, compilación, doubles, interfaz y ensayo nativo. Mantener [KNOWN_ISSUES.md](KNOWN_ISSUES.md), [FINAL_PRODUCT_REPORT.md](FINAL_PRODUCT_REPORT.md) y [MANUAL_RUNTIME_CHECKLIST.md](MANUAL_RUNTIME_CHECKLIST.md) de acuerdo con esa evidencia.

Los baselines deterministas están en tests/fixtures. Revisar diferencias antes de actualizar una huella; no cambiar expected para silenciar una avería desconocida. Cancelar no debe guardar ni mutar; borrado y renombrado deben conservar referencias o bloquearse. Un fallo de build/deploy debe dejar un estado reconocible y recuperable.

No publicar recursos originales, configuraciones personales ni logs privados en la distribución del editor. Conservar avisos de dependencias. El portable necesita su carpeta completa; reconstruirlo no puede sobrescribir proyectos de usuario. Su ensayo local no acredita funcionamiento en otro equipo.

No acumular documentación de fases, paquetes retirados o herramientas de reparación de un solo uso. Conservar conocimiento técnico vigente, dependencias necesarias y pruebas útiles.
