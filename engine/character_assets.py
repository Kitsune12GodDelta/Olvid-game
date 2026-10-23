"""Carga opcional de sprites y retratos para Olvido.

Convención del spritesheet: 4 columnas x 4 filas, celdas 48x64 (configurable).
Filas: down, left, right, up. Columnas: idle, paso A, idle alternativo, paso B.
El punto (x, y) que recibe drawing.py representa el centro inferior del sprite.
Si no existen archivos, el juego conserva automáticamente el renderizado anterior.
"""
from pathlib import Path
import pygame

ROOT = Path(__file__).resolve().parent.parent
CHAR_DIR = ROOT / 'assets' / 'characters'
SHEET_SIZE = (48, 64)
DIRECTIONS = {'down': 0, 'front': 0, 'left': 1, 'right': 2, 'up': 3, 'back': 3}
_CACHE = {}
_PORTRAITS = {}


def _load_sheet(character_id):
    if character_id not in _CACHE:
        path = CHAR_DIR / character_id / 'overworld.png'
        if not path.is_file():
            _CACHE[character_id] = None
        else:
            try:
                _CACHE[character_id] = pygame.image.load(str(path)).convert_alpha()
            except (pygame.error, OSError):
                _CACHE[character_id] = None
    return _CACHE[character_id]


def draw_overworld(surf, x, y, scale, character_id, facing='down', frame=0, moving=False):
    """Dibuja un sprite si está instalado; retorna True si lo dibujó."""
    sheet = _load_sheet(character_id)
    if sheet is None:
        return False
    cw, ch = SHEET_SIZE
    if sheet.get_width() < cw * 4 or sheet.get_height() < ch * 4:
        return False
    row = DIRECTIONS.get(facing, 2)
    # Las columnas 0/2 son poses quietas y 1/3 son pasos alternos.
    # El frame puede avanzar rápidamente; alternamos por paridad para no
    # dejar al personaje congelado durante varios ciclos de animación.
    col = (1 + 2 * ((int(frame) // 4) % 2)) if moving else 0
    src = pygame.Rect(col * cw, row * ch, cw, ch)
    sprite = sheet.subsurface(src)
    size = (max(1, round(cw * scale)), max(1, round(ch * scale)))
    sprite = pygame.transform.scale(sprite, size)
    dest = sprite.get_rect(midbottom=(round(x), round(y)))
    # sombra pequeña y discreta para mantener lectura sobre escenarios claros
    shadow = pygame.Surface((max(4, size[0] // 2), max(2, size[1] // 12)), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 65), shadow.get_rect())
    surf.blit(shadow, (round(x - shadow.get_width() / 2), round(y - shadow.get_height() / 2)))
    surf.blit(sprite, dest)
    return True


def get_portrait(character_id, size=None):
    """Obtiene el retrato transparente o None si aún no se ha creado."""
    if character_id not in _PORTRAITS:
        path = CHAR_DIR / character_id / 'portrait.png'
        try:
            _PORTRAITS[character_id] = pygame.image.load(str(path)).convert_alpha() if path.is_file() else None
        except (pygame.error, OSError):
            _PORTRAITS[character_id] = None
    portrait = _PORTRAITS[character_id]
    if portrait is not None and size:
        return pygame.transform.smoothscale(portrait, size)
    return portrait


def clear_asset_cache():
    """Útil para recargar recursos durante desarrollo."""
    _CACHE.clear()
    _PORTRAITS.clear()
