# Estado actual de Olvido (revisión previa a publicar)

## Cambios de esta revisión
- `save_system.py`: usa `localStorage` en el navegador y archivo JSON en PC.
- `engine/audio.py`: 22050 Hz y frecuencia real del mezclador (menos trabajo en WASM).
- `engine/drawing.py`: los degradados se dibujan una vez y se copian (rendimiento); nuevo `set_pixelate()`.
- Fondos PNG (cuarto, parada, camino, escuela) se muestran sin pixelar; las demás escenas conservan el look retro.
- Animación de caminata: alterna cada 4 pasos (antes parpadeaba por paridad).
- Sprites de Cristel y de la madre desactivados (`overworld.png.off`, hojas sin torso); se usa el dibujo geométrico.
- Se movieron fuera del juego (`../_fuera_del_juego/`): arte conceptual, referencias de fondo sin usar y `tools/`.
- Fondos usados reducidos a 960x600; requirements sin Pillow.

## Pendiente
- Foto del epílogo: `assets/epilogue_cristel_photo.jpg` (sin ella se ve un degradado oscuro).
- Audio opcional: `assets/audio/melancolia.ogg` y `assets/audio/sollozos.ogg`.
- Hojas nuevas de Cristel y de la madre: 192x256 px, 4x4 celdas de 48x64, cuerpo completo,
  filas abajo/izquierda/derecha/arriba. Al tenerlas, guárdalas como `overworld.png`.
- Probar en navegador (escritorio y celular): carga, toques, guardado/continuar, fluidez.
- Nada de esto se ha ejecutado todavía con Pygame.
