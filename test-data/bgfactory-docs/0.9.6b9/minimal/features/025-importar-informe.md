# 025 — Informe de importacion y migracion de guardados

**Area**: Persistencia e intercambio

Ante conflictos de identificadores o referencias rotas durante una importacion se muestra un informe detallado, fila por fila: un recurso ausente se descarta y el componente se anade sin el, y una etiqueta ausente se crea automaticamente o se vincula a otra ya existente con el mismo nombre. Los guardados y ficheros de versiones anteriores de la aplicacion se migran automaticamente al formato actual, sin bloquear el arranque.

- **Available in**: Importacion
- **Code**: init
- **Since**: 2026-08-28
- **Last modified**: 2026-08-28
