# Integración de escenarios — Olvido

## Fondos activos
- `assets/backgrounds/cuarto_breyner.png` — lo dibuja `room.py` durante la transición al cuarto.
- `assets/backgrounds/parada_bus.png` — lo dibuja `commute.py` durante la parada.
- `assets/backgrounds/camino_cristel.png` — lo dibuja `commute.py` durante el trayecto a pie.

Los fondos se escalan al lienzo lógico de 960×600. Los sprites de los personajes se siguen dibujando por encima, por separado; los diálogos, hotspots, guardado y transiciones existentes se conservan.

## Referencias no activadas todavía
`colegio_dia_concepto.png`, `parque_avion.png` y `porton_noche_concepto.png` son referencias limpias para próximas integraciones. No se sustituyeron todas las escenas de recuerdos para evitar cambiar mecánicas o fondos que aún no hemos validado en el teléfono.

## Prueba recomendada en Android/Acode
1. Extrae este ZIP en una carpeta nueva, sin sobrescribir el original.
2. Ejecuta `main.py` como de costumbre.
3. Avanza hasta el cuarto de Breyner; comprueba que el personaje se vea completo y que los puntos interactivos respondan.
4. Avanza hasta la parada y luego camina hasta la casa de Cristel.
5. Si Cristel vuelve a aparecer solo con la cabeza, envía una captura y revisaremos el recorte/escala del sprite por separado.
