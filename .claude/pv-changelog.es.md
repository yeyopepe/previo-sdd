# Changelog de Previo v0.9.8b4 (desde v0.9.7)

## Índice

- ⭐[Novedades](#novedades)
  - Checklist de progreso opcional durante un flujo
- ✏️[Cambios](#cambios)
  - `pv-update` ahora detecta sintaxis de marcadores de plantilla sin resolver en los documentos generados

## ⭐Novedades

- **Checklist de progreso opcional durante un flujo** — si `framework.skills.progress` está configurado (por ejemplo, con el nuevo `pv-internal-progress-todowrite`), `pv-new`, `pv-fix`, `pv-how` y `pv-do` ahora publican en la interfaz un checklist visible de sus pasos principales mientras se ejecutan, para que puedas ver en qué punto está el flujo sin tener que preguntar en el chat. Está desactivado por defecto: si no configuras `skills.progress`, el comportamiento anterior se mantiene exactamente igual, sin mostrar ningún checklist.

## ✏️Cambios

- **`pv-update` ahora detecta sintaxis de marcadores de plantilla sin resolver en los documentos generados** — una nueva comprobación detecta cuando un `description.md`/`plan.md` conserva la sintaxis literal `[[[...]]]` alrededor de una etiqueta (por ejemplo, `**[[[Name]]]**` en vez de `**Name**`), lo que ocurría cuando el modelo copiaba literalmente la notación interna de la plantilla en vez de escribir solo la etiqueta que envuelve. `pv-update` lo corrige automáticamente eliminando los corchetes.
