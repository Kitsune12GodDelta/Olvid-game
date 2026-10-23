# Fondo de la escena 1 — Olvido

`../backgrounds/escuela_atardecer.png` ahora contiene el fondo detallado de la escena 1, ajustado a 960 × 600 para la resolución lógica del juego. El archivo `escuela_atardecer.backup.png` conserva el fondo previo. La imagen original de alta resolución se conserva en `escuela_atardecer_detallado_original.png`.

El fondo no incluye personajes, diálogos ni interfaz. `scenes.py` mantiene la lógica de movimiento, los hotspots, los sprites y los diálogos.

Nota: la adaptación a 960 × 600 se hace mediante recorte centrado para llenar la pantalla sin deformar la imagen.


## Fondos intermedios incorporados

- `cuarto_breyner.png`: fondo del cuarto; se carga desde `room.py`.
- `parada_bus.png`: parada al atardecer; se carga desde `commute.py`.
- `camino_cristel.png`: camino residencial hacia la casa de Cristel; se carga desde `commute.py`.
- `colegio_dia_concepto.png`, `parque_avion.png` y `porton_noche_concepto.png`: referencias visuales preparadas para una integración posterior.

Los tres primeros son recortes limpios de la lámina conceptual, sin los títulos. Se escalan al lienzo lógico 960×600; los personajes y los diálogos continúan siendo capas separadas. Se conservan los fondos y el código anteriores en el ZIP de respaldo original.
