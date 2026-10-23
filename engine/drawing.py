"""
Helpers de dibujo pixel-art, puerto de las funciones rect()/circle()/gradientRect()
del canvas 2D original, más el renderizado de personajes con ciclo de caminata.
"""
import math
import pygame
from .character_assets import draw_overworld as _draw_overworld_asset

WALK_FRAMES = 8

pixelate_world = True   # lo fija cada escena en cada frame


def set_pixelate(value):
    """Las escenas con fondo PNG lo desactivan para no degradar el arte."""
    global pixelate_world
    pixelate_world = value


def pixelate(surf, scale):
    """
    Reduce la superficie a baja resolución y la vuelve a escalar, dando el
    look de píxel grueso/retro (como la resolución nativa de una GBA).
    pygame.transform.scale (sin 'smooth') no interpola, así que el resultado
    queda en bloques definidos en vez de borroso.
    """
    w, h = surf.get_size()
    small = pygame.transform.scale(surf, (max(1, w // scale), max(1, h // scale)))
    return pygame.transform.scale(small, (w, h))


def outline_rect(surf, x, y, w, h, color, thickness=2):
    """Contorno rectangular grueso, estilo sprite retro."""
    pygame.draw.rect(surf, color[:3], (int(x), int(y), int(w), int(h)), width=thickness)


def outline_circle(surf, x, y, r, color, thickness=2):
    pygame.draw.circle(surf, color[:3], (int(x), int(y)), int(r), width=thickness)


# ── PRIMITIVAS ──
def rect(surf, x, y, w, h, color, outline=False):
    x, y, w, h = int(round(x)), int(round(y)), int(round(w)), int(round(h))
    if w <= 0 or h <= 0:
        return
    if len(color) == 4 and color[3] < 255:
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill(color)
        surf.blit(s, (x, y))
    else:
        pygame.draw.rect(surf, color[:3], (x, y, w, h))
    if outline:
        pygame.draw.rect(surf, OUTLINE_COL, (x, y, w, h), width=1)


def circle(surf, x, y, r, color, outline=False):
    x, y, r = int(round(x)), int(round(y)), int(round(r))
    if r <= 0:
        return
    if len(color) == 4 and color[3] < 255:
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (r, r), r)
        surf.blit(s, (x - r, y - r))
    else:
        pygame.draw.circle(surf, color[:3], (x, y), r)
    if outline:
        pygame.draw.circle(surf, OUTLINE_COL, (x, y), r, width=2)


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


_GRAD_CACHE = {}


def gradient_rect(surf, x, y, w, h, color1, color2, vertical=True):
    """Degradado; se dibuja una sola vez en una superficie y luego solo se copia."""
    x, y, w, h = int(x), int(y), int(w), int(h)
    if w <= 0 or h <= 0:
        return
    key = (w, h, tuple(color1[:3]), tuple(color2[:3]), vertical)
    grad = _GRAD_CACHE.get(key)
    if grad is None:
        grad = pygame.Surface((w, h))
        if vertical:
            for i in range(h):
                t = i / max(1, h - 1)
                pygame.draw.line(grad, lerp_color(color1, color2, t), (0, i), (w - 1, i))
        else:
            for i in range(w):
                t = i / max(1, w - 1)
                pygame.draw.line(grad, lerp_color(color1, color2, t), (i, 0), (i, h - 1))
        _GRAD_CACHE[key] = grad
    surf.blit(grad, (x, y))


def tile_ground(surf, x, y, w, h, color_a, color_b, tile_size=24, line_color=None):
    """
    Terreno en cuadrícula de tiles alternados, como el overworld de un juego
    retro (pasto/tierra/piedra en vez de un degradado liso).
    """
    x, y, w, h = int(x), int(y), int(w), int(h)
    cols = (w // tile_size) + 2
    rows = (h // tile_size) + 2
    for row in range(rows):
        for col in range(cols):
            tx = x + col * tile_size
            ty = y + row * tile_size
            color = color_a if (row + col) % 2 == 0 else color_b
            pygame.draw.rect(surf, color[:3], (tx, ty, tile_size, tile_size))
    if line_color:
        for row in range(rows + 1):
            ly = y + row * tile_size
            pygame.draw.line(surf, line_color, (x, ly), (x + cols * tile_size, ly), 1)
        for col in range(cols + 1):
            lx = x + col * tile_size
            pygame.draw.line(surf, line_color, (lx, y), (lx, y + rows * tile_size), 1)


def radial_glow(surf, cx, cy, radius, color, max_alpha=70):
    """Aproximación de un radial gradient con círculos concéntricos."""
    radius = int(radius)
    if radius <= 0:
        return
    glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    steps = 24
    for i in range(steps, 0, -1):
        r = int(radius * i / steps)
        if r <= 0:
            continue
        alpha = int(max_alpha * (1 - i / steps))
        pygame.draw.circle(glow, (*color[:3], alpha), (radius, radius), r)
    surf.blit(glow, (int(cx - radius), int(cy - radius)), special_flags=pygame.BLEND_ADD)


OUTLINE_COL = (18, 15, 22)  # contorno casi-negro, estilo sprite retro

# Sprite sheet opcional de Breyner. Si falta el archivo, se conserva el dibujo original.
_BREYNER_SHEET = None
_BREYNER_SHEET_FAILED = False

def _draw_breyner_sprite(surf, x, y, scale, facing='right', moving=False, frame=0, bob=0.0):
    """Dibuja un fotograma de assets/characters/breyner/overworld.png.

    Hoja: 4 columnas de fotogramas x 4 filas de dirección
    (frente, perfil, perfil opuesto, espalda), celdas de 48x64.
    La selección de dirección/animación coincide con character_assets.py.
    Devuelve False si el recurso no está disponible para activar el dibujo anterior.
    """
    global _BREYNER_SHEET, _BREYNER_SHEET_FAILED
    if _BREYNER_SHEET is None and not _BREYNER_SHEET_FAILED:
        import os
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'characters', 'breyner', 'overworld.png')
        try:
            _BREYNER_SHEET = pygame.image.load(path).convert_alpha()
        except (pygame.error, OSError):
            _BREYNER_SHEET_FAILED = True
    if _BREYNER_SHEET is None:
        return False
    row = {'down': 0, 'front': 0, 'left': 1, 'right': 2, 'up': 3, 'back': 3}.get(facing, 2)
    col = (1 + 2 * ((int(frame) // 4) % 2)) if moving else 0
    cell = _BREYNER_SHEET.subsurface(pygame.Rect(col * 48, row * 64, 48, 64))
    size = (max(1, int(48 * scale)), max(1, int(64 * scale)))
    if size != (48, 64):
        cell = pygame.transform.scale(cell, size)
    surf.blit(cell, (int(x - size[0] / 2), int(y - size[1] + bob)))
    return True


def draw_rotated_rect(surf, ox, oy, lx, ly, lw, lh, angle_deg, color, outline=False):
    """
    Dibuja un rect definido en espacio local (lx,ly,lw,lh) rotado angle_deg
    alrededor del origen (ox,oy). Puerto fiel de ctx.translate+ctx.rotate+fillRect.
    Con outline=True agrega un contorno oscuro, estilo sprite retro.
    """
    ang = math.radians(angle_deg)
    cos_a, sin_a = math.cos(ang), math.sin(ang)
    corners = [(lx, ly), (lx + lw, ly), (lx + lw, ly + lh), (lx, ly + lh)]
    pts = []
    for cx, cy in corners:
        rx = cx * cos_a - cy * sin_a
        ry = cx * sin_a + cy * cos_a
        pts.append((ox + rx, oy + ry))
    pygame.draw.polygon(surf, color[:3], pts)
    if outline:
        pygame.draw.polygon(surf, OUTLINE_COL, pts, width=1)


# ── PERSONAJES ──
def draw_character_static(surf, x, y, scale, palette, facing='right', bob=0.0, expression=None):
    """Personaje estático con sprites externos cuando existen y dibujo anterior como respaldo."""
    character_id = palette.get('character_id')
    if character_id and _draw_overworld_asset(surf, x, y, scale, character_id, facing, 0, False):
        return
    if palette.get('hair_style') == 'short-side' and _draw_breyner_sprite(surf, x, y, scale, facing, False, 0, math.sin(bob) * 2):
        return
    s = scale
    y_off = math.sin(bob) * 2
    tx, ty = x, y + y_off

    sh = pygame.Surface((int(30 * s), int(10 * s)), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 77), sh.get_rect())
    surf.blit(sh, (tx - 15 * s, ty))

    rect(surf, tx - 6 * s, ty - 22 * s, 5 * s, 18 * s, palette['pants'], outline=True)
    rect(surf, tx + 1 * s, ty - 22 * s, 5 * s, 18 * s, palette['pants'], outline=True)
    rect(surf, tx - 7 * s, ty - 5 * s, 7 * s, 5 * s, palette['shoe'], outline=True)
    rect(surf, tx + 0 * s, ty - 5 * s, 7 * s, 5 * s, palette['shoe'], outline=True)
    rect(surf, tx - 8 * s, ty - 44 * s, 16 * s, 24 * s, palette['shirt'], outline=True)
    rect(surf, tx - 11 * s, ty - 42 * s, 4 * s, 16 * s, palette['shirt'], outline=True)
    rect(surf, tx + 7 * s, ty - 42 * s, 4 * s, 16 * s, palette['shirt'], outline=True)
    rect(surf, tx - 11 * s, ty - 27 * s, 4 * s, 4 * s, palette['skin'])
    rect(surf, tx + 7 * s, ty - 27 * s, 4 * s, 4 * s, palette['skin'])
    rect(surf, tx - 3 * s, ty - 48 * s, 6 * s, 5 * s, palette['skin'])
    # cabeza chibi (más grande, centrada en el mismo punto que antes)
    rect(surf, tx - 11 * s, ty - 65 * s, 22 * s, 20 * s, palette['skin'], outline=True)
    rect(surf, tx - 12 * s, ty - 68 * s, 24 * s, 8 * s, palette['hair'], outline=True)
    if palette['hair_style'] == 'long':
        rect(surf, tx - 13 * s, ty - 63 * s, 4 * s, 19 * s, palette['hair'], outline=True)
        rect(surf, tx + 9 * s, ty - 63 * s, 4 * s, 19 * s, palette['hair'], outline=True)
    if palette['hair_style'] == 'short-side':
        rect(surf, tx + 9 * s, ty - 65 * s, 4 * s, 13 * s, palette['hair'], outline=True)

    eo = -1 if facing == 'left' else 1
    if expression == 'confused':
        rect(surf, tx - 6 * s * eo - 1 * s, ty - 58 * s, 3 * s, 3 * s, (26, 26, 36))
        rect(surf, tx + 2 * s * eo - 1 * s, ty - 58 * s, 3 * s, 3 * s, (26, 26, 36))
        rect(surf, tx - 1.5 * s, ty - 50 * s, 3 * s, 1 * s, (138, 90, 90))
    elif expression == 'curious':
        rect(surf, tx - 6 * s * eo - 1 * s, ty - 58 * s, 3.5 * s, 3.5 * s, (26, 26, 36))
        rect(surf, tx + 2 * s * eo - 1 * s, ty - 58 * s, 3.5 * s, 3.5 * s, (26, 26, 36))
        rect(surf, tx - 2 * s, ty - 50 * s, 4 * s, 1.5 * s, (138, 90, 90))
    elif expression == 'warm':
        rect(surf, tx - 6 * s * eo - 1 * s, ty - 57 * s, 3 * s, 2.5 * s, (26, 26, 36))
        rect(surf, tx + 2 * s * eo - 1 * s, ty - 57 * s, 3 * s, 2.5 * s, (26, 26, 36))
        rect(surf, tx - 3 * s, ty - 50 * s, 6 * s, 2 * s, (163, 106, 106))
    else:
        rect(surf, tx - 6 * s * eo - 1 * s, ty - 58 * s, 3 * s, 3.5 * s, (26, 26, 36))
        rect(surf, tx + 2 * s * eo - 1 * s, ty - 58 * s, 3 * s, 3.5 * s, (26, 26, 36))
        rect(surf, tx - 2 * s, ty - 50 * s, 4 * s, 1.5 * s, (138, 90, 90))


def draw_walk_character(surf, x, y, scale, palette, facing, frame, moving, anim_frame):
    """Dibuja el sprite del personaje si está instalado; conserva el dibujo antiguo como respaldo."""
    character_id = palette.get('character_id')
    if character_id and _draw_overworld_asset(surf, x, y, scale, character_id, facing, frame, moving):
        return
    if palette.get('hair_style') == 'short-side' and _draw_breyner_sprite(surf, x, y, scale, facing, moving, frame):
        return
    s = scale
    dir_ = -1 if facing == 'left' else 1
    phase = (frame / WALK_FRAMES) * math.pi * 2
    body_bob = math.sin(phase) * 2.5 if moving else 0
    leg_swing = math.sin(phase) * 10 if moving else 0
    arm_swing = math.sin(phase + math.pi) * 8 if moving else 0
    lean_x = math.sin(phase) * 1.2 if moving else 0

    tx, ty = round(x + lean_x), round(y + body_bob)

    sh = pygame.Surface((int(28 * s), int(8 * s)), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 64), sh.get_rect())
    surf.blit(sh, (tx - 14 * s, ty))

    leg_off = leg_swing * 0.6 if moving else 0
    # pierna delantera
    draw_rotated_rect(surf, tx + 2 * s * dir_, ty - 10 * s, -3 * s, 0, 5 * s, 18 * s,
                       leg_off * dir_, palette['pants'], outline=True)
    draw_rotated_rect(surf, tx + 2 * s * dir_, ty - 10 * s, -4 * s, 16 * s, 7 * s, 5 * s,
                       leg_off * dir_, palette['shoe'], outline=True)
    # pierna trasera (más tenue)
    draw_rotated_rect(surf, tx - 2 * s * dir_, ty - 10 * s, -2 * s, 0, 5 * s, 18 * s,
                       -leg_off * dir_, palette['pants'], outline=True)
    draw_rotated_rect(surf, tx - 2 * s * dir_, ty - 10 * s, -3 * s, 16 * s, 7 * s, 5 * s,
                       -leg_off * dir_, palette['shoe'], outline=True)

    # torso
    rect(surf, tx - 8 * s, ty - 44 * s, 16 * s, 24 * s, palette['shirt'], outline=True)

    # brazos
    draw_rotated_rect(surf, tx - 8 * s, ty - 40 * s, 0, 0, 4 * s, 16 * s,
                       -arm_swing * dir_, palette['shirt'], outline=True)
    draw_rotated_rect(surf, tx - 8 * s, ty - 40 * s, 0, 14 * s, 4 * s, 4 * s,
                       -arm_swing * dir_, palette['skin'], outline=True)
    draw_rotated_rect(surf, tx + 4 * s, ty - 40 * s, 0, 0, 4 * s, 16 * s,
                       arm_swing * dir_, palette['shirt'], outline=True)
    draw_rotated_rect(surf, tx + 4 * s, ty - 40 * s, 0, 14 * s, 4 * s, 4 * s,
                       arm_swing * dir_, palette['skin'], outline=True)

    # cuello
    rect(surf, tx - 3 * s, ty - 48 * s, 6 * s, 5 * s, palette['skin'])
    # cabeza chibi (más grande, centrada en el mismo punto que antes)
    rect(surf, tx - 11 * s, ty - 65 * s, 22 * s, 20 * s, palette['skin'], outline=True)

    # cabello
    rect(surf, tx - 12 * s, ty - 68 * s, 24 * s, 8 * s, palette['hair'], outline=True)
    if palette['hair_style'] == 'short-side':
        rect(surf, tx + 8 * s, ty - 65 * s, 4 * s, 13 * s, palette['hair'], outline=True)

    # ojos (parpadeo cada ~3s) — más grandes, estilo retro
    eye_off = -1 if facing == 'left' else 1
    blinking = (anim_frame % 180) < 4
    eye_color = palette['skin'] if blinking else (20, 18, 26)
    rect(surf, tx - 6 * s * eye_off - 1 * s, ty - 57 * s, 3 * s, 3.5 * s, eye_color)
    rect(surf, tx + 2 * s * eye_off - 1 * s, ty - 57 * s, 3 * s, 3.5 * s, eye_color)
    rect(surf, tx - 2 * s, ty - 50 * s, 4 * s, 1.5 * s, (138, 90, 90))


def draw_walk_character_expression(surf, x, y, scale, palette, facing, frame, moving, expression, anim_frame):
    """Cristel: usa su sprite externo si existe y conserva el render anterior como respaldo."""
    character_id = palette.get('character_id')
    if character_id and _draw_overworld_asset(surf, x, y, scale, character_id, facing, frame, moving):
        return
    s = scale
    dir_ = -1 if facing == 'left' else 1
    phase = (frame / WALK_FRAMES) * math.pi * 2
    body_bob = math.sin(phase) * 2 if moving else 0
    lean_x = math.sin(phase) * 0.8 if moving else 0
    tx, ty = round(x + lean_x), round(y + body_bob)

    sh = pygame.Surface((int(24 * s), int(6 * s)), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 51), sh.get_rect())
    surf.blit(sh, (tx - 12 * s, ty))

    leg_off = (math.sin(phase) * 8 * 0.6) if moving else 0
    draw_rotated_rect(surf, tx + 2 * s * dir_, ty - 10 * s, -3 * s, 0, 5 * s, 18 * s,
                       leg_off * dir_, palette['pants'], outline=True)
    draw_rotated_rect(surf, tx + 2 * s * dir_, ty - 10 * s, -4 * s, 16 * s, 7 * s, 5 * s,
                       leg_off * dir_, palette['shoe'], outline=True)
    draw_rotated_rect(surf, tx - 2 * s * dir_, ty - 10 * s, -2 * s, 0, 5 * s, 18 * s,
                       -leg_off * dir_, palette['pants'], outline=True)
    draw_rotated_rect(surf, tx - 2 * s * dir_, ty - 10 * s, -3 * s, 16 * s, 7 * s, 5 * s,
                       -leg_off * dir_, palette['shoe'], outline=True)

    rect(surf, tx - 7 * s, ty - 44 * s, 14 * s, 24 * s, palette['shirt'], outline=True)

    arm_sw = (math.sin(phase + math.pi) * 7) if moving else 0
    draw_rotated_rect(surf, tx - 7 * s, ty - 40 * s, 0, 0, 4 * s, 14 * s, -arm_sw * dir_, palette['shirt'], outline=True)
    draw_rotated_rect(surf, tx - 7 * s, ty - 40 * s, 0, 12 * s, 4 * s, 4 * s, -arm_sw * dir_, palette['skin'], outline=True)
    draw_rotated_rect(surf, tx + 3 * s, ty - 40 * s, 0, 0, 4 * s, 14 * s, arm_sw * dir_, palette['shirt'], outline=True)
    draw_rotated_rect(surf, tx + 3 * s, ty - 40 * s, 0, 12 * s, 4 * s, 4 * s, arm_sw * dir_, palette['skin'], outline=True)

    # cuello
    rect(surf, tx - 3 * s, ty - 47 * s, 6 * s, 4 * s, palette['skin'])
    # cabeza chibi (más grande, centrada en el mismo punto que antes)
    rect(surf, tx - 10 * s, ty - 63 * s, 20 * s, 18 * s, palette['skin'], outline=True)
    rect(surf, tx - 11 * s, ty - 66 * s, 22 * s, 7 * s, palette['hair'], outline=True)
    rect(surf, tx - 12 * s, ty - 61 * s, 4 * s, 17 * s, palette['hair'], outline=True)
    rect(surf, tx + 8 * s, ty - 61 * s, 4 * s, 17 * s, palette['hair'], outline=True)
    if moving:
        hs = abs(math.sin(phase * 0.5) * 3)
        rect(surf, tx + 8 * s, ty - 52 * s, 5 * s, hs, palette['hair'])

    eo = -1 if facing == 'left' else 1
    blinking = (anim_frame % 180) < 4
    if blinking:
        eye_color = palette['skin']
    else:
        eye_color = (20, 18, 26)

    if expression == 'confused':
        rect(surf, tx - 5 * s * eo - 1 * s, ty - 55 * s, 3 * s, 2.5 * s, eye_color)
        rect(surf, tx + 2 * s * eo - 1 * s, ty - 55 * s, 3 * s, 2.5 * s, eye_color)
        if not blinking:
            rect(surf, tx - 2 * s, ty - 49 * s, 2 * s, 1 * s, (106, 80, 80))
        rect(surf, tx - 1 * s, ty - 47 * s, 2 * s, 1 * s, (138, 90, 90))
    elif expression == 'curious':
        rect(surf, tx - 5 * s * eo - 1 * s, ty - 55 * s, 3.5 * s, 3.5 * s, eye_color)
        rect(surf, tx + 2 * s * eo - 1 * s, ty - 55 * s, 3.5 * s, 3.5 * s, eye_color)
        rect(surf, tx - 2 * s, ty - 47 * s, 4 * s, 1.5 * s, (138, 90, 90))
    elif expression == 'warm':
        rect(surf, tx - 5 * s * eo - 1 * s, ty - 55 * s, 3 * s, 2 * s, eye_color)
        rect(surf, tx + 2 * s * eo - 1 * s, ty - 55 * s, 3 * s, 2 * s, eye_color)
        rect(surf, tx - 3 * s, ty - 47 * s, 6 * s, 2 * s, (163, 106, 106))
    else:
        rect(surf, tx - 5 * s * eo - 1 * s, ty - 55 * s, 3 * s, 2 * s, eye_color)
        rect(surf, tx + 2 * s * eo - 1 * s, ty - 55 * s, 3 * s, 2 * s, eye_color)
        rect(surf, tx - 3 * s, ty - 47 * s, 6 * s, 2 * s, (163, 106, 106))
