"""
Configuración global editable desde el menú principal:
nombres de los personajes, idioma, volumen y esquema de control.
Todo tiene un valor por defecto para quien no quiera cambiar nada.
"""

character_names = {'breyner': 'Breyner', 'cristel': 'Cristel'}
language = 'es'                # 'es' | 'en'
volume = 1.0                   # 0.0 - 1.0
control_scheme = 'keyboard'    # 'keyboard' | 'dpad' | 'touchpad'

DEFAULT_B = 'Breyner'
DEFAULT_C = 'Cristel'


def name_b():
    return character_names['breyner'] or DEFAULT_B


def name_c():
    return character_names['cristel'] or DEFAULT_C


def set_name_b(name):
    name = name.strip()
    character_names['breyner'] = name if name else DEFAULT_B


def set_name_c(name):
    name = name.strip()
    character_names['cristel'] = name if name else DEFAULT_C


def set_language(lang):
    global language
    language = lang


def set_volume(v):
    global volume
    volume = max(0.0, min(1.0, round(v, 2)))


def set_control_scheme(scheme):
    global control_scheme
    control_scheme = scheme


def tr(es, en):
    """
    Devuelve el texto en el idioma activo, sustituyendo {b} y {c}
    por los nombres configurados de los personajes.
    """
    text = es if language == 'es' else en
    try:
        return text.format(b=name_b(), c=name_c())
    except (KeyError, IndexError):
        return text
