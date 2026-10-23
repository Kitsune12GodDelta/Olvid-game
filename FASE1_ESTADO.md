# Olvido — Estado de la fase 1: sprites

## Estado actual verificado

- El motor espera hojas de 192×256 px divididas en celdas de 48×64 px.
- `breyner/overworld.png` está activo y tiene canal alfa.
- `cristel/overworld.png.off` y `madre_cristel/overworld.png.off` se mantienen desactivados intencionalmente; no se reactivaron porque son hojas previas que necesitan revisión visual.
- Los retratos de los tres personajes están presentes.
- El motor conserva dibujo procedural como respaldo cuando no hay hoja activa para un personaje.
- `scene5_setup()` continúa presente y conserva las interacciones del marcador, la banca, el avión, el minijuego de dibujo y el desbloqueo del recuerdo.

## Pendiente antes de cerrar la fase

- Rehacer las hojas de Cristel y la madre con fotogramas limpios y coherentes.
- Revisar la hoja de Breyner para confirmar la correspondencia exacta entre filas, columnas y direcciones.
- Probar movimiento y diálogos dentro del juego con Pygame instalado.

## Importante

Las dimensiones correctas no garantizan que los fotogramas sean visualmente correctos. No se declara esta fase terminada hasta probar los personajes dentro del juego.


## Ajuste técnico añadido en esta revisión

- Unifiqué la selección de dirección y fotograma entre `engine/drawing.py` y `engine/character_assets.py`: las filas representan direcciones y las columnas representan fotogramas.
- La animación alterna entre las columnas de paso 1 y 3 usando la paridad del contador de fotogramas, evitando que un contador que avanza rápidamente deje el personaje demasiado tiempo en una sola pose.
- Esto corrige la lógica de selección, pero no certifica la calidad visual de cada celda. La prueba en Pygame sigue pendiente.
