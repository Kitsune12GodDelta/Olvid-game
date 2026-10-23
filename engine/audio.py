"""
Motor de audio sintetizado, puerto del Web Audio API original.
No usa numpy (por compatibilidad con pygbag/WASM) — genera PCM puro con math+array.
"""
import math
import array
import pygame
import config

SAMPLE_RATE = 22050   # menor costo de síntesis en navegador (WASM)
sound_on = True


def _play(snd, **kwargs):
    """Reproduce un Sound aplicando el volumen global de config (sin regenerar PCM)."""
    try:
        snd.set_volume(config.volume)
    except Exception:
        pass
    return snd.play(**kwargs)

_tone_cache = {}
_scheduled = []       # [(trigger_ms, Sound), ...]
_ambient_channels = []


def init_mixer():
    try:
        pygame.mixer.pre_init(SAMPLE_RATE, -16, 2, 512)
    except Exception:
        pass


def _rate():
    """Frecuencia real del mezclador (en navegador puede diferir de la pedida)."""
    info = pygame.mixer.get_init()
    return info[0] if info else SAMPLE_RATE


def _wave(wave, phase):
    if wave == 'sine':
        return math.sin(2 * math.pi * phase)
    if wave == 'square':
        return 1.0 if phase < 0.5 else -1.0
    if wave == 'triangle':
        return 4 * abs(phase - 0.5) - 1
    if wave == 'sawtooth':
        return 2 * phase - 1
    return math.sin(2 * math.pi * phase)


def _make_tone(freq, duration, wave='sine', volume=0.3, attack=0.05):
    sr = _rate()
    n = max(1, int(sr * duration))
    buf = array.array('h', bytes(0))
    buf.extend([0] * (n * 2))
    amp = 32767.0 * volume
    for i in range(n):
        t = i / sr
        phase = (t * freq) % 1.0
        v = _wave(wave, phase)
        if t < attack and attack > 0:
            env = t / attack
        else:
            rem = duration - attack
            env = max(0.0, 1 - (t - attack) / rem) if rem > 0 else 1.0
        s = int(max(-32767, min(32767, amp * v * env)))
        buf[2 * i] = s
        buf[2 * i + 1] = s
    return pygame.mixer.Sound(buffer=buf.tobytes())


def _make_tone_loop(freq, duration, wave='sine', volume=0.1):
    """Tono de amplitud constante, pensado para loop continuo (ambiente)."""
    sr = _rate()
    n = max(1, int(sr * duration))
    buf = array.array('h', bytes(0))
    buf.extend([0] * (n * 2))
    amp = 32767.0 * volume
    for i in range(n):
        phase = (i / sr * freq) % 1.0
        v = _wave(wave, phase)
        s = int(max(-32767, min(32767, amp * v)))
        buf[2 * i] = s
        buf[2 * i + 1] = s
    return pygame.mixer.Sound(buffer=buf.tobytes())


def get_tone(freq, duration, wave='sine', volume=0.3):
    key = (round(freq, 2), round(duration, 3), wave, round(volume, 3))
    snd = _tone_cache.get(key)
    if snd is None:
        snd = _make_tone(freq, duration, wave, volume)
        _tone_cache[key] = snd
    return snd


def schedule_tone(freq, duration, wave, volume, delay_s):
    trigger = pygame.time.get_ticks() + int(delay_s * 1000)
    _scheduled.append((trigger, get_tone(freq, duration, wave, volume)))


def update_audio():
    """Llamar una vez por frame desde el loop principal."""
    if not _scheduled:
        return
    now = pygame.time.get_ticks()
    remaining = []
    for trigger, snd in _scheduled:
        if now >= trigger:
            if sound_on:
                try:
                    _play(snd)
                except Exception:
                    pass
        else:
            remaining.append((trigger, snd))
    _scheduled[:] = remaining


# ── EFECTOS ──
def play_click():
    if sound_on:
        _play(get_tone(880, 0.08, 'sine', 0.14))


def play_unlock():
    schedule_tone(523, 0.2, 'sine', 0.16, 0)
    schedule_tone(659, 0.2, 'sine', 0.16, 0.1)
    schedule_tone(784, 0.35, 'sine', 0.18, 0.2)


def play_pickup():
    schedule_tone(660, 0.1, 'triangle', 0.16, 0)
    schedule_tone(880, 0.15, 'triangle', 0.16, 0.08)


def play_page_turn():
    if sound_on:
        _play(get_tone(220, 0.12, 'square', 0.05))


def play_match():
    schedule_tone(587, 0.15, 'sine', 0.16, 0)
    schedule_tone(880, 0.25, 'sine', 0.18, 0.1)


def play_mismatch():
    if sound_on:
        _play(get_tone(180, 0.18, 'sawtooth', 0.1))


# ── AMBIENTE (pad continuo de 3 armónicos, por escena) ──
def start_ambient(base_freq):
    stop_ambient()
    if not sound_on:
        return
    harmonics = [(base_freq, 0.05), (base_freq * 1.5, 0.032), (base_freq * 2, 0.022)]
    for freq, vol in harmonics:
        cycles = max(1, round(freq * 1.2))
        dur = cycles / freq
        snd = _make_tone_loop(freq, dur, 'sine', vol)
        ch = _play(snd, loops=-1, fade_ms=1200)
        _ambient_channels.append(ch)


def stop_ambient():
    for ch in _ambient_channels:
        try:
            if ch:
                ch.fadeout(500)
        except Exception:
            pass
    _ambient_channels.clear()


def toggle_sound():
    global sound_on
    sound_on = not sound_on
    if not sound_on:
        stop_ambient()
    return sound_on
