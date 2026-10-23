"""
Controles táctiles opcionales, para cuando config.control_scheme no es 'keyboard'.
Se dibujan encima de la escena y alimentan la misma dirección de entrada que
usan las flechas / A-D, así que el resto del juego no necesita saber cuál
esquema de control está activo.
"""
import pygame
import config
from engine.constants import W, H, font

touch_dir = 0     # -1, 0, 1 — dirección pedida por el control en pantalla
_held = False

_dpad_left = pygame.Rect(26, H - 110, 64, 64)
_dpad_right = pygame.Rect(100, H - 110, 64, 64)
_touchpad = pygame.Rect(26, H - 90, 200, 56)

COL_CTRL_BG = (20, 18, 30, 180)
COL_CTRL_BORDER = (232, 163, 176)
COL_CTRL_TEXT = (244, 233, 216)


def active():
    return config.control_scheme in ('dpad', 'touchpad')


def handle_mousedown(pos):
    global touch_dir, _held
    if config.control_scheme == 'dpad':
        if _dpad_left.collidepoint(pos):
            touch_dir = -1
            _held = True
            return True
        if _dpad_right.collidepoint(pos):
            touch_dir = 1
            _held = True
            return True
    elif config.control_scheme == 'touchpad':
        if _touchpad.collidepoint(pos):
            touch_dir = -1 if pos[0] < _touchpad.centerx else 1
            _held = True
            return True
    return False


def handle_mousemotion(pos):
    global touch_dir
    if _held and config.control_scheme == 'touchpad' and _touchpad.collidepoint(pos):
        touch_dir = -1 if pos[0] < _touchpad.centerx else 1


def handle_mouseup():
    global touch_dir, _held
    touch_dir = 0
    _held = False


def draw(surf):
    if not active():
        return
    if config.control_scheme == 'dpad':
        for r, label in ((_dpad_left, '\u25c0'), (_dpad_right, '\u25b6')):
            s = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            s.fill(COL_CTRL_BG)
            surf.blit(s, r.topleft)
            pygame.draw.rect(surf, COL_CTRL_BORDER, r, width=2, border_radius=10)
            t = font('h1').render(label, True, COL_CTRL_TEXT)
            surf.blit(t, t.get_rect(center=r.center))
    else:  # touchpad
        s = pygame.Surface((_touchpad.w, _touchpad.h), pygame.SRCALPHA)
        s.fill(COL_CTRL_BG)
        surf.blit(s, _touchpad.topleft)
        pygame.draw.rect(surf, COL_CTRL_BORDER, _touchpad, width=2, border_radius=14)
        pygame.draw.line(surf, COL_CTRL_BORDER, (_touchpad.centerx, _touchpad.y + 6),
                          (_touchpad.centerx, _touchpad.bottom - 6), 1)
        lt = font('body').render('\u25c0', True, COL_CTRL_TEXT)
        rt = font('body').render('\u25b6', True, COL_CTRL_TEXT)
        surf.blit(lt, lt.get_rect(center=(_touchpad.x + _touchpad.w // 4, _touchpad.centery)))
        surf.blit(rt, rt.get_rect(center=(_touchpad.x + 3 * _touchpad.w // 4, _touchpad.centery)))
