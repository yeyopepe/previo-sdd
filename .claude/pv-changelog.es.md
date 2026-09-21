# Changelog de Previo v0.9.8b4 (desde v0.9.7)

## Índice

- ✏️[Cambios](#cambios)
  - `pv-update` ahora detecta sintaxis de marcadores de plantilla sin resolver en los documentos generados

## ✏️Cambios

- **`pv-update` ahora detecta sintaxis de marcadores de plantilla sin resolver en los documentos generados** — una nueva comprobación detecta cuando un `description.md`/`plan.md` conserva la sintaxis literal `[[[...]]]` alrededor de una etiqueta (por ejemplo, `**[[[Name]]]**` en vez de `**Name**`), lo que ocurría cuando el modelo copiaba literalmente la notación interna de la plantilla en vez de escribir solo la etiqueta que envuelve. `pv-update` lo corrige automáticamente eliminando los corchetes.
