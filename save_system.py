"""
Guardado simple en JSON, compatible con PC y con navegador (pygbag).

- En PC: archivo savegame.json junto al juego.
- En navegador (sys.platform == 'emscripten'): localStorage del navegador,
  porque el sistema de archivos virtual de pygbag no persiste al cerrar la pestaña.

Se guarda cada vez que Breyner entra al cuarto (entre escenas).
Interfaz pública sin cambios: save_game, has_save, load_game, delete_save.
"""
import json
import os
import sys

import config
from engine import ui

IS_WEB = sys.platform == 'emscripten'
SAVE_KEY = 'olvido_savegame_v1'
SAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'savegame.json')


def _storage():
    """localStorage del navegador, o None si no está disponible."""
    try:
        from platform import window   # solo existe dentro de pygbag
        return window.localStorage
    except Exception:
        return None


def _web_read():
    store = _storage()
    if store is None:
        return None
    try:
        value = store.getItem(SAVE_KEY)
    except Exception:
        return None
    if value is None:
        return None
    text = str(value)
    return None if text in ('', 'null', 'None', 'undefined') else text


def _build_data(resume_index):
    return {
        'resume_index': resume_index,
        'memories_found': ui.memories_found,
        'fragments': list(ui.fragments),
        'polaroid_scenes': [p['scene'] for p in ui.polaroids],
        'inventory': list(ui.inventory),
        'names': dict(config.character_names),
        'language': config.language,
        'volume': config.volume,
        'control_scheme': config.control_scheme,
    }


def save_game(resume_index):
    """resume_index: índice de escena (de SCENES) al que se vuelve al continuar."""
    text = json.dumps(_build_data(resume_index), ensure_ascii=False)
    try:
        if IS_WEB:
            store = _storage()
            if store is None:
                return False
            store.setItem(SAVE_KEY, text)
            return True
        with open(SAVE_PATH, 'w', encoding='utf-8') as f:
            f.write(text)
        return True
    except Exception:
        return False


def has_save():
    if IS_WEB:
        return _web_read() is not None
    return os.path.isfile(SAVE_PATH)


def load_game():
    try:
        if IS_WEB:
            text = _web_read()
            return json.loads(text) if text else None
        with open(SAVE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def delete_save():
    try:
        if IS_WEB:
            store = _storage()
            if store is not None:
                store.removeItem(SAVE_KEY)
        elif os.path.isfile(SAVE_PATH):
            os.remove(SAVE_PATH)
    except Exception:
        pass
