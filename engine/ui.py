"""
Capa de UI/interacción: diálogo con máquina de escribir, elecciones, hotspots,
inventario, tarjeta de escena, fundidos, progreso, caja de recuerdos (fotos +
fragmentos), minijuego de cartas. Puerto fiel de la lógica en el <script> del
HTML original (dialogueBox, choiceBox, hotspots, inventoryBar, panelOverlay,
cardGameOverlay, fadeOverlay, progress).
"""
import random
import pygame
import config
from . import audio
from .constants import W, H, font
from .drawing import rect, circle, gradient_rect
from .character_assets import get_portrait

# ───────────── DIÁLOGO ─────────────
dialogue_queue = []
dialogue_active = False
dialogue_speaker = ''
dialogue_full_text = ''
dialogue_shown_chars = 0
dialogue_next_char_tick = 0
on_dialogue_end = None
CHAR_INTERVAL_MS = 18

# ───────────── ELECCIONES ─────────────
choice_visible = False
choice_prompt = ''
choice_options = []       # [{'key','text','rect'}]
choice_callback = None
choice_hover = -1

# ───────────── HOTSPOTS ─────────────
hotspots = []
hover_hotspot = None

# ───────────── INVENTARIO ─────────────
inventory = []
inv_hover = -1

# ───────────── TOAST ─────────────
toast_text = ''
toast_until_ms = 0

# ───────────── TARJETA DE ESCENA ─────────────
scene_card_active = False
scene_card_eyebrow = ''
scene_card_title = ''
scene_card_desc = ''
scene_card_t0 = 0
scene_card_callback = None
scene_card_fired = False
SC_FADE_IN = 400
SC_HOLD = 3200
SC_FADE_OUT = 600

# ───────────── FUNDIDO ─────────────
fade_alpha = 0.0
fade_state = None   # None | 'out' | 'holding' | 'pending_in' | 'in'
fade_t0 = 0
fade_pending_cb = None
fade_fired = False

# ───────────── PROGRESO ─────────────
progress_current = 0
progress_total = 6

# ───────────── RECUERDOS ─────────────
memories_found = 0
fragments = []
polaroids = []   # [{'scene': i, 'draw': fn}]

def scene_names():
    return ['',
            config.tr('Detrás del curso', 'Behind the classroom'),
            config.tr('El portón negro', 'The black gate'),
            config.tr('El celular olvidado', 'The forgotten phone'),
            config.tr('22 de octubre', 'October 22nd'),
            config.tr('Parque Héroes del 41', 'Héroes del 41 Park'),
            config.tr('Su cumpleaños', 'Her birthday')]


def fragment_names():
    return ['',
            config.tr('Una rama seca de pino', 'A dry pine branch'),
            config.tr('El eco de tres besos', 'The echo of three kisses'),
            config.tr('La voz de su madre', "Her mother's voice"),
            config.tr('Las manos agarradas contra la pared', 'Hands held together against the wall'),
            config.tr('El "XD" dibujado a marcador', 'The "XD" drawn in marker'),
            config.tr('Una hoja del cubo infinito', 'A page from the infinity cube')]

# ───────────── TARJETA PERSISTENTE (créditos finales) ─────────────
persistent_card_active = False
persistent_card_eyebrow = ''
persistent_card_title = ''
persistent_card_lines = []
persistent_card_link_rect = pygame.Rect(0, 0, 0, 0)

memory_box_open = False
memory_box_tab = 'polaroids'
_mb_close_rect = pygame.Rect(0, 0, 0, 0)
_mb_tab_rects = {}

# ───────────── MINIJUEGO DE CARTAS ─────────────
card_game_active = False
card_deck = []        # [{'pairId','text','state','rect'}]
card_flipped = []
card_on_complete = None
card_match_count = 0
card_pairs_total = 0
card_pending_resolve = None   # None | 'mismatch' | 'finish'
card_pending_tick = 0

# ───────────── BOTONES SUPERIORES ─────────────
btn_sound_rect = pygame.Rect(W - 44, 10, 34, 34)
btn_memorybox_rect = pygame.Rect(W - 86, 10, 34, 34)

hint_text = ''  # se fija dinámicamente según el idioma al entrar a cada escena

# ───────────── LLAMADAS DIFERIDAS GENÉRICAS ─────────────
_delayed_calls = []   # [(trigger_tick, callback)]


def call_later(ms, callback):
    _delayed_calls.append((pygame.time.get_ticks() + ms, callback))


def _update_delayed(now):
    if not _delayed_calls:
        return
    remaining = []
    for trigger, cb in _delayed_calls:
        if now >= trigger:
            cb()
        else:
            remaining.append((trigger, cb))
    _delayed_calls[:] = remaining


def reset_all():
    global memories_found, fragments, polaroids, inventory, hotspots
    memories_found = 0
    fragments.clear()
    polaroids.clear()
    inventory.clear()
    hotspots.clear()


# ───────────────────────────────────────────────
# TEXTO
# ───────────────────────────────────────────────
def wrap_text(fnt, text, max_width):
    words = text.split(' ')
    lines = []
    cur = ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if fnt.size(trial)[0] <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ───────────────────────────────────────────────
# DIÁLOGO
# ───────────────────────────────────────────────
def queue_dialogue(lines, callback=None):
    global dialogue_queue, on_dialogue_end
    dialogue_queue = list(lines)
    on_dialogue_end = callback
    _show_next_line()


def _show_next_line():
    global dialogue_active, dialogue_speaker, dialogue_full_text, dialogue_shown_chars
    global on_dialogue_end, dialogue_next_char_tick
    if not dialogue_queue:
        dialogue_active = False
        if on_dialogue_end:
            cb = on_dialogue_end
            on_dialogue_end = None
            cb()
        return
    dialogue_active = True
    line = dialogue_queue.pop(0)
    dialogue_speaker = line.get('speaker', '')
    dialogue_full_text = line.get('text', '')
    dialogue_shown_chars = 0
    dialogue_next_char_tick = pygame.time.get_ticks() + CHAR_INTERVAL_MS
    audio.play_page_turn()


def dialogue_click():
    """Click durante diálogo: completa la línea si está escribiendo, o avanza."""
    global dialogue_shown_chars
    if dialogue_shown_chars < len(dialogue_full_text):
        dialogue_shown_chars = len(dialogue_full_text)
    else:
        _show_next_line()


def _update_dialogue(now):
    global dialogue_shown_chars, dialogue_next_char_tick
    if not dialogue_active:
        return
    if dialogue_shown_chars >= len(dialogue_full_text):
        return
    while now >= dialogue_next_char_tick and dialogue_shown_chars < len(dialogue_full_text):
        dialogue_shown_chars += 1
        dialogue_next_char_tick += CHAR_INTERVAL_MS


# ───────────────────────────────────────────────
# ELECCIONES
# ───────────────────────────────────────────────
def show_choice(prompt, options, callback):
    global choice_visible, choice_prompt, choice_options, choice_callback
    choice_prompt = prompt
    choice_callback = callback
    choice_options = []
    y = H - 150
    for key, text in options:
        r = pygame.Rect(26, y, W - 52, 40)
        choice_options.append({'key': key, 'text': text, 'rect': r})
        y += 48
    choice_visible = True


def choice_click(pos):
    global choice_visible
    for opt in choice_options:
        if opt['rect'].collidepoint(pos):
            audio.play_click()
            choice_visible = False
            cb = choice_callback
            if cb:
                cb(opt['key'])
            return True
    return False


# ───────────────────────────────────────────────
# HOTSPOTS
# ───────────────────────────────────────────────
def add_hotspot(x, y, w, h, label, action, disabled=False):
    hotspots.append({'rect': pygame.Rect(x, y, w, h), 'label': label,
                      'action': action, 'disabled': disabled, 'found': False})


def clear_hotspots():
    hotspots.clear()


def hotspot_at(pos):
    for h in hotspots:
        if not h['disabled'] and h['rect'].collidepoint(pos):
            return h
    return None


# ───────────────────────────────────────────────
# INVENTARIO
# ───────────────────────────────────────────────
def add_inventory_item(item_id, icon, name):
    if any(i['id'] == item_id for i in inventory):
        return
    inventory.append({'id': item_id, 'icon': icon, 'name': name})
    show_toast('+ ' + name)
    audio.play_pickup()


def has_item(item_id):
    return any(i['id'] == item_id for i in inventory)


def inventory_rects():
    rects = []
    y = 54
    for item in inventory:
        rects.append((pygame.Rect(W - 44, y, 34, 34), item))
        y += 40
    return rects


# ───────────────────────────────────────────────
# TOAST
# ───────────────────────────────────────────────
def show_toast(text):
    global toast_text, toast_until_ms
    toast_text = text
    toast_until_ms = pygame.time.get_ticks() + 1800


# ───────────────────────────────────────────────
# TARJETA DE ESCENA
# ───────────────────────────────────────────────
def show_scene_card(eyebrow, title, desc, callback):
    global scene_card_active, scene_card_eyebrow, scene_card_title, scene_card_desc
    global scene_card_t0, scene_card_callback, scene_card_fired
    scene_card_eyebrow = eyebrow
    scene_card_title = title
    scene_card_desc = desc
    scene_card_callback = callback
    scene_card_t0 = pygame.time.get_ticks()
    scene_card_fired = False
    scene_card_active = True


def _update_scene_card(now):
    global scene_card_active, scene_card_fired
    if not scene_card_active:
        return
    elapsed = now - scene_card_t0
    total = SC_HOLD + SC_FADE_OUT
    if elapsed >= total and not scene_card_fired:
        scene_card_fired = True
        scene_card_active = False
        cb = scene_card_callback
        if cb:
            cb()


def _scene_card_alpha(now):
    elapsed = now - scene_card_t0
    if elapsed < SC_FADE_IN:
        return elapsed / SC_FADE_IN
    if elapsed < SC_HOLD:
        return 1.0
    if elapsed < SC_HOLD + SC_FADE_OUT:
        return max(0.0, 1 - (elapsed - SC_HOLD) / SC_FADE_OUT)
    return 0.0


# ───────────────────────────────────────────────
# FUNDIDO (transición entre escenas)
# ───────────────────────────────────────────────
def fade_out(callback):
    global fade_state, fade_t0, fade_pending_cb, fade_fired
    fade_state = 'out'
    fade_t0 = pygame.time.get_ticks()
    fade_pending_cb = callback
    fade_fired = False


def fade_in():
    global fade_state, fade_t0
    fade_state = 'pending_in'
    fade_t0 = pygame.time.get_ticks()


def _update_fade(now):
    global fade_alpha, fade_state, fade_t0, fade_fired
    if fade_state == 'out':
        elapsed = now - fade_t0
        fade_alpha = min(1.0, elapsed / 600)
        if elapsed >= 650 and not fade_fired:
            fade_fired = True
            cb = fade_pending_cb
            fade_state = 'holding'
            if cb:
                cb()
    elif fade_state == 'pending_in':
        if now - fade_t0 >= 50:
            fade_state = 'in'
            fade_t0 = now
    elif fade_state == 'in':
        elapsed = now - fade_t0
        fade_alpha = max(0.0, 1 - elapsed / 600)
        if elapsed >= 600:
            fade_state = None


# ───────────────────────────────────────────────
# PROGRESO
# ───────────────────────────────────────────────
def render_progress(current, total):
    global progress_current, progress_total
    progress_current = current
    progress_total = total


# ───────────────────────────────────────────────
# RECUERDOS: fotos + fragmentos
# ───────────────────────────────────────────────
def capture_polaroid(scene_index, draw_fn):
    polaroids.append({'scene': scene_index, 'draw': draw_fn})


def collect_fragment(scene_index):
    if scene_index not in fragments:
        fragments.append(scene_index)
        show_toast('\u2726 ' + config.tr('Fragmento encontrado: ', 'Fragment found: ') + fragment_names()[scene_index])
        audio.play_pickup()


def show_persistent_card(eyebrow, title, desc_lines):
    global persistent_card_active, persistent_card_eyebrow, persistent_card_title, persistent_card_lines
    persistent_card_active = True
    persistent_card_eyebrow = eyebrow
    persistent_card_title = title
    persistent_card_lines = desc_lines


def open_memory_box():
    global memory_box_open
    memory_box_open = True


def close_memory_box():
    global memory_box_open
    memory_box_open = False


def memory_box_click(pos):
    global memory_box_tab
    if _mb_close_rect.collidepoint(pos):
        audio.play_click()
        close_memory_box()
        return True
    for tab, r in _mb_tab_rects.items():
        if r.collidepoint(pos):
            audio.play_click()
            memory_box_tab = tab
            return True
    return True  # el overlay consume cualquier click dentro de él


# ───────────────────────────────────────────────
# MINIJUEGO DE CARTAS DE MEMORIA
# ───────────────────────────────────────────────
def start_memory_card_game(pairs, on_complete):
    global card_game_active, card_deck, card_flipped, card_on_complete
    global card_match_count, card_pairs_total, card_pending_resolve
    card_on_complete = on_complete
    card_pairs_total = len(pairs)
    card_match_count = 0
    card_flipped = []
    card_pending_resolve = None

    deck_data = []
    for idx, p in enumerate(pairs):
        deck_data.append({'pairId': idx, 'text': p['text']})
        deck_data.append({'pairId': idx, 'text': p['text']})
    random.shuffle(deck_data)

    cols, card_w, card_h, gap = 4, 90, 110, 10
    grid_w = cols * card_w + (cols - 1) * gap
    start_x = (W - grid_w) // 2
    start_y = (H - (2 * card_h + gap)) // 2

    card_deck = []
    for i, data in enumerate(deck_data):
        col = i % cols
        row = i // cols
        x = start_x + col * (card_w + gap)
        y = start_y + row * (card_h + gap)
        card_deck.append({'pairId': data['pairId'], 'text': data['text'],
                           'state': 'hidden', 'rect': pygame.Rect(x, y, card_w, card_h)})
    card_game_active = True


def card_click(pos):
    global card_flipped, card_match_count, card_pending_resolve, card_pending_tick
    if card_pending_resolve is not None:
        return True  # esperando a que se resuelva el par anterior
    now = pygame.time.get_ticks()
    for card in card_deck:
        if card['state'] != 'hidden':
            continue
        if card['rect'].collidepoint(pos):
            card['state'] = 'flipped'
            audio.play_click()
            card_flipped.append(card)
            if len(card_flipped) == 2:
                a, b = card_flipped
                if a['pairId'] == b['pairId']:
                    a['state'] = 'matched'
                    b['state'] = 'matched'
                    audio.play_match()
                    card_match_count += 1
                    if card_match_count == card_pairs_total:
                        card_pending_resolve = 'finish'
                        card_pending_tick = now + 700
                    else:
                        card_flipped = []
                else:
                    audio.play_mismatch()
                    card_pending_resolve = 'mismatch'
                    card_pending_tick = now + 800
            return True
    return True


def _update_card_game(now):
    global card_pending_resolve, card_flipped, card_game_active, card_on_complete
    if card_pending_resolve is None:
        return
    if now < card_pending_tick:
        return
    if card_pending_resolve == 'mismatch':
        for c in card_flipped:
            if c['state'] == 'flipped':
                c['state'] = 'hidden'
        card_flipped = []
        card_pending_resolve = None
    elif card_pending_resolve == 'finish':
        card_game_active = False
        card_pending_resolve = None
        cb = card_on_complete
        card_on_complete = None
        if cb:
            cb()


# ───────────────────────────────────────────────
# ACTUALIZACIÓN GENERAL (llamar 1x por frame)
# ───────────────────────────────────────────────
def update(now):
    global toast_text
    _update_dialogue(now)
    _update_scene_card(now)
    _update_fade(now)
    _update_card_game(now)
    _update_delayed(now)
    if toast_text and now >= toast_until_ms:
        toast_text = ''


def blocking_ui():
    return (dialogue_active or choice_visible or card_game_active
            or memory_box_open or persistent_card_active)


# ───────────────────────────────────────────────
# MANEJO DE CLICKS (orden de prioridad, como el JS original)
# ───────────────────────────────────────────────
def handle_click(pos):
    """Devuelve True si el click fue consumido por la UI."""
    if memory_box_open:
        return memory_box_click(pos)
    if card_game_active:
        return card_click(pos)
    if choice_visible:
        return choice_click(pos)
    if dialogue_active:
        dialogue_click()
        return True

    if persistent_card_active:
        if persistent_card_link_rect.collidepoint(pos):
            audio.play_click()
            open_memory_box()
        return True  # la tarjeta cubre toda la pantalla (igual que el original)

    if btn_sound_rect.collidepoint(pos):
        audio.play_click()
        audio.toggle_sound()
        return True
    if btn_memorybox_rect.collidepoint(pos):
        audio.play_click()
        open_memory_box()
        return True

    hs = hotspot_at(pos)
    if hs:
        hs['found'] = True
        audio.play_click()
        hs['action']()
        return True
    return False


def handle_mousemotion(pos):
    global hover_hotspot, choice_hover, inv_hover
    hover_hotspot = hotspot_at(pos) if not blocking_ui() else None
    if choice_visible:
        choice_hover = -1
        for i, opt in enumerate(choice_options):
            if opt['rect'].collidepoint(pos):
                choice_hover = i
                break
    inv_hover = -1
    for i, (r, item) in enumerate(inventory_rects()):
        if r.collidepoint(pos):
            inv_hover = i
            break


# ═════════════════════════════════════════════════
# DIBUJO
# ═════════════════════════════════════════════════
COL_CREAM = (244, 233, 216)
COL_PINK = (232, 163, 176)
COL_BLUE = (163, 201, 232)
COL_GREY = (154, 143, 174)
COL_GREY_DIM = (122, 112, 144)
COL_GREY_FAINT = (90, 80, 112)
COL_BORDER = (74, 64, 96)
COL_BORDER_DIM = (58, 52, 80)
COL_PANEL_BG = (42, 36, 56)


def draw(surf, anim_frame):
    _draw_progress(surf)
    _draw_hotspot_label(surf)
    _draw_hint(surf)
    _draw_toast(surf)
    _draw_top_buttons(surf)
    _draw_inventory(surf)
    if dialogue_active:
        _draw_dialogue(surf)
    if choice_visible:
        _draw_choice(surf)
    if scene_card_active:
        _draw_scene_card(surf)
    if persistent_card_active:
        _draw_persistent_card(surf)
    if card_game_active:
        _draw_card_game(surf)
    if memory_box_open:
        _draw_memory_box(surf)
    _draw_fade(surf)


def _panel_bg(surf, rect_, color, alpha):
    s = pygame.Surface((rect_.w, rect_.h), pygame.SRCALPHA)
    s.fill((*color, alpha))
    surf.blit(s, rect_.topleft)


def _draw_progress(surf):
    total = max(1, progress_total)
    spacing = 16
    start_x = W // 2 - (total - 1) * spacing // 2
    for i in range(total):
        x = start_x + i * spacing
        if i < progress_current:
            col = COL_PINK
        elif i == progress_current:
            col = COL_BLUE
        else:
            col = COL_PANEL_BG
        pygame.draw.circle(surf, col, (x, 18), 5)
        pygame.draw.circle(surf, COL_BORDER, (x, 18), 5, width=1)


def _draw_hotspot_label(surf):
    if blocking_ui() or not hover_hotspot:
        return
    label = ('\u2713 ' if hover_hotspot['found'] else '') + hover_hotspot['label']
    txt = font('tiny').render(label, True, COL_CREAM)
    pad = 6
    box = pygame.Rect(hover_hotspot['rect'].x, max(0, hover_hotspot['rect'].y - 30),
                       txt.get_width() + pad * 2, txt.get_height() + pad)
    pygame.draw.rect(surf, (26, 26, 36), box)
    pygame.draw.rect(surf, COL_CREAM, box, width=2)
    surf.blit(txt, (box.x + pad, box.y + pad // 2))


def _draw_hint(surf):
    text = hint_text or config.tr('haz clic para explorar', 'click to explore')
    txt = font('tiny').render(text, True, COL_GREY_FAINT)
    surf.blit(txt, (W // 2 - txt.get_width() // 2, H - 20))


def _draw_toast(surf):
    if not toast_text:
        return
    txt = font('small').render(toast_text, True, COL_CREAM)
    box = pygame.Rect(0, 54, txt.get_width() + 36, txt.get_height() + 16)
    box.centerx = W // 2
    _panel_bg(surf, box, (20, 18, 30), 235)
    pygame.draw.rect(surf, COL_PINK, box, width=2)
    surf.blit(txt, (box.x + 18, box.y + 8))


def _draw_top_buttons(surf):
    for r, active in ((btn_sound_rect, audio.sound_on), (btn_memorybox_rect, True)):
        _panel_bg(surf, r, (20, 18, 30), 210)
        pygame.draw.rect(surf, COL_BORDER, r, width=2)
    icon = '\U0001F50A' if audio.sound_on else '\U0001F507'
    _blit_center(surf, font('icon_small'), icon, btn_sound_rect.center, COL_CREAM)
    _blit_center(surf, font('icon_small'), '\U0001F4E6', btn_memorybox_rect.center, COL_CREAM)


def _blit_center(surf, fnt, text, center, color):
    try:
        t = fnt.render(text, True, color)
    except Exception:
        t = fnt.render('?', True, color)
    surf.blit(t, t.get_rect(center=center))


def _draw_inventory(surf):
    for i, (r, item) in enumerate(inventory_rects()):
        _panel_bg(surf, r, (20, 18, 30), 220)
        pygame.draw.rect(surf, COL_BORDER, r, width=2)
        _blit_center(surf, font('icon_small'), item['icon'], r.center, COL_CREAM)
        if inv_hover == i:
            tip = font('tiny').render(item['name'], True, COL_CREAM)
            tipbox = pygame.Rect(r.x - tip.get_width() - 16, r.centery - tip.get_height() // 2 - 3,
                                  tip.get_width() + 12, tip.get_height() + 6)
            pygame.draw.rect(surf, (26, 26, 36), tipbox)
            pygame.draw.rect(surf, COL_CREAM, tipbox, width=1)
            surf.blit(tip, (tipbox.x + 6, tipbox.y + 3))


def _draw_dialogue(surf):
    box = pygame.Rect(0, H - 158, W, 158)
    _panel_bg(surf, box, (8, 7, 13), 250)
    pygame.draw.line(surf, COL_BORDER_DIM, (0, box.y), (W, box.y), 3)

    # Retrato opcional de Breyner. Si el recurso falta, la caja conserva
    # exactamente el diseño de texto anterior.
    portrait = None
    if dialogue_speaker:
        speaker_key = str(dialogue_speaker).strip().lower()
        if dialogue_speaker == config.name_b() or 'breyner' in speaker_key:
            portrait = get_portrait('breyner', (92, 116))
        elif dialogue_speaker == config.name_c() or 'cristel' in speaker_key:
            portrait = get_portrait('cristel', (92, 116))
        elif 'madre' in speaker_key or 'mamá' in speaker_key or 'mama' in speaker_key:
            portrait = get_portrait('madre_cristel', (92, 116))
    text_x = 26
    text_width = W - 60
    if portrait is not None:
        portrait_box = pygame.Rect(18, box.y + 20, 100, 122)
        pygame.draw.rect(surf, COL_BORDER, portrait_box, border_radius=7)
        portrait_rect = portrait.get_rect(center=portrait_box.center)
        surf.blit(portrait, portrait_rect)
        text_x = 136
        text_width = W - text_x - 28

    speaker_col = COL_BLUE if dialogue_speaker == config.name_c() else COL_PINK
    if dialogue_speaker:
        sp = font('speaker').render(dialogue_speaker.upper(), True, speaker_col)
        surf.blit(sp, (text_x, box.y + 14))

    shown = dialogue_full_text[:dialogue_shown_chars]
    lines = wrap_text(font('body'), shown, text_width)
    ty = box.y + 36
    for ln in lines[:4]:
        t = font('body').render(ln, True, COL_CREAM)
        surf.blit(t, (text_x, ty))
        ty += 22

    if dialogue_shown_chars >= len(dialogue_full_text):
        hint = font('tiny').render(config.tr('\u25b8 click para continuar', '\u25b8 click to continue'), True, COL_GREY_DIM)
        surf.blit(hint, (W - hint.get_width() - 24, box.y + 136))


def _draw_choice(surf):
    box = pygame.Rect(0, H - 150 - 36, W, 150 + 36)
    _panel_bg(surf, box, (8, 7, 13), 250)
    pygame.draw.line(surf, COL_BORDER_DIM, (0, box.y), (W, box.y), 3)
    prompt = font('tiny').render(choice_prompt.upper(), True, COL_GREY)
    surf.blit(prompt, (26, box.y + 14))
    for i, opt in enumerate(choice_options):
        hovered = (i == choice_hover)
        bg = (255, 255, 255, 14) if not hovered else (*COL_PINK, 30)
        _panel_bg(surf, opt['rect'], bg[:3], bg[3])
        pygame.draw.rect(surf, COL_PINK if hovered else COL_BORDER, opt['rect'], width=2)
        t = font('small').render(opt['text'], True, COL_CREAM)
        surf.blit(t, (opt['rect'].x + 14, opt['rect'].centery - t.get_height() // 2))


def _draw_scene_card(surf):
    alpha = int(max(0.0, min(1.0, _scene_card_alpha(pygame.time.get_ticks()))) * 255)
    if alpha <= 0:
        return
    bgsurf = pygame.Surface((W, H), pygame.SRCALPHA)
    bgsurf.fill((10, 10, 18, alpha))
    surf.blit(bgsurf, (0, 0))

    eyebrow = font('eyebrow').render(scene_card_eyebrow.upper(), True, (*COL_PINK,))
    eyebrow.set_alpha(alpha)
    title = font('h1').render(scene_card_title, True, COL_CREAM)
    title.set_alpha(alpha)
    surf.blit(eyebrow, (W // 2 - eyebrow.get_width() // 2, H // 2 - 70))
    surf.blit(title, (W // 2 - title.get_width() // 2, H // 2 - 40))

    desc_lines = wrap_text(font('small'), scene_card_desc, 480)
    ty = H // 2 + 18
    for ln in desc_lines:
        t = font('small').render(ln, True, COL_GREY)
        t.set_alpha(alpha)
        surf.blit(t, (W // 2 - t.get_width() // 2, ty))
        ty += 22


def _draw_persistent_card(surf):
    global persistent_card_link_rect
    bgsurf = pygame.Surface((W, H), pygame.SRCALPHA)
    bgsurf.fill((10, 10, 18, 255))
    surf.blit(bgsurf, (0, 0))

    eyebrow = font('eyebrow').render(persistent_card_eyebrow.upper(), True, COL_PINK)
    title = font('h1').render(persistent_card_title, True, COL_CREAM)
    surf.blit(eyebrow, (W // 2 - eyebrow.get_width() // 2, H // 2 - 90))
    surf.blit(title, (W // 2 - title.get_width() // 2, H // 2 - 58))

    ty = H // 2
    for ln in persistent_card_lines:
        t = font('small').render(ln, True, COL_GREY)
        surf.blit(t, (W // 2 - t.get_width() // 2, ty))
        ty += 22

    ty += 10
    link = font('small').render(config.tr('ver caja de recuerdos completa', 'view the full memory box'), True, COL_BLUE)
    link_rect = link.get_rect(center=(W // 2, ty))
    surf.blit(link, link_rect)
    pygame.draw.line(surf, COL_BLUE, (link_rect.x, link_rect.bottom),
                      (link_rect.right, link_rect.bottom), 1)
    persistent_card_link_rect = link_rect.inflate(20, 14)


def _draw_card_game(surf):
    bgsurf = pygame.Surface((W, H), pygame.SRCALPHA)
    bgsurf.fill((8, 7, 14, 247))
    surf.blit(bgsurf, (0, 0))
    title = font('eyebrow').render(config.tr('RECONSTRUYENDO EL RECUERDO', 'REBUILDING THE MEMORY'), True, COL_PINK)
    surf.blit(title, (W // 2 - title.get_width() // 2, 70))
    sub = font('tiny').render(config.tr('encuentra los pares para ayudar a {c} a recordar',
                                         'find the pairs to help {c} remember'),
                               True, COL_GREY_DIM)
    surf.blit(sub, (W // 2 - sub.get_width() // 2, 96))

    for card in card_deck:
        r = card['rect']
        if card['state'] == 'matched':
            s = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            s.fill((58, 52, 80, 120))
            surf.blit(s, r.topleft)
            pygame.draw.rect(surf, COL_BLUE, r, width=2)
        elif card['state'] == 'flipped':
            pygame.draw.rect(surf, (58, 52, 80), r)
            pygame.draw.rect(surf, COL_PINK, r, width=2)
            lines = wrap_text(font('tiny'), card['text'], r.w - 14)
            ty = r.centery - (len(lines) * 14) // 2
            for ln in lines:
                t = font('tiny').render(ln, True, (232, 216, 200))
                surf.blit(t, (r.centerx - t.get_width() // 2, ty))
                ty += 16
        else:
            pygame.draw.rect(surf, COL_PANEL_BG, r)
            pygame.draw.rect(surf, COL_BORDER, r, width=2)
            _blit_center(surf, font('icon'), '\u2726', r.center, COL_GREY_FAINT)


def _draw_memory_box(surf):
    global _mb_close_rect, _mb_tab_rects
    bgsurf = pygame.Surface((W, H), pygame.SRCALPHA)
    bgsurf.fill((8, 7, 14, 245))
    surf.blit(bgsurf, (0, 0))

    title = font('h1').render(config.tr('CAJA DE RECUERDOS', 'MEMORY BOX'), True, COL_PINK)
    surf.blit(title, (W // 2 - title.get_width() // 2, 36))
    sub = font('tiny').render(config.tr('fragmentos y fotografías de lo vivido', 'fragments and photographs of what was lived'), True, COL_GREY_DIM)
    surf.blit(sub, (W // 2 - sub.get_width() // 2, 72))

    tabs = [('polaroids', config.tr('Fotografías', 'Photographs')), ('fragments', config.tr('Fragmentos', 'Fragments'))]
    tab_w, tab_h = 150, 30
    tx = W // 2 - (tab_w * 2 + 10) // 2
    _mb_tab_rects = {}
    for key, label in tabs:
        r = pygame.Rect(tx, 100, tab_w, tab_h)
        _mb_tab_rects[key] = r
        active = (memory_box_tab == key)
        pygame.draw.rect(surf, COL_PANEL_BG if active else (20, 18, 30), r)
        pygame.draw.rect(surf, COL_PINK if active else COL_BORDER_DIM, r, width=1)
        t = font('tiny').render(label.upper(), True, COL_PINK if active else COL_GREY_DIM)
        surf.blit(t, (r.centerx - t.get_width() // 2, r.centery - t.get_height() // 2))
        tx += tab_w + 10

    grid_top = 150
    cols = 4
    cell_w, cell_h, gap = 170, 130, 16
    grid_w = cols * cell_w + (cols - 1) * gap
    start_x = W // 2 - grid_w // 2

    if memory_box_tab == 'polaroids':
        for i in range(1, 7):
            idx = i - 1
            col = idx % cols
            row = idx // cols
            x = start_x + col * (cell_w + gap)
            y = grid_top + row * (cell_h + gap)
            found = next((p for p in polaroids if p['scene'] == i), None)
            card = pygame.Rect(x, y, cell_w, cell_h)
            pygame.draw.rect(surf, (244, 236, 224) if found else COL_PANEL_BG, card)
            thumb_rect = pygame.Rect(x + 8, y + 8, cell_w - 16, cell_h - 36)
            thumb = pygame.Surface((thumb_rect.w, thumb_rect.h))
            if found:
                try:
                    found['draw'](thumb, thumb_rect.w, thumb_rect.h)
                except Exception:
                    thumb.fill((26, 22, 34))
                cap_col = (58, 40, 24)
                cap_text = scene_names()[i]
            else:
                thumb.fill((26, 22, 34))
                _blit_center(thumb, font('h1'), '?', (thumb_rect.w // 2, thumb_rect.h // 2), COL_BORDER_DIM)
                cap_col = (90, 80, 112)
                cap_text = '???'
            surf.blit(thumb, thumb_rect.topleft)
            cap = font('tiny').render(cap_text, True, cap_col)
            surf.blit(cap, (card.centerx - cap.get_width() // 2, y + cell_h - 22))
    else:
        y = grid_top
        for i in range(1, 7):
            found = i in fragments
            r = pygame.Rect(W // 2 - 300, y, 600, 40)
            col = (*COL_PINK, 20) if found else (58, 52, 80, 60)
            _panel_bg(surf, r, col[:3], col[3])
            pygame.draw.rect(surf, (*COL_PINK, 80) if found else COL_BORDER_DIM, r, width=1)
            txt = ('\u2726 ' + fragment_names()[i]) if found else '\u2726 ??? \u2014 ' + config.tr('sigue explorando esta escena', 'keep exploring this scene')
            t = font('small').render(txt, True, (232, 216, 200) if found else COL_GREY_FAINT)
            surf.blit(t, (r.x + 14, r.centery - t.get_height() // 2))
            y += 48

    close_w, close_h = 160, 38
    _mb_close_rect = pygame.Rect(W // 2 - close_w // 2, H - 60, close_w, close_h)
    pygame.draw.rect(surf, (10, 9, 16), _mb_close_rect)
    pygame.draw.rect(surf, COL_PINK, _mb_close_rect, width=2)
    t = font('small').render(config.tr('CERRAR', 'CLOSE'), True, COL_CREAM)
    surf.blit(t, (_mb_close_rect.centerx - t.get_width() // 2, _mb_close_rect.centery - t.get_height() // 2))


def _draw_fade(surf):
    if fade_alpha <= 0.001:
        return
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    s.fill((0, 0, 0, int(fade_alpha * 255)))
    surf.blit(s, (0, 0))
