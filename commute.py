"""
El recorrido real: bus desde la parada cerca del colegio (UTN) hasta la
casa de Cristel en Ambato 348, Ibarra. Se repite completo cada vez que
Breyner va a su casa (antes de las escenas 2, 3 y 6). No importa scenes.py
(mismo patrón que room.py, evita import circular).
"""
import math
import pygame
import config
from engine import ui, movement, audio
from engine import drawing as _drawing
from engine.drawing import rect, circle, gradient_rect, tile_ground, draw_walk_character
from engine.constants import W, H, PALETTE_BREYNER, font

anim_frame = 0
_on_arrive = None
_phase = 'stop'   # 'stop' | 'walk'
_bus_t = 0        # para animar la llegada del bus
_BACKGROUND_CACHE = {}

def _load_background(name):
    if name not in _BACKGROUND_CACHE:
        import os
        path = os.path.join(os.path.dirname(__file__), 'assets', 'backgrounds', name)
        try:
            image = pygame.image.load(path).convert()
            _BACKGROUND_CACHE[name] = pygame.transform.smoothscale(image, (W, H))
        except (pygame.error, OSError):
            _BACKGROUND_CACHE[name] = False
    return _BACKGROUND_CACHE[name]


def setup(on_arrive):
    global _on_arrive, _phase, anim_frame, _bus_t
    anim_frame = 0
    _bus_t = 0
    _on_arrive = on_arrive
    _phase = 'stop'
    ui.clear_hotspots()
    movement.disable_movement()
    audio.start_ambient(175)

    def board_bus():
        ui.queue_dialogue([{'speaker': '', 'text': config.tr(
            '{b} subió al bus en la parada de siempre.',
            '{b} got on the bus at the usual stop.')}], _start_walk)

    ui.queue_dialogue([{'speaker': '', 'text': config.tr(
        'La parada de siempre, junto al colegio. El mismo camino de cada vez hacia la casa de {c}.',
        "The usual stop, next to the college. The same route as always, toward {c}'s house.")}],
        board_bus)


def _start_walk():
    global _phase
    _phase = 'walk'
    ui.clear_hotspots()
    movement.enable_movement(100, 540, {'minX': 100, 'maxX': 860, 'groundY': 540})
    ui.hint_text = config.tr('\u2190 \u2192 / A D para caminar hasta la casa de {c}',
                              "\u2190 \u2192 / A D to walk to {c}'s house")

    def llegada():
        movement.disable_movement()
        cb = _on_arrive
        ui.fade_out(lambda: cb())
    movement.add_pickup_zone(820, 540, 40, 'llegada-casa', '\U0001F3E0',
                              config.tr('La casa de {c}', "{c}'s house"), llegada, False)


def _draw_bus_stop(surf):
    """Parada ilustrada; el personaje y el autobús animado se dibujan aparte."""
    global _bus_t
    _bus_t += 1
    background = _load_background('parada_bus.png')
    if background:
        _drawing.set_pixelate(False)
        surf.blit(background, (0, 0))
    else:
        gradient_rect(surf, 0, 0, W, H, (66, 91, 143), (255, 145, 103))
        tile_ground(surf, 0, 440, W, H - 440, (92, 88, 99), (65, 61, 77), tile_size=30)
    # Un bus sencillo se acerca desde la izquierda sin tapar el refugio.
    bus_x = min(40, -260 + _bus_t * 1.4)
    rect(surf, bus_x, 405, 150, 54, (151, 56, 65), outline=True)
    rect(surf, bus_x + 10, 414, 38, 24, (119, 174, 204), outline=True)
    rect(surf, bus_x + 54, 414, 38, 24, (119, 174, 204), outline=True)
    circle(surf, bus_x + 34, 461, 10, (25, 23, 32), outline=True)
    circle(surf, bus_x + 121, 461, 10, (25, 23, 32), outline=True)
    draw_walk_character(surf, 400, 540, 1.6, PALETTE_BREYNER, 'right', 0, False, anim_frame)


def _draw_walk(surf):
    """Camino ilustrado hacia la casa de Cristel, con movimiento independiente."""
    background = _load_background('camino_cristel.png')
    if background:
        _drawing.set_pixelate(False)
        surf.blit(background, (0, 0))
    else:
        gradient_rect(surf, 0, 0, W, 320, (73, 92, 145), (255, 157, 106))
        tile_ground(surf, 0, 500, W, H - 500, (92, 86, 91), (65, 60, 73), tile_size=28)
    movement.draw_pickup_zones(surf, anim_frame, {'circle': circle, 'font': font('icon')})
    draw_walk_character(surf, movement.player.x, movement.player.y, movement.player.scale,
                        PALETTE_BREYNER, movement.player.facing, movement.player.walk_frame,
                        movement.player.moving, anim_frame)

def draw(surf):
    global anim_frame
    anim_frame += 1
    if _phase == 'stop':
        _draw_bus_stop(surf)
    else:
        _draw_walk(surf)
