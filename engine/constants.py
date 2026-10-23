"""
Constantes compartidas: tamaño de pantalla, colores, paletas de personajes.
Puerto fiel de los valores CSS/JS de olvido-v3-final.html
"""
import pygame

W, H = 960, 600
FPS = 60
PIXEL_SCALE = 3   # 1 "pixel" de juego = 3px reales; sube esto para un look aún más retro


def hx(h):
    """Convierte '#rrggbb' a tupla (r,g,b)."""
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# ── COLORES UI (puerto directo del CSS original) ──
COL_BG_DARK = hx('#0a0a12')
COL_CREAM = hx('#f4e9d8')
COL_PINK = hx('#e8a3b0')
COL_BLUE = hx('#a3c9e8')
COL_GREY = hx('#9a8fae')
COL_GREY_DIM = hx('#7a7090')
COL_GREY_FAINT = hx('#5a5070')
COL_BORDER = hx('#4a4060')
COL_BORDER_DIM = hx('#3a3450')
COL_PANEL_BG = hx('#2a2438')
COL_POLAROID = hx('#f4ece0')
COL_POLAROID_CAP = hx('#3a2818')
COL_POLAROID_LOCKED = hx('#2a2438')

# ── PALETAS DE PERSONAJES ──
PALETTE_BREYNER = {
    'skin': hx('#d9a878'), 'hair': hx('#2a2018'), 'shirt': hx('#3a5a7a'),
    'pants': hx('#2a2a38'), 'shoe': hx('#1a1a20'), 'hair_style': 'short-side', 'character_id': 'breyner',
}
PALETTE_CRISTEL = {
    'skin': hx('#e8c4a0'), 'hair': hx('#3a2818'), 'shirt': hx('#b06a80'),
    'pants': hx('#4a3a50'), 'shoe': hx('#3a2a30'), 'hair_style': 'long', 'character_id': 'cristel',
}

PALETTE_MADRE_CRISTEL = {
    'skin': hx('#e8c4a0'), 'hair': hx('#4a3028'), 'shirt': hx('#c98791'),
    'pants': hx('#34364b'), 'shoe': hx('#2a2530'), 'hair_style': 'long', 'character_id': 'madre_cristel',
}

# ── FUENTES (se inicializan tras pygame.font.init()) ──
_fonts = {}


def init_fonts():
    pygame.font.init()
    _fonts['title'] = pygame.font.Font(None, 54)
    _fonts['start_title'] = pygame.font.Font(None, 72)
    _fonts['subtitle'] = pygame.font.Font(None, 20)
    _fonts['h1'] = pygame.font.Font(None, 40)
    _fonts['eyebrow'] = pygame.font.Font(None, 18)
    _fonts['body'] = pygame.font.Font(None, 22)
    _fonts['speaker'] = pygame.font.Font(None, 18)
    _fonts['small'] = pygame.font.Font(None, 16)
    _fonts['tiny'] = pygame.font.Font(None, 14)
    _fonts['icon'] = pygame.font.Font(None, 26)
    _fonts['icon_small'] = pygame.font.Font(None, 20)
    for key in ('speaker', 'eyebrow'):
        _fonts[key].set_bold(True)


def font(name):
    return _fonts[name]
