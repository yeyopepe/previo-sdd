# 025 — Exportar e importar selectivo

**Area**: Persistencia

Permite mover componentes, recursos y etiquetas sueltos entre partidas en formato JSON, eligiendo exactamente qué llevarse. Al importar se decide entre añadir a lo existente o sobrescribir toda la partida, y cómo resolver ids duplicados (sobrescribir o conservar ambos). Ante conflictos de ids o referencias se muestra un informe detallado. También hay un aviso específico si un fichero importado trae contenido que no se pudo convertir.

- **Available in**: Modo edición
- **Code**: init
- **Since**: 2026-08-28
- **Last modified**: 2026-08-28
