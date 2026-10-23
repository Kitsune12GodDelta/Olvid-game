# Revisión de sprites — madre de Cristel

- Fuente: respaldo detallado `overworld.png.off.backup`.
- Salida: `assets/characters/madre_cristel/overworld.png`.
- Formato: PNG RGBA, 192×256 px; celdas 48×64 px.
- Acción: cada celda se recortó por su canal alfa y se ajustó proporcionalmente a un área máxima de 44×59 px con remuestreo NEAREST, centrada horizontalmente y alineada cerca de la base.
- Copia previa: `overworld.png.backup-before-autofit`.

Esta corrección busca evitar recortes de contenido entre celdas; no es un redibujo artístico ni una validación visual en ejecución. Debe revisarse dentro de Pygame antes de considerarla final.
