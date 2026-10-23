"""
Epílogos de Olvido (Bloque 4).

Tres pantallas independientes, encadenadas por un EpilogueManager:
    1. ReflectionScreen  - texto reflexivo de cierre
    2. BusFarewell       - despedida en la parada, cruce de frontera narrado
    3. FinalPhoto        - foto final, 4 frases, fundido lento a negro

Cada pantalla es una clase que cumple el contrato de `Epilogue`
(enter / update / draw / handle_click / exit). Para añadir o quitar una
pantalla basta editar la lista pasada a EpilogueManager al final del archivo.
Al terminar la última se llama a `on_finish` (los créditos).

Va en la raíz de olvido_py/, junto a room.py y commute.py.
Todas las pantallas desactivan el pixelado: el arte nuevo debe verse nítido.
"""
import os
import pygame
import config
from engine import ui, audio, drawing
from engine.constants import W, H, PALETTE_BREYNER, font
from engine.drawing import rect, circle, gradient_rect, tile_ground, \
    draw_character_static, draw_walk_character

_ROOT = os.path.dirname(os.path.abspath(__file__))
_IMG_CACHE = {}

# ───────── TEXTOS EDITABLES ─────────
# Las 4 frases finales (es, en). Se muestran en cuadros de texto, una por clic.
FINAL_SPEAKER = ''   # pon config.name_b() si quieres mostrar su retrato y nombre
FINAL_PHRASES = [
    ('Nunca pude recuperarme al final de todo, amor mío.',
     'I never managed to recover from it all, my love.'),
    ('Yo solo quería que fueras feliz conmigo, pero al menos sé que si tú estás bien, '
     'yo lo estaré en alguna parte de mi corazón.',
     "I only wanted you to be happy with me, but at least I know that if you're okay, "
     "I'll be okay somewhere in my heart."),
    ('Todas las noches pienso en ti y supongo que lo haré hasta el final de mis días. '
     'Te amo mucho y gracias por todo. No te soltaré, pero quiero que seas feliz a tu manera.',
     "Every night I think of you, and I suppose I will until the end of my days. "
     "I love you so much, and thank you for everything. I won't let go of you, "
     "but I want you to be happy in your own way."),
    ('Aunque ya no me dejes ni siquiera ser tu amigo o parte de ella, cuídate mucho.',
     'Even if you no longer let me be your friend, or even a part of it, take care of yourself.'),
]

# Audio opcional (formato .ogg, el más seguro con pygbag). Si faltan, no se rompe nada.
AUDIO_MUSIC = ('assets', 'audio', 'melancolia.ogg')   # música melancólica en loop
AUDIO_SOBS = ('assets', 'audio', 'sollozos.ogg')      # sollozos leves (~10 s)
# Respaldo sintetizado si no hay música: melodía escasa (frecuencia Hz, retraso s).
MELODY = [(220.0, 1), (261.63, 5), (329.63, 9), (293.66, 14), (261.63, 19), (220.0, 24)]


# ───────── UTILIDADES ─────────
def _load_image(rel_path):
    """Carga y escala a 960x600 una sola vez. Devuelve None si falta el archivo."""
    if rel_path not in _IMG_CACHE:
        try:
            img = pygame.image.load(os.path.join(_ROOT, *rel_path.split('/'))).convert()
            _IMG_CACHE[rel_path] = pygame.transform.smoothscale(img, (W, H))
        except (pygame.error, OSError):
            _IMG_CACHE[rel_path] = None
    return _IMG_CACHE[rel_path]


def _clamp01(x):
    return max(0.0, min(1.0, x))


def _ease_out(t):
    return 1 - (1 - t) ** 3


def _ease_in(t):
    return t * t


def _blit_alpha(surf, img, alpha01, pos):
    img.set_alpha(int(_clamp01(alpha01) * 255))
    surf.blit(img, pos)


def _play_music():
    """Música de fondo desde archivo. Devuelve True si pudo reproducirla."""
    if not audio.sound_on:
        return False
    try:
        pygame.mixer.music.load(os.path.join(_ROOT, *AUDIO_MUSIC))
        pygame.mixer.music.set_volume(config.volume * 0.6)
        pygame.mixer.music.play(loops=-1, fade_ms=3000)
        return True
    except (pygame.error, OSError):
        return False


def _play_sobs():
    """Sollozos leves desde archivo; si no existe, simplemente no suenan."""
    if not audio.sound_on:
        return
    try:
        snd = pygame.mixer.Sound(os.path.join(_ROOT, *AUDIO_SOBS))
        snd.set_volume(config.volume * 0.4)
        snd.play(fade_ms=1500)
    except (pygame.error, OSError):
        pass


# ───────── CONTRATO BASE ─────────
class Epilogue:
    """Contrato común. Una pantalla pide avanzar poniendo `self.done = True`."""

    def __init__(self):
        self.t0 = 0
        self.done = False

    def enter(self, now):
        self.t0 = now
        self.done = False

    def update(self, now):
        pass

    def draw(self, surf, now):
        pass

    def handle_click(self, pos):
        """Devuelve True si consumió el click."""
        return False

    def exit(self):
        pass


# ───────── 1) PANTALLA REFLEXIVA ─────────
class ReflectionScreen(Epilogue):
    FIRST_DELAY = 800
    LINE_GAP = 2800
    FADE = 1500

    def enter(self, now):
        super().enter(now)
        self.lines = [
            config.tr('No todo lo que se olvida se pierde.',
                      'Not everything that is forgotten is lost.'),
            config.tr('A veces se queda como un color, una canción, una sensación sin nombre.',
                      'Sometimes it stays as a color, a song, a feeling with no name.'),
            config.tr('Y recordar por los dos también es una forma de quedarse.',
                      'And remembering for both of us is also a way of staying.'),
        ]
        self.ready_ms = (self.FIRST_DELAY + (len(self.lines) - 1) * self.LINE_GAP
                         + self.FADE + 800)
        audio.start_ambient(130)
        ui.hint_text = ' '

    def draw(self, surf, now):
        gradient_rect(surf, 0, 0, W, H, (16, 13, 28), (4, 4, 10))
        el = now - self.t0
        fnt = font('h1')
        line_h, para_gap = 38, 26
        blocks = []
        for i, text in enumerate(self.lines):
            a = _clamp01((el - self.FIRST_DELAY - i * self.LINE_GAP) / self.FADE)
            blocks.append((a, ui.wrap_text(fnt, text, 760)))
        total = sum(len(rows) * line_h for _, rows in blocks) + para_gap * (len(blocks) - 1)
        y = (H - total) // 2
        for a, rows in blocks:
            for row in rows:
                img = fnt.render(row, True, (244, 233, 216))
                _blit_alpha(surf, img, a, img.get_rect(midtop=(W // 2, y)).topleft)
                y += line_h
            y += para_gap
        if el >= self.ready_ms and (now // 600) % 2 == 0:
            hint = font('tiny').render(config.tr('toca para continuar', 'tap to continue'),
                                       True, (122, 112, 144))
            surf.blit(hint, hint.get_rect(center=(W // 2, H - 40)))

    def handle_click(self, pos):
        if pygame.time.get_ticks() - self.t0 >= self.ready_ms:
            self.done = True
        else:
            self.t0 -= 100000   # saltar la animación: todo visible de golpe
        return True


# ───────── 2) DESPEDIDA EN LA PARADA ─────────
class BusFarewell(Epilogue):
    BUS_REST_X = 360
    BUS_W = 220
    ARRIVE_MS = 3000
    WALK_MS = 1500
    DEPART_MS = 4500
    GROUND_Y = 540

    def enter(self, now):
        super().enter(now)
        self.phase = 'wait'          # wait → arrive → board → walk → depart → border
        self.phase_t0 = now
        self.bus_x = -float(self.BUS_W + 80)
        self.breyner_x = 300.0
        self.family = self._build_family()
        audio.start_ambient(175)
        ui.clear_hotspots()
        ui.hint_text = ' '
        ui.call_later(900, self._first_dialogue)

    # --- secuencia narrativa (texto editable) ---
    def _first_dialogue(self):
        b = config.name_b()
        ui.queue_dialogue([
            {'speaker': '', 'text': config.tr(
                'La parada se llenó de gente que no era de la parada. Su familia lo acompañó hasta el final.',
                'The stop filled with people who did not belong to the stop. His family stayed with him to the end.')},
            {'speaker': '', 'text': config.tr(
                'Desde donde estaba, eran solo siluetas contra la luz. Era más fácil así.',
                'From where he stood, they were only silhouettes against the light. It was easier that way.')},
            {'speaker': b, 'text': config.tr(
                'No dije mucho. Los abrazos hablaron por mí.',
                "I didn't say much. The hugs spoke for me.")},
        ], lambda: self._set_phase('arrive'))

    def _board_dialogue(self):
        ui.queue_dialogue([
            {'speaker': config.name_b(), 'text': config.tr(
                'Subí sin voltear. Si volteaba, no me iba.',
                "I got on without turning around. If I turned, I wouldn't leave.")},
        ], lambda: self._set_phase('walk'))

    def _border_dialogue(self):
        ui.queue_dialogue([
            {'speaker': '', 'text': config.tr(
                'El bus avanzó hacia el norte. Tulcán. El puente de Rumichaca.',
                'The bus headed north. Tulcán. The Rumichaca bridge.')},
            {'speaker': '', 'text': config.tr(
                'Un sello, una fila, un papel. Y al otro lado, Ipiales: otro país, el mismo cielo.',
                'A stamp, a line, a piece of paper. And on the other side, Ipiales: another country, the same sky.')},
            {'speaker': config.name_b(), 'text': config.tr(
                'Dejé mi casa, a mi gente y una historia a medias. Pero la llevaba conmigo.',
                'I left my home, my people, and a half-told story. But I carried it with me.')},
        ], self._finish)

    def _finish(self):
        self.done = True

    def _set_phase(self, phase):
        self.phase = phase
        self.phase_t0 = pygame.time.get_ticks()
        if phase == 'board':
            self._board_dialogue()
        elif phase == 'border':
            self._border_dialogue()

    # --- animación ---
    def update(self, now):
        t = now - self.phase_t0
        rest, off = self.BUS_REST_X, W + 120
        if self.phase == 'arrive':
            k = _clamp01(t / self.ARRIVE_MS)
            self.bus_x = -self.BUS_W - 80 + (rest + self.BUS_W + 80) * _ease_out(k)
            if k >= 1:
                self._set_phase('board')
        elif self.phase == 'walk':
            k = _clamp01(t / self.WALK_MS)
            self.breyner_x = 300 + (rest + 70 - 300) * k
            if k >= 1:
                self._set_phase('depart')
        elif self.phase == 'depart':
            k = _clamp01(t / self.DEPART_MS)
            self.bus_x = rest + (off - rest) * _ease_in(k)
            if k >= 1:
                self._set_phase('border')

    @staticmethod
    def _build_family():
        """Siluetas pre-renderizadas una sola vez (no se asigna memoria por frame)."""
        s = pygame.Surface((190, 140), pygame.SRCALPHA)
        col = (8, 6, 14, 255)
        for cx, h in ((40, 130), (100, 120), (150, 90)):
            r = 11 if h > 100 else 9
            pygame.draw.circle(s, col, (cx, 140 - h + r), r)
            pygame.draw.rect(s, col, (cx - 14, 140 - h + r * 2, 28, h - r * 2), border_radius=8)
        return s

    def _draw_bus(self, surf):
        x = int(self.bus_x)
        rect(surf, x, 395, self.BUS_W, 80, (151, 56, 65), outline=True)
        rect(surf, x, 440, self.BUS_W, 8, (110, 38, 48))
        for i in range(4):
            rect(surf, x + 12 + i * 48, 408, 38, 28, (119, 174, 204), outline=True)
        rect(surf, x + self.BUS_W - 6, 452, 6, 10, (255, 214, 140))   # faro
        for wx in (x + 48, x + self.BUS_W - 48):
            circle(surf, wx, 478, 14, (25, 23, 32), outline=True)

    def draw(self, surf, now):
        bg = _load_image('assets/backgrounds/parada_bus.png')
        if bg:
            surf.blit(bg, (0, 0))
        else:
            gradient_rect(surf, 0, 0, W, H, (66, 91, 143), (255, 145, 103))
            tile_ground(surf, 0, 480, W, H - 480, (92, 88, 99), (65, 61, 77), tile_size=30)

        # La familia se desvanece lentamente mientras el bus se va.
        fam_a = 1.0
        if self.phase == 'depart':
            fam_a = 1 - _clamp01((now - self.phase_t0) / self.DEPART_MS)
        elif self.phase == 'border':
            fam_a = 0.0
        if fam_a > 0:
            _blit_alpha(surf, self.family, fam_a * 0.9, (100, self.GROUND_Y - 150))

        if self.phase != 'wait':
            self._draw_bus(surf)

        if self.phase in ('wait', 'arrive', 'board'):
            draw_character_static(surf, 300, self.GROUND_Y, 1.7, PALETTE_BREYNER,
                                  'left' if self.phase == 'wait' else 'right', now * 0.003)
        elif self.phase == 'walk':
            draw_walk_character(surf, self.breyner_x, self.GROUND_Y, 1.7, PALETTE_BREYNER,
                                'right', (now // 120) % 8, True, now // 16)

    def exit(self):
        ui.hint_text = ''


# ───────── 3) FOTO FINAL ─────────
class FinalPhoto(Epilogue):
    """Fotograma final → 4 frases en cuadros de texto → fundido lento a negro
    con sollozos y música → fin (el manager lanza los créditos)."""
    PHOTO_FADE_IN = 4000
    FADE_OUT = 10000
    BLACK_HOLD = 1500

    def enter(self, now):
        super().enter(now)
        self.phase = 'photo_in'      # photo_in → dialogue → fade_out
        self.phase_t0 = now
        self.photo = _load_image('assets/epilogue_cristel_photo.jpg')
        self.black = pygame.Surface((W, H))
        self.black.fill((0, 0, 0))
        audio.start_ambient(110)
        ui.clear_hotspots()
        ui.hint_text = ' '

    def _set_phase(self, phase):
        self.phase = phase
        self.phase_t0 = pygame.time.get_ticks()

    def _start_dialogue(self):
        lines = [{'speaker': FINAL_SPEAKER, 'text': config.tr(es, en)}
                 for es, en in FINAL_PHRASES]
        ui.queue_dialogue(lines, self._start_fade_out)

    def _start_fade_out(self):
        self._set_phase('fade_out')
        _play_sobs()
        if not _play_music():                 # sin archivo: melodía sintetizada
            for freq, delay in MELODY:
                audio.schedule_tone(freq, 2.0, 'sine', 0.10, delay)

    def update(self, now):
        t = now - self.phase_t0
        if self.phase == 'photo_in' and t >= self.PHOTO_FADE_IN:
            self._set_phase('dialogue')
            self._start_dialogue()
        elif self.phase == 'fade_out' and t >= self.FADE_OUT + self.BLACK_HOLD:
            self.done = True

    def draw(self, surf, now):
        t = now - self.phase_t0
        surf.fill((0, 0, 0))
        photo_a = _clamp01(t / self.PHOTO_FADE_IN) if self.phase == 'photo_in' else 1.0
        if self.photo:
            _blit_alpha(surf, self.photo, photo_a, (0, 0))
        else:   # respaldo si falta la foto
            gradient_rect(surf, 0, 0, W, H, (30, 24, 44), (8, 6, 14))
        if self.phase == 'fade_out':
            _blit_alpha(surf, self.black, t / self.FADE_OUT, (0, 0))

    # Sin handle_click: los clics los consume el cuadro de texto (ui.handle_click).
    # Sin audio.stop_ambient() en exit(): el sonido sigue bajo los créditos.


# ───────── GESTOR ─────────
class EpilogueManager:
    """Encadena pantallas con fundido. Ninguna conoce a las demás."""

    def __init__(self, factories):
        self._factories = factories
        self._screens = []
        self._index = -1
        self._on_finish = None
        self._transitioning = False

    @property
    def current(self):
        return self._screens[self._index] if 0 <= self._index < len(self._screens) else None

    def start(self, on_finish):
        self._screens = [f() for f in self._factories]
        self._on_finish = on_finish
        self._transitioning = False
        self._enter(0)

    def _enter(self, i):
        self._index = i
        self._screens[i].enter(pygame.time.get_ticks())

    def _advance(self):
        if self._transitioning:
            return
        self._transitioning = True

        def swap():
            cur = self.current
            if cur:
                cur.exit()
            nxt = self._index + 1
            if nxt >= len(self._screens):
                self._index = -1
                self._transitioning = False
                cb, self._on_finish = self._on_finish, None
                if cb:
                    cb()          # créditos
                ui.fade_in()
                return
            self._enter(nxt)
            self._transitioning = False
            ui.fade_in()
        ui.fade_out(swap)

    def draw(self, surf):
        cur = self.current
        if cur is None:
            surf.fill((0, 0, 0))
            return
        now = pygame.time.get_ticks()
        cur.update(now)
        cur.draw(surf, now)
        if cur.done:
            self._advance()

    def handle_click(self, pos):
        cur = self.current
        return bool(cur and not self._transitioning and cur.handle_click(pos))


manager = EpilogueManager([ReflectionScreen, BusFarewell, FinalPhoto])
