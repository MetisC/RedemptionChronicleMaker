# Instrucciones del proyecto

## Producto vigente

Petición vigente: cierre definitivo del alcance original según research/authoring_completion/FINAL_REQUIREMENTS.md, docs/AUTHORING_COMPLETION.md y docs/EMBRACE_AUTHORING_PARITY.md. El cierre del desarrollo admite alternativas funcionales suficientes; no exige compatibilidad universal con scripts privados de campaña ni código binario arbitrario. Mantener separada la aceptación dentro del juego. Trabajar en main y conservar los casos manuales pendientes sin declarar100% de aceptación nativa. Conservar RC4 Dynamic Encounters según docs/RC4_REQUIREMENTS.md. Investigar mecanismos originales antes de diseñar e implementar; añadir encuentros dinámicos encima de los existentes, sin reescribirlos. Formato 10 optativo, tutorial 9 intacto; Showcase sólo laboratorio opcional. Sin otra pestaña, geometría ni gameplay automatizado. Conservar seguridad y UX de RC3.

Redemption Chronicle Maker 1.0.0-rc10. La fase de cierre quedó completada en rc6; rc8 empaquetó el main auditado; rc9 mejoró la autoría de actores; rc10 añade escritura diferida, acciones de respuesta, reacciones a flags y enlaces contextuales de eventos. No incrementar de nuevo salvo petición explícita del usuario o cambios reales de producto. Conservar el tutorial aceptado en formato 9 y la mini crónica, así como el runtime que funciona. Showcase añade sólo un laboratorio dinámico optativo; dynamic_lab es independiente. No declarar 1.0 final mientras falten DYN01–12 y los casos manuales de docs/MANUAL_RUNTIME_CHECKLIST.md. Alcance/límites: docs/FINAL_PRODUCT_REPORT.md.

El usuario realiza las pruebas dentro de Redemption: no automatizar ni jugar el juego. Separar generación, compilación contra Codex, pruebas con doubles, pruebas de interfaz y observación nativa. La aceptación del tutorial no certifica automáticamente el Showcase, save/load ni multijugador.

## Autoría y archivos

- Generar formatos y Java mediante la API real. No ejecutar Embrace, NOT Editor, editores originales ni frontends del SDK. Pueden estudiarse archivos y documentación originales.
- La geometría original permanece inmutable. Las escenas, actores, historia y recursos propios son capas sobre ella.
- Código, herramientas, pruebas, documentación, recursos extraídos y builds permanecen en este workspace.
- Preservar los proyectos y recursos de usuario de user_workspaces/. No confundirlos con ensayos desechables.
- Petición actual: eliminar documentación histórica, versiones anteriores y restos sin uso, sin archivarlos ni conservar copias de lo retirado. Mantener únicamente documentación vigente y dependencias de ejecución, compilación y regresión. No reinstaurar carpetas de fases antiguas.

## Instalación de Redemption

La instalación H:\GOG\Vampire The Masquerade - Redemption es de lectura, excepto su carpeta RCM, que el usuario autorizó expresamente a actualizar. Verificar rutas resueltas y enlaces; comprobar que Vampire esté cerrado antes de sustituir recursos cargados. No modificar archivos fuera de RCM. Los despliegues conservan la propiedad de archivos y las referencias de inventario del jugador; no limpiar automáticamente perfiles ni carpetas ajenas.

Esta limpieza afecta sólo al workspace, no a la instalación del juego.

## Evidencia y regresiones

- El tutorial «Una carta al amanecer» fue confirmado por el usuario: docs/FINAL_PRODUCT_REPORT.md y research/native_acceptance/.
- EastLondon utiliza su entorno gris original. No añadir un cielo experimental como reparación sin petición o evidencia nueva.
- Las plantillas propias deben estar disponibles al restaurar inventarios antes de LAN; conservar el contrato de carga inicial y profile_compatibility.
- No alterar hashes de fixtures para ocultar regresiones. Los baselines vigentes están en tests/fixtures/.
- La calidad se comprueba con tools/quality.py y tools/test.py. Los resultados offline no sustituyen la verificación dentro del juego.

- Ejecutar tools/quality.py sin compilaciones independientes concurrentes en el mismo workspace: las pruebas de atomicidad comprueban que build/.staging quede vacía.
