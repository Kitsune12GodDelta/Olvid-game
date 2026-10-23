"""Minijuegos de Olvido con interfaz visual mejorada.

Se conserva la interfaz pública y la lógica de los minijuegos existentes para
no romper main.py ni las escenas: heartbeat, drawing y cube.
"""
import math
import random
import pygame
import config
from engine import audio
from engine.constants import W, H, font

mode = 'none'  # 'none' | 'heartbeat' | 'drawing' | 'cube'

# Paleta coherente con los escenarios cinematográficos de Olvido.
INK = (7, 13, 31)
NAVY = (13, 24, 49)
BLUE = (81, 119, 177)
PALE_BLUE = (166, 202, 239)
CREAM = (248, 232, 211)
PINK = (238, 139, 164)
GOLD = (255, 195, 119)
MUTED = (154, 169, 202)


def active():
    return mode != 'none'


def _rounded_panel(surf, rect, fill=(10, 18, 39, 232), border=BLUE, radius=16, width=2):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, fill, panel.get_rect(), border_radius=radius)
    surf.blit(panel, rect.topleft)
    pygame.draw.rect(surf, border, rect, width=width, border_radius=radius)
    inner = rect.inflate(-8, -8)
    if inner.width > 0 and inner.height > 0:
        pygame.draw.rect(surf, (255, 255, 255, 18), inner, width=1, border_radius=max(4, radius - 5))


def _draw_backdrop(surf, title, subtitle):
    """Overlay oscuro con degradado, estrellas y panel legible."""
    shade = pygame.Surface((W, H), pygame.SRCALPHA)
    shade.fill((5, 8, 20, 218))
    surf.blit(shade, (0, 0))
    # Halo suave detrás del contenido.
    glow = pygame.Surface((W, H), pygame.SRCALPHA)
    for radius, alpha in ((210, 8), (160, 10), (110, 13)):
        pygame.draw.circle(glow, (88, 119, 190, alpha), (W // 2, H // 2), radius)
    surf.blit(glow, (0, 0))
    # Pequeños destellos deterministas para evitar parpadeos.
    for i in range(42):
        x = (i * 137 + 31) % W
        y = (i * 83 + 19) % H
        r = 1 if i % 4 else 2
        pygame.draw.circle(surf, (105, 137, 194), (x, y), r)
    panel = pygame.Rect(int(W * .13), int(H * .09), int(W * .74), int(H * .82))
    _rounded_panel(surf, panel, (5, 12, 29, 235), (83, 119, 178), 18, 2)
    title_img = font('eyebrow').render(title.upper(), True, PINK)
    surf.blit(title_img, title_img.get_rect(center=(W // 2, panel.y + 34)))
    pygame.draw.line(surf, (72, 96, 146), (panel.x + 28, panel.y + 57), (panel.right - 28, panel.y + 57), 1)
    sub_img = font('small').render(subtitle, True, CREAM)
    surf.blit(sub_img, sub_img.get_rect(center=(W // 2, panel.y + 78)))
    return panel


def _heart_points(cx, cy, scale, n=22):
    pts = []
    for i in range(n):
        t = (i / n) * 2 * math.pi
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * scale, cy + y * scale))
    return pts


# 1) Ritmo del corazón
_hb_t0 = 0
_hb_beat = 0
_hb_total = 5
_hb_period = 950
_hb_on_complete = None


def start_heartbeat(on_complete):
    global mode, _hb_t0, _hb_beat, _hb_on_complete
    mode = 'heartbeat'
    _hb_t0 = pygame.time.get_ticks()
    _hb_beat = 0
    _hb_on_complete = on_complete


def _hb_phase(now):
    return ((now - _hb_t0) % _hb_period) / _hb_period


def _update_heartbeat(now):
    global _hb_beat
    completed = (now - _hb_t0) // _hb_period
    if completed > _hb_beat:
        _hb_beat = completed
        if _hb_beat >= _hb_total:
            _finish_heartbeat()


def _finish_heartbeat():
    global mode
    mode = 'none'
    cb = _hb_on_complete
    if cb:
        cb()


def _click_heartbeat(pos):
    now = pygame.time.get_ticks()
    phase = _hb_phase(now)
    if 0.32 < phase < 0.68:
        audio.play_match()
    else:
        audio.play_mismatch()
    return True


def _draw_heartbeat(surf):
    now = pygame.time.get_ticks()
    phase = _hb_phase(now)
    panel = _draw_backdrop(surf,
        config.tr('Ritmo del corazón', 'Heartbeat rhythm'),
        config.tr('Toca al compás y acompaña el momento', 'Tap in time and share the moment'))
    # Anillos pulsantes.
    pulse = .5 + .5 * math.sin(phase * math.tau)
    cx, cy = W // 2, H // 2 + 12
    for i in range(3):
        radius = int(54 + i * 24 + pulse * 8)
        pygame.draw.circle(surf, (63 + i * 9, 78 + i * 8, 128 + i * 8), (cx, cy), radius, 1)
    # Corazón vectorial para que no dependa de los glifos disponibles en la fuente.
    pts = _heart_points(cx, cy - 4, 5.0 + pulse * 1.0, 64)
    pygame.draw.polygon(surf, (100, 35, 65), [(int(x + 4), int(y + 5)) for x, y in pts])
    pygame.draw.polygon(surf, (226, 91 + int(pulse * 32), 126), [(int(x), int(y)) for x, y in pts])
    pygame.draw.polygon(surf, (255, 174, 184), [(int(x), int(y)) for x, y in pts], 2)
    # Progreso en cápsulas.
    bar_w, gap = 34, 12
    total_w = _hb_total * bar_w + (_hb_total - 1) * gap
    start_x = cx - total_w // 2
    y = panel.bottom - 65
    for i in range(_hb_total):
        r = pygame.Rect(start_x + i * (bar_w + gap), y, bar_w, 9)
        pygame.draw.rect(surf, (42, 54, 83), r, border_radius=5)
        if i < _hb_beat:
            pygame.draw.rect(surf, GOLD, r, border_radius=5)
        elif i == _hb_beat:
            pygame.draw.rect(surf, PINK, r, border_radius=5)
    hint = font('tiny').render(config.tr('Toca cualquier parte de la pantalla', 'Tap anywhere on the screen'), True, MUTED)
    surf.blit(hint, hint.get_rect(center=(cx, panel.bottom - 36)))


# 2) Dibuja el corazón
_dw_guide = []
_dw_visited = []
_dw_trail = []
_dw_held = False
_dw_on_complete = None


def start_drawing(on_complete):
    global mode, _dw_guide, _dw_visited, _dw_trail, _dw_on_complete, _dw_held
    mode = 'drawing'
    _dw_guide = _heart_points(W // 2, H // 2 + 6, 6.1, 36)
    _dw_visited = [False] * len(_dw_guide)
    _dw_trail = []
    _dw_held = False
    _dw_on_complete = on_complete


def _mousedown_drawing(pos):
    global _dw_held
    _dw_held = True
    _dw_trail.append(pos)
    _check_drawing_progress(pos)
    return True


def _mousemotion_drawing(pos):
    if not _dw_held:
        return
    _dw_trail.append(pos)
    if len(_dw_trail) > 500:
        _dw_trail.pop(0)
    _check_drawing_progress(pos)


def _mouseup_drawing():
    global _dw_held
    _dw_held = False


def _check_drawing_progress(pos):
    for i, (gx, gy) in enumerate(_dw_guide):
        if not _dw_visited[i] and (pos[0] - gx) ** 2 + (pos[1] - gy) ** 2 < 31 ** 2:
            _dw_visited[i] = True
    if sum(_dw_visited) >= max(1, int(len(_dw_visited) * 0.75)):
        _finish_drawing()


def _finish_drawing():
    global mode
    if mode != 'drawing':
        return
    mode = 'none'
    cb = _dw_on_complete
    if cb:
        cb()


def _draw_drawing(surf):
    panel = _draw_backdrop(surf,
        config.tr('Dibuja nuestro recuerdo', 'Draw our memory'),
        config.tr('Arrastra el dedo para unir los puntos', 'Drag your finger to connect the dots'))
    # Corazón guía y puntos de progreso.
    for i, (gx, gy) in enumerate(_dw_guide):
        nxt = _dw_guide[(i + 1) % len(_dw_guide)]
        pygame.draw.line(surf, (47, 61, 95), (int(gx), int(gy)), (int(nxt[0]), int(nxt[1])), 2)
    for i, (gx, gy) in enumerate(_dw_guide):
        visited = _dw_visited[i]
        color = GOLD if visited else (110, 130, 174)
        pygame.draw.circle(surf, (31, 42, 70), (int(gx), int(gy)), 9)
        pygame.draw.circle(surf, color, (int(gx), int(gy)), 5)
    if len(_dw_trail) > 1:
        pts = [(int(x), int(y)) for x, y in _dw_trail]
        pygame.draw.lines(surf, (95, 37, 72), False, pts, 9)
        pygame.draw.lines(surf, PINK, False, pts, 4)
        for x, y in pts[-8::2]:
            pygame.draw.circle(surf, (255, 193, 196), (x, y), 3)
    progress = sum(_dw_visited) / max(1, len(_dw_visited))
    bar = pygame.Rect(panel.x + 44, panel.bottom - 57, panel.width - 88, 10)
    pygame.draw.rect(surf, (35, 47, 75), bar, border_radius=5)
    fill = bar.copy()
    fill.width = int(bar.width * progress)
    if fill.width:
        pygame.draw.rect(surf, PINK, fill, border_radius=5)
    pct = font('tiny').render(f'{int(progress * 100)}%', True, CREAM)
    surf.blit(pct, pct.get_rect(center=(W // 2, panel.bottom - 32)))


# 3) Armar el cubo infinito
_cb_tiles = []
_cb_next = 1
_cb_on_complete = None


def start_cube(on_complete):
    global mode, _cb_tiles, _cb_next, _cb_on_complete
    mode = 'cube'
    _cb_next = 1
    _cb_on_complete = on_complete
    tile_w, tile_h, gap = 112, 94, 18
    positions = [(W // 2 - tile_w - gap // 2, H // 2 - tile_h - gap // 2 + 12),
                 (W // 2 + gap // 2, H // 2 - tile_h - gap // 2 + 12),
                 (W // 2 - tile_w - gap // 2, H // 2 + gap // 2 + 12),
                 (W // 2 + gap // 2, H // 2 + gap // 2 + 12)]
    nums = [1, 2, 3, 4]
    random.shuffle(nums)
    _cb_tiles = [{'num': n, 'rect': pygame.Rect(p[0], p[1], tile_w, tile_h), 'done': False}
                 for p, n in zip(positions, nums)]


def _click_cube(pos):
    global _cb_next
    for tile in _cb_tiles:
        if tile['done']:
            continue
        if tile['rect'].collidepoint(pos):
            if tile['num'] == _cb_next:
                tile['done'] = True
                audio.play_match()
                _cb_next += 1
                if _cb_next > 4:
                    _finish_cube()
            else:
                audio.play_mismatch()
            return True
    return True


def _finish_cube():
    global mode
    mode = 'none'
    cb = _cb_on_complete
    if cb:
        cb()


def _draw_cube(surf):
    panel = _draw_backdrop(surf,
        config.tr('El cubo infinito', 'The infinity cube'),
        config.tr(f'Toca las piezas en orden · siguiente: {_cb_next}', f'Tap the pieces in order · next: {_cb_next}'))
    for tile in _cb_tiles:
        r = tile['rect']
        # Sombra y tarjeta con bordes suaves.
        shadow = r.move(4, 5)
        pygame.draw.rect(surf, (3, 6, 16), shadow, border_radius=12)
        fill = (25, 47, 76) if tile['done'] else (20, 31, 58)
        edge = GOLD if tile['done'] else (87, 121, 178)
        pygame.draw.rect(surf, fill, r, border_radius=12)
        pygame.draw.rect(surf, edge, r, width=3 if tile['done'] else 2, border_radius=12)
        inner = r.inflate(-10, -10)
        pygame.draw.rect(surf, (255, 255, 255, 16), inner, width=1, border_radius=8)
        col = GOLD if tile['done'] else CREAM
        label = font('title').render(str(tile['num']), True, col)
        surf.blit(label, label.get_rect(center=(r.centerx, r.centery - 3)))
        if tile['done']:
            check = font('tiny').render('✓', True, (171, 222, 202))
            surf.blit(check, check.get_rect(center=(r.centerx, r.bottom - 17)))
    hint = font('tiny').render(config.tr('Cada pieza guarda un recuerdo', 'Each piece holds a memory'), True, MUTED)
    surf.blit(hint, hint.get_rect(center=(W // 2, panel.bottom - 32)))


# Interfaz unificada

def update(now):
    if mode == 'heartbeat':
        _update_heartbeat(now)


def draw(surf):
    if mode == 'heartbeat':
        _draw_heartbeat(surf)
    elif mode == 'drawing':
        _draw_drawing(surf)
    elif mode == 'cube':
        _draw_cube(surf)


def handle_mousedown(pos):
    """Único punto de entrada para pulsaciones en cualquier minijuego activo."""
    if mode == 'heartbeat':
        return _click_heartbeat(pos)
    if mode == 'cube':
        return _click_cube(pos)
    if mode == 'drawing':
        return _mousedown_drawing(pos)
    return False


def handle_mousemotion(pos):
    if mode == 'drawing':
        _mousemotion_drawing(pos)


def handle_mouseup():
    if mode == 'drawing':
        _mouseup_drawing()
