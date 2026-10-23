"""
El cuarto de Breyner — aparece entre cada recuerdo. Autoguarda al entrar,
muestra lo que ya se ha encontrado (polaroids en el corcho, ítems en el
escritorio) y da un par de objetos examinables con trasfondo opcional.
No depende de scenes.py (evita import circular): scenes.py decide cuándo
mostrar el cuarto y qué pasa al salir; este módulo solo dibuja y reacciona.
"""
import pygame
import config
import save_system
from engine import ui, movement, audio
from engine import drawing as _drawing
from engine.drawing import rect, circle, gradient_rect, tile_ground, draw_walk_character
from engine.constants import W, H, PALETTE_BREYNER, font

anim_frame = 0
_on_continue = None


def _entry_line(next_index):
    if next_index == 1:
        return config.tr(
            'Antes de salir, {b} se quedó un momento mirando sus cosas. Si iba a recordarlo todo, '
            'mejor empezar por algún lado.',
            'Before heading out, {b} stood there a moment, looking at his things. If he was going '
            'to remember it all, he might as well start somewhere.')
    if next_index == 7:
        return config.tr(
            'Solo quedaba un recuerdo. El más difícil de soltar.',
            'Only one memory was left. The hardest one to let go of.')
    return config.tr('Otro recuerdo más lo esperaba.', 'Another memory was waiting for him.')


def setup(next_index, on_continue):
    global _on_continue, anim_frame
    ui.clear_hotspots()
    audio.start_ambient(150)
    movement.enable_movement(460, 540, {'minX': 160, 'maxX': 820, 'groundY': 540})
    ui.hint_text = config.tr('\u2190 \u2192 / A D para moverte \u00b7 toca la puerta para seguir',
                              '\u2190 \u2192 / A D to move \u00b7 tap the door to continue')
    _on_continue = on_continue

    save_system.save_game(next_index)

    def notebook():
        ui.queue_dialogue([{'speaker': '', 'text': config.tr(
            'Un cuaderno lleno de notas a medio terminar. En una página, sin fecha: '
            '"Espero que algún día esto tenga sentido para alguien más, no solo para mí."',
            'A notebook full of half-finished notes. On one undated page: "I hope someday '
            'this means something to someone besides me."')}])
    ui.add_hotspot(150, 368, 50, 30, config.tr('El cuaderno', 'The notebook'), notebook)

    def family_photo():
        ui.queue_dialogue([{'speaker': '', 'text': config.tr(
            'Una foto de la familia en Ibarra, de hace años. {b} sonríe ahí sin saber '
            'todavía nada de lo que vendría.',
            'A family photo from Ibarra, years ago. {b} is smiling in it, not knowing yet '
            'what was coming.')}])
    ui.add_hotspot(640, 258, 46, 40, config.tr('Una foto vieja', 'An old photo'), family_photo)

    def window():
        ui.queue_dialogue([{'speaker': '', 'text': config.tr(
            'Desde la ventana se ve la misma calle de siempre. Nada cambió afuera, aunque '
            'adentro todo se sienta distinto.',
            "From the window, the same street as always. Nothing's changed outside, even "
            "though everything feels different inside.")}])
    ui.add_hotspot(100, 70, 110, 110, config.tr('La ventana', 'The window'), window)

    def seguir():
        movement.disable_movement()
        cb = _on_continue
        ui.fade_out(lambda: cb())
    ui.add_hotspot(860, 360, 70, 200, config.tr('Salir', 'Leave'), seguir)

    ui.queue_dialogue([{'speaker': '', 'text': _entry_line(next_index)}])


def _draw_desk_items(surf, x, y, w):
    """Dibuja en miniatura, en fila, los ítems ya recogidos."""
    items = ui.inventory
    if not items:
        return
    spacing = min(34, max(18, w // max(1, len(items))))
    start_x = x + (w - spacing * (len(items) - 1)) // 2
    for i, item in enumerate(items):
        ix = start_x + i * spacing
        rect(surf, ix - 11, y - 11, 22, 22, (36, 30, 44), outline=True)
        _blit_center(surf, font('icon_small'), item['icon'], (ix, y), (244, 233, 216))


def _draw_corkboard(surf, x, y, w, h):
    rect(surf, x, y, w, h, (90, 69, 48), outline=True)
    cols, rows = 3, 2
    cell_w, cell_h, gap = (w - 16) // cols, (h - 16) // rows, 4
    for i in range(1, 7):
        p = next((pp for pp in ui.polaroids if pp['scene'] == i), None)
        col, row = (i - 1) % cols, (i - 1) // cols
        cx = x + 8 + col * (cell_w + gap)
        cy = y + 8 + row * (cell_h + gap)
        if p:
            thumb = pygame.Surface((cell_w, cell_h))
            try:
                p['draw'](thumb, cell_w, cell_h)
            except Exception:
                thumb.fill((26, 22, 34))
            surf.blit(thumb, (cx, cy))
            pygame.draw.rect(surf, (244, 236, 224), (cx, cy, cell_w, cell_h), width=1)
        else:
            rect(surf, cx, cy, cell_w, cell_h, (58, 44, 34))


def _blit_center(surf, fnt, text, center, color):
    t = fnt.render(text, True, color)
    surf.blit(t, t.get_rect(center=center))


_ROOM_BACKGROUND = None


def draw(surf):
    """Fondo ilustrado del cuarto; conserva a Breyner como sprite jugable."""
    global anim_frame, _ROOM_BACKGROUND
    anim_frame += 1
    if _ROOM_BACKGROUND is None:
        path = __import__('os').path.join(__import__('os').path.dirname(__file__),
                                         'assets', 'backgrounds', 'cuarto_breyner.png')
        try:
            _ROOM_BACKGROUND = pygame.image.load(path).convert()
            _ROOM_BACKGROUND = pygame.transform.smoothscale(_ROOM_BACKGROUND, (W, H))
        except (pygame.error, OSError):
            _ROOM_BACKGROUND = False
    if _ROOM_BACKGROUND:
        _drawing.set_pixelate(False)
        surf.blit(_ROOM_BACKGROUND, (0, 0))
    else:
        # Respaldo visual sencillo si el PNG no está disponible.
        gradient_rect(surf, 0, 0, W, H, (39, 31, 52), (99, 57, 55))
        tile_ground(surf, 0, 420, W, H - 420, (92, 64, 52), (76, 52, 44), tile_size=30)
    # El personaje se dibuja por separado para que siga siendo jugable.
    draw_walk_character(surf, movement.player.x, movement.player.y, movement.player.scale,
                        PALETTE_BREYNER, movement.player.facing, movement.player.walk_frame,
                        movement.player.moving, anim_frame)
