"""
Pantallas fuera del juego: inicio, personalización de nombres y configuración
(volumen, idioma, esquema de control). Todo con valores por defecto, para
quien no quiera tocar nada.
"""
import pygame
import config
import save_system
from engine import audio
from engine.constants import W, H, font
from engine.drawing import gradient_rect

COL_CREAM = (244, 233, 216)
COL_PINK = (232, 163, 176)
COL_GREY = (154, 143, 174)
COL_GREY_DIM = (122, 112, 144)
COL_BORDER = (74, 64, 96)
COL_PANEL = (20, 18, 30)


def _button(surf, rect_, label, active=False, font_key='small'):
    pygame.draw.rect(surf, COL_PANEL if active else (10, 9, 16), rect_)
    pygame.draw.rect(surf, COL_PINK if active else COL_BORDER, rect_, width=2)
    t = font(font_key).render(label, True, COL_CREAM)
    surf.blit(t, (rect_.centerx - t.get_width() // 2, rect_.centery - t.get_height() // 2))


# ─────────────────────────────────────────────
# PANTALLA DE INICIO
# ─────────────────────────────────────────────
btn_continue = pygame.Rect(W // 2 - 110, H // 2 - 62, 220, 48)
btn_start = pygame.Rect(W // 2 - 110, H // 2 - 6, 220, 50)
btn_names = pygame.Rect(W // 2 - 110, H // 2 + 54, 220, 44)
btn_settings = pygame.Rect(W // 2 - 110, H // 2 + 106, 220, 44)
sound_hint_rect = pygame.Rect(0, 0, 0, 0)


def draw_start(surf):
    gradient_rect(surf, 0, 0, W, H, (26, 21, 48), (10, 10, 18))
    title = font('start_title').render('OLVIDO', True, COL_CREAM)
    surf.blit(title, (W // 2 - title.get_width() // 2, H // 2 - 190))
    subtitle = font('subtitle').render(
        config.tr('seis recuerdos \u00b7 una despedida que no fue',
                   'six memories \u00b7 a goodbye that never was'), True, COL_GREY)
    surf.blit(subtitle, (W // 2 - subtitle.get_width() // 2, H // 2 - 130))

    if save_system.has_save():
        _button(surf, btn_continue, config.tr('CONTINUAR', 'CONTINUE'), active=True, font_key='body')
    _button(surf, btn_start, config.tr('EMPEZAR', 'START'), font_key='body')
    _button(surf, btn_names, config.tr('PERSONALIZAR NOMBRES', 'CUSTOMIZE NAMES'))
    _button(surf, btn_settings, config.tr('CONFIGURACIÓN', 'SETTINGS'))

    global sound_hint_rect
    hint = (config.tr('\U0001F50A sonido activado (click para silenciar)', '\U0001F50A sound on (click to mute)')
            if audio.sound_on else
            config.tr('\U0001F507 sonido silenciado (click para activar)', '\U0001F507 sound muted (click to unmute)'))
    htxt = font('tiny').render(hint, True, COL_GREY_DIM)
    sound_hint_rect = htxt.get_rect(center=(W // 2, H // 2 + 178))
    surf.blit(htxt, sound_hint_rect)


def click_start(pos):
    if save_system.has_save() and btn_continue.collidepoint(pos):
        return 'continue'
    if btn_start.collidepoint(pos):
        return 'game'
    if btn_names.collidepoint(pos):
        enter_names_screen()
        return 'names'
    if btn_settings.collidepoint(pos):
        return 'settings'
    if sound_hint_rect.collidepoint(pos):
        audio.toggle_sound()
    return None


# ─────────────────────────────────────────────
# PERSONALIZAR NOMBRES
# ─────────────────────────────────────────────
class TextField:
    def __init__(self, rect_, initial):
        self.rect = rect_
        self.text = initial
        self.active = False

    def handle_click(self, pos):
        self.active = self.rect.collidepoint(pos)
        return self.active

    def handle_textinput(self, char):
        if self.active and len(self.text) < 18 and char.isprintable():
            self.text += char

    def handle_backspace(self):
        if self.active:
            self.text = self.text[:-1]

    def draw(self, surf):
        pygame.draw.rect(surf, COL_PANEL, self.rect)
        pygame.draw.rect(surf, COL_PINK if self.active else COL_BORDER, self.rect, width=2)
        t = font('body').render(self.text, True, COL_CREAM)
        surf.blit(t, (self.rect.x + 10, self.rect.centery - t.get_height() // 2))
        if self.active and (pygame.time.get_ticks() // 500) % 2 == 0:
            cx = self.rect.x + 12 + t.get_width()
            pygame.draw.line(surf, COL_CREAM, (cx, self.rect.y + 8), (cx, self.rect.bottom - 8), 2)


field_b = TextField(pygame.Rect(W // 2 - 150, H // 2 - 70, 300, 44), config.name_b())
field_c = TextField(pygame.Rect(W // 2 - 150, H // 2 + 20, 300, 44), config.name_c())
btn_save = pygame.Rect(W // 2 - 110, H // 2 + 94, 220, 44)
btn_reset = pygame.Rect(W // 2 - 110, H // 2 + 148, 220, 38)
btn_back_names = pygame.Rect(20, 20, 90, 36)


def enter_names_screen():
    field_b.text = config.name_b()
    field_c.text = config.name_c()
    field_b.active = False
    field_c.active = False


def draw_names(surf):
    gradient_rect(surf, 0, 0, W, H, (26, 21, 48), (10, 10, 18))
    title = font('h1').render(config.tr('Nombres de los personajes', 'Character names'), True, COL_PINK)
    surf.blit(title, (W // 2 - title.get_width() // 2, H // 2 - 160))

    lbl_b = font('small').render(
        config.tr('Nombre de él (por defecto: Breyner)', 'His name (default: Breyner)'), True, COL_GREY)
    surf.blit(lbl_b, (field_b.rect.x, field_b.rect.y - 24))
    field_b.draw(surf)

    lbl_c = font('small').render(
        config.tr('Nombre de ella (por defecto: Cristel)', 'Her name (default: Cristel)'), True, COL_GREY)
    surf.blit(lbl_c, (field_c.rect.x, field_c.rect.y - 24))
    field_c.draw(surf)

    _button(surf, btn_save, config.tr('GUARDAR', 'SAVE'))
    _button(surf, btn_reset, config.tr('restablecer por defecto', 'reset to default'), font_key='tiny')
    _button(surf, btn_back_names, config.tr('\u2190 volver', '\u2190 back'), font_key='tiny')


def click_names(pos):
    field_b.handle_click(pos)
    field_c.handle_click(pos)
    if btn_save.collidepoint(pos):
        config.set_name_b(field_b.text)
        config.set_name_c(field_c.text)
        field_b.text, field_c.text = config.name_b(), config.name_c()
        return 'start'
    if btn_reset.collidepoint(pos):
        config.set_name_b('')
        config.set_name_c('')
        field_b.text, field_c.text = config.name_b(), config.name_c()
        return None
    if btn_back_names.collidepoint(pos):
        return 'start'
    return None


def keydown_names(key):
    if key == pygame.K_BACKSPACE:
        field_b.handle_backspace()
        field_c.handle_backspace()
    elif key == pygame.K_TAB:
        field_b.active, field_c.active = (not field_b.active), (not field_c.active)
    elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
        field_b.active = False
        field_c.active = False


def textinput_names(char):
    field_b.handle_textinput(char)
    field_c.handle_textinput(char)


# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
btn_vol_minus = pygame.Rect(W // 2 - 90, H // 2 - 96, 40, 36)
btn_vol_plus = pygame.Rect(W // 2 + 50, H // 2 - 96, 40, 36)
btn_lang_es = pygame.Rect(W // 2 - 100, H // 2 - 22, 90, 36)
btn_lang_en = pygame.Rect(W // 2 + 10, H // 2 - 22, 90, 36)
btn_ctrl_kb = pygame.Rect(W // 2 - 150, H // 2 + 52, 96, 36)
btn_ctrl_dpad = pygame.Rect(W // 2 - 48, H // 2 + 52, 96, 36)
btn_ctrl_touch = pygame.Rect(W // 2 + 54, H // 2 + 52, 96, 36)
btn_back_settings = pygame.Rect(20, 20, 90, 36)


def draw_settings(surf):
    gradient_rect(surf, 0, 0, W, H, (26, 21, 48), (10, 10, 18))
    title = font('h1').render(config.tr('Configuración', 'Settings'), True, COL_PINK)
    surf.blit(title, (W // 2 - title.get_width() // 2, H // 2 - 166))

    vol_lbl = font('small').render(
        config.tr('Volumen', 'Volume') + f': {int(round(config.volume * 100))}%', True, COL_GREY)
    surf.blit(vol_lbl, (W // 2 - vol_lbl.get_width() // 2, H // 2 - 124))
    _button(surf, btn_vol_minus, '-', font_key='body')
    _button(surf, btn_vol_plus, '+', font_key='body')

    lang_lbl = font('small').render(config.tr('Idioma', 'Language'), True, COL_GREY)
    surf.blit(lang_lbl, (W // 2 - lang_lbl.get_width() // 2, H // 2 - 50))
    _button(surf, btn_lang_es, 'Español', active=(config.language == 'es'))
    _button(surf, btn_lang_en, 'English', active=(config.language == 'en'))

    ctrl_lbl = font('small').render(config.tr('Controles', 'Controls'), True, COL_GREY)
    surf.blit(ctrl_lbl, (W // 2 - ctrl_lbl.get_width() // 2, H // 2 + 24))
    _button(surf, btn_ctrl_kb, config.tr('Teclado', 'Keyboard'), active=(config.control_scheme == 'keyboard'), font_key='tiny')
    _button(surf, btn_ctrl_dpad, 'GBA', active=(config.control_scheme == 'dpad'), font_key='tiny')
    _button(surf, btn_ctrl_touch, config.tr('Táctil', 'Touchpad'), active=(config.control_scheme == 'touchpad'), font_key='tiny')

    hint = font('tiny').render(
        config.tr('GBA/Táctil muestran controles en pantalla durante el juego',
                   'GBA/Touchpad show on-screen controls during gameplay'), True, COL_GREY_DIM)
    surf.blit(hint, (W // 2 - hint.get_width() // 2, H // 2 + 96))

    _button(surf, btn_back_settings, config.tr('\u2190 volver', '\u2190 back'), font_key='tiny')


def click_settings(pos):
    if btn_vol_minus.collidepoint(pos):
        config.set_volume(config.volume - 0.1)
    elif btn_vol_plus.collidepoint(pos):
        config.set_volume(config.volume + 0.1)
    elif btn_lang_es.collidepoint(pos):
        config.set_language('es')
    elif btn_lang_en.collidepoint(pos):
        config.set_language('en')
    elif btn_ctrl_kb.collidepoint(pos):
        config.set_control_scheme('keyboard')
    elif btn_ctrl_dpad.collidepoint(pos):
        config.set_control_scheme('dpad')
    elif btn_ctrl_touch.collidepoint(pos):
        config.set_control_scheme('touchpad')
    elif btn_back_settings.collidepoint(pos):
        return 'start'
    return None
