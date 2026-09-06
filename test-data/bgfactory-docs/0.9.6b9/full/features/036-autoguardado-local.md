# 036 — Autoguardado local
**Area**: Persistencia e intercambio

Mientras se trabaja, todo el estado del juego (componentes, recursos, etiquetas, grupos, título y configuración de los paneles) se guarda automáticamente en el navegador tras cada cambio, sin que el usuario tenga que hacer nada. Al reabrir la aplicación en el mismo navegador se recupera exactamente donde se dejó.

Hay una única partida guardada por navegador y perfil. Si el navegador no puede guardar (por ejemplo por falta de espacio), el autoguardado se omite sin interrumpir el trabajo. Si el estado guardado no se puede recuperar, se avisa y se arranca con los recursos de ejemplo.

- **Available in**: Toda la aplicación (transparente para el usuario)
- **Code**: init
- **Since**: 2026-08-28
- **Last modified**: 2026-08-28
