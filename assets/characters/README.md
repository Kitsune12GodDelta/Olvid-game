# Personajes de Olvido — recursos integrados

Los recursos están separados del código de las escenas. Si falta un sprite, el motor conserva el dibujo geométrico anterior como respaldo.

## Carpetas

```text
assets/characters/
  breyner/
    overworld.png
    portrait.png
    portraits/normal.png, feliz.png, triste.png
  cristel/
    overworld.png
    portrait.png
    portraits/normal.png, feliz.png, sorprendida.png
  madre_cristel/
    overworld.png
    portrait.png
    portraits/normal.png, feliz.png, preocupada.png, sorprendida.png
```

## Sprites de exploración (`overworld.png`)

- PNG RGBA con transparencia.
- Hoja de 192 × 256 px, cuatro columnas por cuatro filas.
- Cada celda mide 48 × 64 px.
- Filas: frente/abajo, izquierda, derecha, espalda/arriba.
- Columnas: reposo, paso A, reposo alternativo, paso B.
- Los fotogramas de movimiento de la primera integración son variaciones sutiles de la pose base; deben refinarse con animación dibujada cuadro a cuadro antes de considerar las animaciones finales.

## Retratos

- `portrait.png` es el retrato predeterminado que aparece en los diálogos.
- `portraits/` guarda alternativas de expresión para ampliar más adelante el sistema de diálogo.
- Los retratos tienen un fondo ilustrado oscuro para mantener la estética de novela visual y evitar artefactos de transparencia del tablero conceptual.

## Integración

- `engine/character_assets.py` carga sprites y retratos.
- `engine/drawing.py` usa automáticamente el sprite de la paleta si está disponible y conserva el dibujo anterior como respaldo.
- `engine/ui.py` muestra el retrato correspondiente para Breyner, Cristel y la madre de Cristel cuando el nombre del hablante coincide.
- `PALETTE_MADRE_CRISTEL` está preparado en `engine/constants.py`; la madre no se inserta en ninguna escena hasta que la historia la requiera.

## Identidad visual

- **Breyner:** cabello negro, gafas rectangulares, sudadera roja, pantalón oscuro y zapatillas rojas/blancas.
- **Cristel:** cabello largo castaño oscuro, gafas grandes, uniforme azul marino, falda plisada, medias blancas y zapatos oscuros.
- **Madre de Cristel:** cabello castaño ondulado, cárdigan beige/rosado, blusa clara y pantalón oscuro.

`assets/concept_art/personajes_referencia_organizada.png` conserva la hoja de referencia completa. Los sprites de juego son recursos independientes, no se recorta esa lámina en tiempo de ejecución.

## Estado de revisión visual (fase 2)

- `breyner/overworld.png`: hoja activa, pendiente de prueba dentro del juego.
- `cristel/overworld.png`: hoja activa recuperada de respaldo; aún requiere revisión cuadro a cuadro.
- `madre_cristel/overworld.png`: hoja activa preparada desde el respaldo detallado. Se ajustó cada celda individualmente para centrar el personaje y mantenerlo dentro de 48×64 px usando escalado por vecino más cercano. La hoja anterior se conserva como `overworld.png.backup-before-autofit`.

La revisión automática confirma dimensiones y canal alfa, pero no certifica la calidad artística ni sustituye una prueba de movimiento con Pygame. Si una hoja no carga o tiene dimensiones insuficientes, el motor conserva el dibujo procedural de respaldo.

La hoja de Breyner permanece activa. Las hojas de Cristel y su madre no deben reactivarse hasta revisar cada celda de 48×64 y probar las cuatro direcciones en ejecución.
