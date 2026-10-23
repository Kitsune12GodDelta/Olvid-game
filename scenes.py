"""
Las 8 escenas de Olvido: intro, seis recuerdos reales, final.
Puerto fiel de los diálogos, hotspots, zonas de recolección, elecciones
y arte de fondo del HTML original (olvido-v3-final.html).
"""
import math
import os
import pygame
import config
import room
import commute
import minigames
import save_system
import epilogue
from engine import ui, movement, audio
from engine import drawing as _drawing
from engine.drawing import (rect, circle, gradient_rect, radial_glow, tile_ground,
                             draw_character_static, draw_walk_character,
                             draw_walk_character_expression)
from engine.constants import W, H, PALETTE_BREYNER, PALETTE_CRISTEL, font

anim_frame = 0
current_scene_index = 0
active_draw_fn = None
_scene1_background = None


def cristel_expression():
    if ui.memories_found >= 5:
        return 'warm'
    if ui.memories_found >= 2:
        return 'curious'
    return 'confused'


def _player_near(target_x, threshold):
    return not (movement.movement_enabled and abs(movement.player.x - target_x) > threshold)


def cristel_facing(cristel_x):
    """Cristel gira hacia donde esté Breyner en cada momento, no se queda fija."""
    return 'left' if movement.player.x < cristel_x else 'right'


def memory_unlocked(n):
    ui.memories_found = n

    def _go():
        goto_room(n + 1)
    ui.call_later(400, lambda: ui.fade_out(_go))


def goto_scene(index):
    global current_scene_index
    current_scene_index = index
    ui.fade_in()
    SCENES[index]['setup']()


COMMUTE_BEFORE = {2, 3, 6}  # escenas que ocurren en casa de Cristel: bus + caminata antes


def goto_room(next_index):
    """Pasa por el cuarto de Breyner antes de la siguiente escena (autoguarda al entrar)."""
    global current_scene_index, active_draw_fn

    def proceed():
        if next_index in COMMUTE_BEFORE:
            goto_commute(next_index)
        else:
            goto_scene(next_index)

    current_scene_index = 'room'
    ui.fade_in()
    room.setup(next_index, proceed)
    active_draw_fn = room.draw


def goto_commute(target_index):
    """Bus + caminata hasta la casa de Cristel, antes de las escenas 2, 3 y 6."""
    global current_scene_index, active_draw_fn
    current_scene_index = 'commute'
    ui.fade_in()
    commute.setup(lambda: goto_scene(target_index))
    active_draw_fn = commute.draw


# ─────────────────────────────────────────────
# INTRO
# ─────────────────────────────────────────────
def intro_setup():
    global active_draw_fn
    ui.clear_hotspots()
    movement.disable_movement()
    active_draw_fn = draw_intro
    audio.start_ambient(220)
    ui.queue_dialogue([
        {'speaker': '', 'text': config.tr('Ibarra, Ecuador. Una mañana cualquiera, camino a la escuela.', "Ibarra, Ecuador. An ordinary morning, on the way to school.")},
        {'speaker': config.name_b(), 'text': config.tr('{c} iba caminando a mi lado, como siempre. Pero algo no estaba bien.', "{c} was walking beside me, like always. But something wasn't right.")},
        {'speaker': config.name_c(), 'text': config.tr('Disculpa... ¿te conozco? Perdón, es que... no recuerdo tu nombre.', "Excuse me... do I know you? I'm sorry, it's just... I don't remember your name.")},
        {'speaker': config.name_b(), 'text': config.tr('Soy {b}. ¿{c}? ¿Estás bien?', "I'm {b}. {c}? Are you okay?")},
        {'speaker': config.name_c(), 'text': config.tr('Sí, perdón. Es raro. Recuerdo todo lo demás... la escuela, mis amigas, mi familia. Pero tú... no sé quién eres.', "Yes, sorry. It's strange. I remember everything else... school, my friends, my family. But you... I don't know who you are.")},
        {'speaker': config.name_b(), 'text': config.tr('Algo se había roto. No sabía qué, pero sabía que tenía que recordarle quién era yo para ella. Recorrería cada lugar que vivimos juntos.', "Something had broken. I didn't know what, but I knew I had to remind her who I was to her. I'd go back to every place we had lived through together.")},
    ], lambda: goto_room(1))


def draw_intro(surf):
    gradient_rect(surf, 0, 0, W, H, (143, 184, 216), (232, 212, 192))
    circle(surf, 820, 100, 50, (255, 244, 216))
    rect(surf, 0, 420, W, H - 420, (90, 84, 98))
    rect(surf, 0, 415, W, 8, (68, 64, 80))
    for i in range(0, W, 60):
        rect(surf, i, 460, 30, 4, (122, 116, 136))
    draw_character_static(surf, 380, 470, 1.5, PALETTE_BREYNER, 'right', anim_frame * 0.1)
    draw_character_static(surf, 460, 470, 1.4, PALETTE_CRISTEL, 'right', anim_frame * 0.1 + 1, 'confused')


# ─────────────────────────────────────────────
# ESCENA 1 — Detrás del curso
# ─────────────────────────────────────────────
def scene1_setup():
    global active_draw_fn
    ui.clear_hotspots()
    active_draw_fn = draw_scene1
    audio.start_ambient(196)

    def after_card():
        movement.enable_movement(300, 540, {'minX': 90, 'maxX': 760, 'groundY': 540})
        ui.hint_text = config.tr('\u2190 \u2192 / A D para moverte \u00b7 camina hacia los objetos', '\u2190 \u2192 / A D to move \u00b7 walk up to objects')

        def pines():
            ui.queue_dialogue([{'speaker': config.name_b(), 'text': config.tr('Los árboles de pino, con sus ramas secas. Siempre estaban ahí, como testigos.', "The pine trees, with their dry branches. They were always there, like witnesses.")}],
                               lambda: ui.collect_fragment(1))
        ui.add_hotspot(120, 380, 130, 160, config.tr('Los pinos secos', 'The dry pines'), pines)

        def ventanal():
            ui.queue_dialogue([{'speaker': config.name_b(), 'text': config.tr('Detrás de nosotros estaba el curso, con ese ventanal grande. Adentro, la clase seguía como si nada.', "Behind us was the classroom, with that big window. Inside, class went on like nothing was happening.")}])
        ui.add_hotspot(640, 280, 220, 140, config.tr('El ventanal del curso', 'The classroom window'), ventanal)

        def escalera():
            ui.queue_dialogue([{'speaker': config.name_b(), 'text': config.tr('A la derecha, la escalera de piedra que llevaba a los patios de atrás. Por ahí nos habíamos escapado un momento.', "To the right, the stone stairs that led to the back courtyards. We had snuck off that way for a moment, once.")}])
        ui.add_hotspot(780, 320, 60, 220, config.tr('La escalera de piedra', 'The stone stairs'), escalera)

        def cristel_talk():
            if not _player_near(450, 90):
                ui.queue_dialogue([{'speaker': '', 'text': config.tr('(Acércate más a {c} para hablar con ella.)', "(Get closer to {c} to talk to her.)")}])
                return

            def after_setup_dialogue():
                def on_choice(choice):
                    if choice == 'calm':
                        resp = {'speaker': config.name_b(), 'text': config.tr('Le dije que no se preocupara, que fuéramos lento. Ella sonrió, aliviada.', "I told her not to worry, that we'd take it slow. She smiled, relieved.")}
                    else:
                        resp = {'speaker': config.name_b(), 'text': config.tr('Le dije la verdad: no sabía bien cómo me sentía, pero quería intentarlo con ella.', "I told her the truth: I wasn't sure how I felt, but I wanted to try with her.")}

                    def finish():
                        ui.capture_polaroid(1, draw_polaroid_scene1)
                        movement.disable_movement()
                        memory_unlocked(1)
                    ui.queue_dialogue([
                        resp,
                        {'speaker': config.name_b(), 'text': config.tr('La abracé, y le di un beso en la frente. Desde ese día empecé a esperarla en la tarde para acompañarla a su casa.', "I hugged her, and kissed her forehead. From that day on I started waiting for her in the afternoons to walk her home.")},
                        {'speaker': '', 'text': config.tr('\u2726 El primer hilo entre los dos. \u2726', "\u2726 The first thread between the two of us. \u2726")},
                    ], finish)
                ui.show_choice(config.tr('{c} espera tu respuesta', "{c} is waiting for your answer"), [
                    ('calm', config.tr('"No te preocupes. Vayamos lento."', '"Don\'t worry. Let\'s take it slow."')),
                    ('honest', config.tr('"No sé bien cómo me siento todavía, pero quiero intentarlo."',
                                          '"I\'m not totally sure how I feel yet, but I want to try."')),
                ], on_choice)
            ui.queue_dialogue([
                {'speaker': config.name_c(), 'text': config.tr('Una amiga me dijo que te gustaba... y quería hablar conmigo de eso.', "A friend told me you liked me... and she wanted to talk to me about it.")},
                {'speaker': config.name_b(), 'text': config.tr('Nos vinimos para acá, atrás del curso. Tú estabas nerviosa.', "We came back here, behind the classroom. You were nervous.")},
                {'speaker': config.name_c(), 'text': config.tr('Empecé a sentir algo por ti. Pero no quería arruinar nuestra amistad...', "I started feeling something for you. But I didn't want to ruin our friendship...")},
            ], after_setup_dialogue)
        ui.add_hotspot(380, 360, 140, 200, config.name_c(), cristel_talk)
        ui.render_progress(0, 6)

    ui.show_scene_card(config.tr('Recuerdo I', 'Memory I'), config.tr('Detrás del curso', 'Behind the classroom'),
                        config.tr('Donde una amiga le contó a {c} que {b} sentía algo por ella.',
                                  'Where a friend told {c} that {b} had feelings for her.'), after_card)


def draw_scene1(surf):
    """Dibuja el fondo artístico del colegio y conserva los sprites jugables.

    El fondo es una imagen independiente; los personajes, diálogos, controles y
    hotspots siguen siendo dibujados por el código original.
    """
    global _scene1_background
    if _scene1_background is None:
        bg_path = os.path.join(os.path.dirname(__file__), 'assets', 'backgrounds', 'escuela_atardecer.png')
        try:
            _scene1_background = pygame.image.load(bg_path).convert()
            _scene1_background = pygame.transform.scale(_scene1_background, (W, H))
        except (pygame.error, OSError):
            _scene1_background = False
    if _scene1_background:
        _drawing.set_pixelate(False)
        surf.blit(_scene1_background, (0, 0))
    else:
        # Respaldo simple si el recurso no se encuentra.
        gradient_rect(surf, 0, 0, W, 350, (69, 103, 157), (255, 174, 119))
        rect(surf, 0, 390, W, 210, (76, 76, 91))

    # Mantener el mismo sistema de personajes y posiciones de la escena original.
    draw_walk_character(surf, movement.player.x, movement.player.y, movement.player.scale,
                         PALETTE_BREYNER, movement.player.facing, movement.player.walk_frame,
                         movement.player.moving, anim_frame)
    draw_walk_character_expression(surf, 490, 540, 1.5, PALETTE_CRISTEL, cristel_facing(490), 0, False,
                                    cristel_expression(), anim_frame)


def draw_polaroid_scene1(surf, w, h):
    surf.fill((168, 196, 216))
    rect(surf, 0, h * 0.6, w, h * 0.4, (106, 122, 90))
    circle(surf, w * 0.2, h * 0.5, 14, (52, 82, 52))
    rect(surf, w * 0.45, h * 0.4, 8, 18, (58, 90, 122))
    rect(surf, w * 0.55, h * 0.42, 7, 16, (176, 106, 128))


# ─────────────────────────────────────────────
# ESCENA 2 — El portón negro
# ─────────────────────────────────────────────
def scene2_setup():
    global active_draw_fn
    ui.clear_hotspots()
    active_draw_fn = draw_scene2
    audio.start_ambient(174)

    def after_card():
        movement.enable_movement(300, 540, {'minX': 90, 'maxX': 700, 'groundY': 540})
        ui.hint_text = config.tr('\u2190 \u2192 / A D para moverte \u00b7 camina hacia los objetos', '\u2190 \u2192 / A D to move \u00b7 walk up to objects')

        def hoja():
            ui.queue_dialogue([{'speaker': config.name_b(), 'text': config.tr('Una hojita seca, de las que caían esa tarde. La guardo igual, sin razón aparente.', "A little dry leaf, one of the ones falling that afternoon. I still keep it, for no real reason.")}],
                               lambda: ui.collect_fragment(2))
        movement.add_pickup_zone(735, 540, 55, 'hoja-porton', '\U0001F342', config.tr('Una hojita seca', 'A little dry leaf'), hoja, ui.has_item('hoja-porton'))

        def porton():
            ui.queue_dialogue([{'speaker': config.name_b(), 'text': config.tr('El portón negro de su casa. Ahí nos quedamos parados, sin querer despedirnos todavía.', "The black gate at her house. We stood there, not wanting to say goodbye yet.")}])
        ui.add_hotspot(560, 200, 160, 320, config.tr('El portón negro', 'The black gate'), porton)

        def pareja():
            if not _player_near(460, 90):
                ui.queue_dialogue([{'speaker': '', 'text': config.tr('(Acércate al portón, junto a {c}.)', "(Go to the gate, next to {c}.)")}])
                return

            def finish():
                ui.add_inventory_item('foto-porton', '\U0001F5BC\uFE0F', config.tr('El recuerdo del portón', 'The memory of the gate'))
                ui.capture_polaroid(2, draw_polaroid_scene2)
                movement.disable_movement()
                memory_unlocked(2)

            def after_minigame():
                ui.queue_dialogue([
                    {'speaker': config.name_b(), 'text': config.tr('La besé. Forcejeó un poco, torpe, corto. Pero al final se rindió y me correspondió.', "I kissed her. She pulled back a little, clumsy, brief. But in the end she gave in and kissed me back.")},
                    {'speaker': config.name_b(), 'text': config.tr('La volví a besar. Esta vez duró más. Ese día la besé tres veces.', "I kissed her again. This time it lasted longer. I kissed her three times that day.")},
                    {'speaker': config.name_b(), 'text': config.tr('Desde ahí, ya le decía \"amor\". Fue el primer beso de los dos — el mío de ella, y el de ella, mío.', "From then on, I was already calling her \"love\". It was the first kiss for both of us — hers from me, and mine from her.")},
                    {'speaker': '', 'text': config.tr('\u2726 1.71m y 1.47m, abrazados frente a un portón negro. \u2726', "\u2726 1.71m and 1.47m, hugging in front of a black gate. \u2726")},
                ], finish)

            def start_minigame():
                minigames.start_heartbeat(after_minigame)

            ui.queue_dialogue([
                {'speaker': config.name_b(), 'text': config.tr('Aunque todavía no éramos pareja, ya actuábamos como una. Le dije lo mucho que la amaba.', "Even though we weren't a couple yet, we already acted like one. I told her how much I loved her.")},
                {'speaker': config.name_b(), 'text': config.tr('Le agradecí por hacer de mi vida escolar algo mucho mejor con solo su presencia.', "I thanked her for making my school life so much better just by being in it.")},
                {'speaker': config.name_c(), 'text': config.tr('¿...qué?', "...what?")},
                {'speaker': config.name_b(), 'text': config.tr('Estábamos abrazados. La miré, y miré sus labios.', "We were hugging. I looked at her, and looked at her lips.")},
            ], start_minigame)
        ui.add_hotspot(380, 340, 160, 220, config.tr('{b} y {c}', '{b} and {c}'), pareja)
        ui.render_progress(1, 6)

    ui.show_scene_card(config.tr('Recuerdo II', 'Memory II'), config.tr('El portón negro', 'The black gate'),
                        config.tr('Último día de Primero de Bachillerato. La acompañó a casa, y todo cambió.',
                                  'Last day of the first year of high school. He walked her home, and everything changed.'),
                        after_card)


def draw_scene2(surf):
    """Escena del portón negro: fondo nocturno detallado, con sprites y objetos aparte."""
    # Cielo azul de noche con un halo cálido cerca de la entrada.
    gradient_rect(surf, 0, 0, W, 390, (17, 27, 55), (58, 55, 78))
    radial_glow(surf, 635, 250, 190, (255, 177, 91), max_alpha=42)

    # Siluetas de árboles y follaje en capas.
    for x, top, width, height in [(45, 45, 115, 205), (145, 80, 105, 170),
                                  (790, 30, 130, 220), (865, 90, 90, 155)]:
        rect(surf, x + width // 2 - 8, top + 45, 16, height, (48, 39, 39))
        for dx, dy, r, col in [(-20, 10, 34, (25, 48, 43)), (15, -8, 39, (30, 58, 48)),
                               (38, 22, 31, (36, 65, 50)), (-2, 34, 36, (27, 53, 45))]:
            circle(surf, x + width // 2 + dx, top + dy + 38, r, col)
        # pequeñas motas de luz pixeladas en las hojas
        for j in range(7):
            px = x + (j * 19) % max(1, width)
            py = top + 20 + (j * 23) % max(1, height // 2)
            rect(surf, px, py, 5, 4, (64, 83, 55))

    # Fachada y ventanas cálidas de la casa.
    rect(surf, 0, 215, W, 270, (69, 62, 67))
    rect(surf, 0, 215, W, 12, (103, 91, 88))
    rect(surf, 30, 250, 235, 205, (92, 76, 70))
    rect(surf, 40, 260, 215, 185, (56, 51, 57))
    for wx in (58, 142, 202):
        rect(surf, wx, 278, 42, 82, (36, 42, 59))
        rect(surf, wx + 4, 282, 34, 72, (238, 157, 79) if wx == 142 else (83, 105, 125))
        rect(surf, wx + 17, 282, 4, 72, (47, 45, 52))
        rect(surf, wx, 314, 42, 4, (47, 45, 52))

    # Muro de piedra y pilares que enmarcan el portón.
    rect(surf, 0, 390, W, 98, (91, 81, 82))
    for x in range(0, W, 48):
        rect(surf, x, 395, 44, 24, (113, 100, 94))
        rect(surf, x + 10, 426, 36, 24, (76, 72, 79))
        rect(surf, x + 2, 454, 42, 25, (104, 91, 87))
    # Portón de hierro negro con barrotes y remates.
    rect(surf, 300, 275, 340, 213, (20, 22, 31))
    rect(surf, 308, 284, 324, 195, (31, 35, 45))
    rect(surf, 300, 270, 340, 10, (37, 39, 49))
    for gx in range(310, 636, 27):
        rect(surf, gx, 282, 5, 197, (10, 13, 22))
        circle(surf, gx + 2, 286, 4, (120, 91, 63))
    for gy in (340, 410, 475):
        rect(surf, 306, gy, 328, 4, (12, 15, 23))
    # Pilares de piedra con textura discreta.
    for px in (278, 632):
        rect(surf, px, 258, 28, 232, (143, 124, 111))
        rect(surf, px - 7, 250, 42, 15, (174, 149, 127))
        rect(surf, px + 5, 275, 5, 190, (161, 139, 121))
        for yy in range(295, 465, 38):
            rect(surf, px, yy, 28, 3, (104, 94, 93))
    # Farol encendido y resplandor en el pilar derecho.
    radial_glow(surf, 676, 315, 95, (255, 180, 91), max_alpha=55)
    rect(surf, 668, 300, 7, 50, (28, 31, 40))
    rect(surf, 655, 294, 33, 8, (24, 27, 35))
    rect(surf, 660, 276, 23, 20, (36, 37, 43))
    rect(surf, 664, 280, 15, 12, (255, 199, 104))
    rect(surf, 668, 282, 7, 8, (255, 232, 163))

    # Suelo adoquinado con bordillo, hojas y sombras.
    tile_ground(surf, 0, 488, W, H - 488, (77, 70, 73), (61, 58, 67), tile_size=28)
    rect(surf, 0, 484, W, 7, (42, 43, 55))
    for lx, ly in [(90, 535), (190, 565), (730, 520), (820, 575), (248, 590)]:
        rect(surf, lx, ly, 7, 3, (166, 105, 62))
        rect(surf, lx + 4, ly + 3, 5, 2, (118, 78, 55))

    # Mantener los sprites, las zonas interactivas y los efectos originales.
    draw_walk_character(surf, movement.player.x, movement.player.y, movement.player.scale,
                         PALETTE_BREYNER, movement.player.facing, movement.player.walk_frame,
                         movement.player.moving, anim_frame)
    draw_walk_character_expression(surf, 465, 548, 1.42, PALETTE_CRISTEL, cristel_facing(465),
                                    movement.player.walk_frame, False, cristel_expression(), anim_frame)
    movement.draw_pickup_zones(surf, anim_frame, {'circle': circle, 'font': font('icon')})

    for i in range(3):
        t = (anim_frame * 0.5 + i * 40) % 120
        alpha = max(0, int(255 * (1 - t / 120)))
        label = font('small').render('♥', True, (232, 163, 176))
        label.set_alpha(alpha)
        surf.blit(label, (450 + i * 15, 470 - t))


def draw_polaroid_scene2(surf, w, h):
    surf.fill((232, 168, 120))
    rect(surf, 0, h * 0.65, w, h * 0.35, (106, 98, 88))
    rect(surf, w * 0.55, h * 0.15, w * 0.25, h * 0.6, (24, 24, 28))
    rect(surf, w * 0.35, h * 0.35, 8, 20, (58, 90, 122))
    rect(surf, w * 0.42, h * 0.4, 7, 17, (176, 106, 128))


# ─────────────────────────────────────────────
# ESCENA 3 — El celular olvidado (minijuego de cartas)
# ─────────────────────────────────────────────
def scene3_setup():
    global active_draw_fn
    ui.clear_hotspots()
    active_draw_fn = draw_scene3
    audio.start_ambient(207)

    def after_card():
        movement.enable_movement(300, 540, {'minX': 90, 'maxX': 760, 'groundY': 540})
        ui.hint_text = config.tr('\u2190 \u2192 / A D para moverte \u00b7 camina hacia los objetos', '\u2190 \u2192 / A D to move \u00b7 walk up to objects')

        def celular():
            ui.queue_dialogue([{'speaker': config.name_b(), 'text': config.tr('{c} había olvidado su celular en el curso. No lo pensé dos veces: fui a llevárselo a su casa.', "{c} had left her phone at school. I didn't think twice: I went to bring it to her house.")}],
                               lambda: ui.add_inventory_item('celular', '\U0001F4F1', config.tr('El celular de {c}', "{c}'s phone")))
        movement.add_pickup_zone(450, 540, 55, 'celular', '\U0001F4F1', config.tr('El celular de {c}', "{c}'s phone"), celular, ui.has_item('celular'))

        def madre():
            if not ui.has_item('celular'):
                ui.queue_dialogue([{'speaker': config.tr("Madre de {c}", "{c}'s mother"), 'text': config.tr('¿Buscas a {c}? Un momento, hijo.', "Are you looking for {c}? One moment, dear.")}])
                return

            def after_minigame():
                ui.queue_dialogue([{'speaker': config.name_b(), 'text': config.tr('Mientras hablaba con su madre, sentí que cada recuerdo nuestro encajaba, como piezas que por fin tenían sentido.', "While I talked with her mother, I felt like every memory of ours fit together, like pieces that finally made sense.")}],
                                   unlock_scene3_final)

            def after_mother_dialogue():
                ui.start_memory_card_game([
                    {'text': config.tr('Los pinos', 'The pines')}, {'text': config.tr('El portón', 'The gate')},
                    {'text': config.tr('El celular', 'The phone')}, {'text': config.tr('La rosa', 'The rose')},
                ], after_minigame)
            ui.queue_dialogue([
                {'speaker': config.tr("Madre de {c}", "{c}'s mother"), 'text': config.tr('Así que tú eres {b}. Mucho gusto, hijo.', "So you're {b}. Nice to meet you, dear.")},
                {'speaker': config.name_b(), 'text': config.tr('Estaba nervioso, pero intenté actuar con responsabilidad y respeto. Quería dar una buena impresión.', "I was nervous, but I tried to act responsibly and respectfully. I wanted to make a good impression.")},
            ], after_mother_dialogue)
        ui.add_hotspot(700, 280, 150, 220, config.tr('La madre de {c}', "{c}'s mother"), madre)
        ui.render_progress(2, 6)

    ui.show_scene_card(config.tr('Recuerdo III', 'Memory III'), config.tr('El celular olvidado', 'The forgotten phone'),
                        config.tr('{c} olvidó su teléfono. {b} fue a devolvérselo y conoció a su madre.',
                                  '{c} forgot her phone. {b} went to return it and met her mother.'), after_card)


def unlock_scene3_final():
    def cristel_reclamo():
        def finish():
            ui.capture_polaroid(3, draw_polaroid_scene3)
            movement.disable_movement()
            memory_unlocked(3)
        ui.queue_dialogue([
            {'speaker': config.name_c(), 'text': config.tr('Gracias por traerlo. Pero... ¿por qué no simplemente me lo entregaste y ya? ¿Por qué no me esperaste?', "Thanks for bringing it. But... why didn't you just hand it to me and go? Why didn't you wait for me?")},
            {'speaker': config.name_b(), 'text': config.tr('Le reclamé un poco, la verdad. Quería preguntarle por qué no me esperó ella primero.', "I called her out a little, honestly. I wanted to ask why she hadn't waited for me first.")},
            {'speaker': config.name_b(), 'text': config.tr('Al final lo dejamos así. Ella me agradeció, sonriendo.', "In the end we left it at that. She thanked me, smiling.")},
            {'speaker': config.name_b(), 'text': config.tr('Pero lo que más me quedó de ese día fue otra cosa: había conocido a alguien muy importante en su vida.', "But what stayed with me most from that day was something else: I had met someone very important in her life.")},
            {'speaker': '', 'text': config.tr('\u2726 Acercarse a su mundo, un paso más. \u2726', "\u2726 One step closer to her world. \u2726")},
        ], finish)
    ui.add_hotspot(380, 360, 140, 200, config.name_c(), cristel_reclamo)
    ui.show_toast(config.tr('{c} está lista para hablar', '{c} is ready to talk'))


def draw_scene3(surf):
    gradient_rect(surf, 0, 0, W, 350, (188, 216, 232), (232, 224, 208))
    tile_ground(surf, 0, 460, W, H - 460, (158, 142, 110), (142, 126, 94), tile_size=26)
    rect(surf, 0, 454, W, 8, (122, 106, 74))
    rect(surf, 120, 100, 720, 380, (224, 212, 184))
    rect(surf, 120, 100, 720, 24, (200, 184, 144))
    rect(surf, 420, 280, 110, 200, (122, 90, 58))
    rect(surf, 440, 360, 14, 18, (58, 42, 24))
    rect(surf, 415, 275, 5, 210, (74, 58, 40))
    rect(surf, 700, 200, 160, 160, (90, 122, 138))
    rect(surf, 700, 200, 160, 16, (255, 255, 255)); rect(surf, 700, 340, 160, 16, (255, 255, 255))
    rect(surf, 692, 200, 16, 156, (255, 255, 255)); rect(surf, 852, 200, 16, 156, (255, 255, 255))
    rect(surf, 180, 420, 30, 40, (122, 90, 58))
    for i in range(5):
        rect(surf, 180 + i * 5, 390, 6, 35, (74, 122, 74))
    rect(surf, 880, 420, 30, 40, (122, 90, 58))
    for i in range(5):
        rect(surf, 880 + i * 5, 390, 6, 35, (74, 122, 74))
    rect(surf, 740, 230, 22.4, 28.8, (202, 168, 136))
    rect(surf, 728, 250, 50, 70, (122, 90, 106))
    rect(surf, 720, 248, 70, 6, (58, 40, 24))

    draw_walk_character(surf, movement.player.x, movement.player.y, movement.player.scale,
                         PALETTE_BREYNER, movement.player.facing, movement.player.walk_frame,
                         movement.player.moving, anim_frame)
    draw_walk_character_expression(surf, 460, 545, 1.5, PALETTE_CRISTEL, cristel_facing(460),
                                    movement.player.walk_frame, False, cristel_expression(), anim_frame)
    movement.draw_pickup_zones(surf, anim_frame, {'circle': circle, 'font': font('icon')})


def draw_polaroid_scene3(surf, w, h):
    surf.fill((188, 216, 232))
    rect(surf, 0, h * 0.6, w, h * 0.4, (154, 138, 106))
    rect(surf, w * 0.1, h * 0.1, w * 0.8, h * 0.55, (224, 212, 184))
    rect(surf, w * 0.6, h * 0.15, 16, 16, (202, 168, 136))
    rect(surf, w * 0.35, h * 0.4, 8, 18, (58, 90, 122))


# ─────────────────────────────────────────────
# ESCENA 4 — 22 de octubre
# ─────────────────────────────────────────────
def scene4_setup():
    global active_draw_fn
    ui.clear_hotspots()
    active_draw_fn = draw_scene4
    audio.start_ambient(185)

    def after_card():
        movement.enable_movement(300, 540, {'minX': 90, 'maxX': 760, 'groundY': 540})
        ui.hint_text = config.tr('\u2190 \u2192 / A D para moverte \u00b7 camina hacia los objetos', '\u2190 \u2192 / A D to move \u00b7 walk up to objects')

        def pensativa():
            ui.queue_dialogue([
                {'speaker': config.name_b(), 'text': config.tr('Ese día ella estaba rara. Cuando se encerraba en su mundo así, no quería hablar con nadie.', "That day she was acting strange. When she shut herself in her own world like that, she didn't want to talk to anyone.")},
                {'speaker': config.name_c(), 'text': config.tr('¿Qué somos, {b}?', "What are we, {b}?")},
                {'speaker': config.name_b(), 'text': config.tr('Algo más que amigos. Eso es obvio.', "Something more than friends. That's obvious.")},
                {'speaker': config.name_c(), 'text': config.tr('Mi familia dijo que parecer novios sin serlo no está bien... No quiero obligarte a nada.', "My family said it's not right to look like a couple without being one... I don't want to force you into anything.")},
            ])
        ui.add_hotspot(380, 340, 200, 220, config.tr('{c}, pensativa', '{c}, thoughtful'), pensativa)

        def pared():
            if not _player_near(700, 100):
                ui.queue_dialogue([{'speaker': '', 'text': config.tr('(Acércate más a la pared, junto a {c}.)', "(Get closer to the wall, next to {c}.)")}])
                return

            def manos():
                def on_choice(choice):
                    if choice == 'direct':
                        line = {'speaker': config.name_b(), 'text': config.tr('¿Quieres ser mi novia?', "Will you be my girlfriend?")}
                    else:
                        line = {'speaker': config.name_b(), 'text': config.tr('Quiero que esto sea real. ¿Y tú?', "I want this to be real. What about you?")}

                    def finish():
                        ui.add_inventory_item('fecha-22', '\U0001F4C5', config.tr('22 de octubre', 'October 22nd'))
                        ui.capture_polaroid(4, draw_polaroid_scene4)
                        movement.disable_movement()
                        memory_unlocked(4)
                    ui.queue_dialogue([
                        line,
                        {'speaker': config.name_c(), 'text': config.tr('Espera... ¿esto es porque te sientes obligado por lo que dije?', "Wait... is this because you feel obligated by what I said?")},
                        {'speaker': config.name_b(), 'text': config.tr('No. De verdad te quiero a mi lado.', "No. I really want you by my side.")},
                        {'speaker': config.name_b(), 'text': config.tr('La besé más apasionadamente esta vez, con ella contra la pared. Los dos sabíamos que ya éramos novios.', "I kissed her more passionately this time, with her against the wall. We both knew we were official now.")},
                        {'speaker': '', 'text': config.tr('\u2726 22 de octubre de 2024. El día en que todo se hizo oficial. \u2726', "\u2726 October 22nd, 2024. The day everything became official. \u2726")},
                    ], finish)
                ui.show_choice(config.tr('Este es el momento.', 'This is the moment.'), [
                    ('direct', config.tr('"¿Quieres ser mi novia?"', '"Will you be my girlfriend?"')),
                    ('soft', config.tr('"Quiero que esto sea real. ¿Y tú?"', '"I want this to be real. What about you?"')),
                ], on_choice)
            ui.queue_dialogue([{'speaker': config.name_b(), 'text': config.tr('Hice lo más lógico que pude pensar. La miré, agarré sus manos con cuidado.', "I did the most logical thing I could think of. I looked at her, took her hands carefully.")}], manos)
        ui.add_hotspot(620, 280, 160, 280, config.tr('La pared', 'The wall'), pared)
        ui.render_progress(3, 6)

    ui.show_scene_card(config.tr('Recuerdo IV', 'Memory IV'), config.tr('22 de octubre, 2024', 'October 22nd, 2024'),
                        config.tr('El día que {c} preguntó "¿qué somos?" y {b} respondió con un beso.',
                                  'The day {c} asked "what are we?" and {b} answered with a kiss.'), after_card)


def draw_scene4(surf):
    gradient_rect(surf, 0, 0, W, 400, (216, 168, 136), (240, 208, 168))
    tile_ground(surf, 0, 470, W, H - 470, (94, 88, 76), (80, 74, 62), tile_size=28)
    rect(surf, 0, 464, W, 8, (68, 64, 56))
    rect(surf, 560, 90, 280, 390, (192, 168, 136))
    rect(surf, 80, 440, 200, 40, (122, 116, 104))
    rect(surf, 820, 420, 120, 60, (106, 100, 88))
    radial_glow(surf, 700, 400, 300, (244, 208, 150), max_alpha=55)

    draw_walk_character_expression(surf, 700, 540, 1.5, PALETTE_CRISTEL, cristel_facing(700), 0, False,
                                    cristel_expression(), anim_frame)
    draw_walk_character(surf, movement.player.x, movement.player.y, movement.player.scale,
                         PALETTE_BREYNER, movement.player.facing, movement.player.walk_frame,
                         movement.player.moving, anim_frame)
    for i in range(5):
        t = (anim_frame * 0.4 + i * 60) % 200
        rect(surf, 600 + i * 40, 100 + t, 4, 4, (232, 196, 160))


def draw_polaroid_scene4(surf, w, h):
    surf.fill((216, 168, 136))
    rect(surf, 0, h * 0.7, w, h * 0.3, (90, 84, 72))
    rect(surf, w * 0.55, h * 0.1, w * 0.35, h * 0.65, (192, 168, 136))
    rect(surf, w * 0.6, h * 0.3, 7, 17, (176, 106, 128))
    rect(surf, w * 0.68, h * 0.28, 8, 19, (58, 90, 122))


# ─────────────────────────────────────────────
# ESCENA 5 — Parque Héroes del 41
# ─────────────────────────────────────────────
def scene5_setup():
    global active_draw_fn
    ui.clear_hotspots()
    active_draw_fn = draw_scene5
    audio.start_ambient(233)

    def after_card():
        movement.enable_movement(280, 478, {'minX': 90, 'maxX': 760, 'groundY': 478})
        ui.hint_text = config.tr('\u2190 \u2192 / A D para moverte \u00b7 camina hacia los objetos', '\u2190 \u2192 / A D to move \u00b7 walk up to objects')

        def marcador():
            ui.queue_dialogue([{'speaker': config.name_b(), 'text': config.tr('Un marcador, olvidado en la banca. La misma idea de siempre: dibujar algo en la piel que dure un rato, aunque se borre.', "A marker, left behind on the bench. The same idea as always: draw something on the skin that lasts a while, even if it fades.")}],
                               lambda: ui.add_inventory_item('marcador', '\U0001F58A\uFE0F', config.tr('El marcador', 'The marker')))
        movement.add_pickup_zone(600, 478, 50, 'marcador', '\U0001F58A\uFE0F', config.tr('El marcador', 'The marker'), marcador, ui.has_item('marcador'))

        def madera():
            ui.queue_dialogue([{'speaker': config.name_b(), 'text': config.tr('En la madera de la banca, alguien más había dejado un corazón parecido, mucho antes que nosotros. Quizás todos dejamos algo así en los lugares que amamos.', "On the wood of the bench, someone else had carved a similar heart, long before us. Maybe we all leave something like that in the places we love.")}],
                               lambda: ui.collect_fragment(5))
        movement.add_pickup_zone(450, 478, 45, 'madera-corazon', '\u2726', config.tr('Algo dibujado en la madera', 'Something carved in the wood'), madera, ui.has_item('madera-corazon'))

        def avion():
            ui.queue_dialogue([{'speaker': config.name_b(), 'text': config.tr('El Parque de El Avión, en Ibarra. Salimos del colegio temprano, como a las 10 u 11 de la mañana, y vinimos aquí.', "The Airplane Park, in Ibarra. We left school early, around 10 or 11 in the morning, and came here.")}])
        ui.add_hotspot(700, 200, 180, 140, config.tr('El avión del parque', "The park's airplane"), avion)

        def banca():
            ui.queue_dialogue([
                {'speaker': config.name_b(), 'text': config.tr('Nos sentamos en una banca apartada. No había mucha gente. La puse entre mis piernas, abrazándola.', "We sat on a bench off to the side. There weren't many people around. I held her between my legs, hugging her.")},
                {'speaker': config.name_b(), 'text': config.tr('Le di besitos en el cuello, en la boca, en el cachete. Solo queríamos estar así, tranquilos.', "I gave her little kisses on the neck, the mouth, the cheek. We just wanted to be like that, calm.")},
            ])
        def cristel_banca():
            if not ui.has_item('marcador'):
                ui.queue_dialogue([{'speaker': config.name_b(), 'text': config.tr('Tal vez deba buscar algo con que dibujar antes.', "Maybe I should find something to draw with first.")}])
                return

            def finish():
                ui.capture_polaroid(5, draw_polaroid_scene5)
                movement.disable_movement()
                memory_unlocked(5)

            def after_minigame():
                ui.queue_dialogue([
                    {'speaker': config.name_c(), 'text': config.tr('Toma la foto, así, con las manos agarradas.', "Take the photo, like this, with our hands together.")},
                    {'speaker': config.name_b(), 'text': config.tr('Esa foto todavía la tengo. Las manos agarradas, el corazón dibujado entre las dos.', "I still have that photo. Our hands together, the heart drawn between them.")},
                    {'speaker': '', 'text': config.tr('\u2726 Un corazón a marcador, en un parque cualquiera de un martes. \u2726', "\u2726 A marker heart, in an ordinary park on an ordinary Tuesday. \u2726")},
                ], finish)

            def start_minigame():
                minigames.start_drawing(after_minigame)

            ui.queue_dialogue([
                {'speaker': config.name_b(), 'text': config.tr('Con un marcador, nos dibujamos un corazón en las manos. Y a los costados, un \"XD\" — nuestra broma tonta.', "With a marker, we drew a heart on our hands. And on each side, an \"XD\" — our silly joke.")},
            ], start_minigame)
        # La interacción específica con Cristel debe tener prioridad sobre la banca,
        # porque ambas zonas se solapan alrededor del personaje.
        ui.add_hotspot(470, 460, 80, 60, config.tr('{c}, en la banca', '{c}, on the bench'), cristel_banca)
        ui.add_hotspot(380, 380, 220, 160, config.tr('La banca apartada', 'The secluded bench'), banca)
        ui.render_progress(4, 6)

    ui.show_scene_card(config.tr('Recuerdo V', 'Memory V'), config.tr('Parque Héroes del 41', 'Héroes del 41 Park'),
                        config.tr('Salieron temprano del colegio. Se sentaron en una banca apartada, solos.',
                                  'They left school early. They sat on a bench off to the side, alone.'), after_card)


def draw_scene5(surf):
    gradient_rect(surf, 0, 0, W, 300, (74, 150, 216), (168, 216, 236))
    for cx, cy, r in ((150, 70, 20), (180, 65, 26), (210, 75, 18), (700, 55, 20), (730, 50, 24)):
        circle(surf, cx, cy, r, (255, 255, 255))
    tile_ground(surf, 0, 400, W, H - 400, (92, 158, 76), (80, 142, 66), tile_size=24)
    rect(surf, 0, 396, W, 8, (58, 106, 48))
    rect(surf, 0, 500, W, H - 500, (184, 172, 150))
    for i in range(14):
        rect(surf, i * 72, 500, 68, H - 500, (192, 180, 156) if i % 2 == 0 else (176, 164, 140))

    for i in range(7):
        bx = 60 + i * 135
        rect(surf, bx, 460, 90, 34, (58, 106, 52))
        for k in range(4):
            fx = bx + 10 + k * 20
            circle(surf, fx, 468 + (k % 2) * 8, 4, (216, 112, 58) if k % 2 == 0 else (200, 90, 74))

    def park_tree(x, y, scale):
        rect(surf, x - 5 * scale, y, 10 * scale, 55 * scale, (90, 69, 48), outline=True)
        circle(surf, x, y - 14 * scale, 34 * scale, (74, 138, 74), outline=True)
        circle(surf, x - 20 * scale, y - 4 * scale, 24 * scale, (69, 128, 69), outline=True)
        circle(surf, x + 20 * scale, y - 4 * scale, 24 * scale, (63, 122, 63), outline=True)
        circle(surf, x, y - 30 * scale, 22 * scale, (82, 154, 82), outline=True)
    park_tree(70, 400, 1.3); park_tree(930, 390, 1.35)

    # monumento del avión
    rect(surf, 700, 330, 160, 40, (168, 164, 154))
    rect(surf, 700, 330, 160, 8, (192, 188, 176))
    rect(surf, 730, 300, 12, 32, (138, 134, 128))
    rect(surf, 818, 300, 12, 32, (138, 134, 128))
    ang = math.radians(-6.9)  # -0.12 rad del original

    def rot(px, py):
        rx = px * math.cos(ang) - py * math.sin(ang)
        ry = px * math.sin(ang) + py * math.cos(ang)
        return 778 + rx, 250 + ry

    def rot_rect(lx, ly, lw, lh, color):
        pts = [rot(lx, ly), rot(lx + lw, ly), rot(lx + lw, ly + lh), rot(lx, ly + lh)]
        pygame.draw.polygon(surf, color, pts)
    rot_rect(-95, -8, 190, 20, (200, 200, 208))
    rot_rect(70, -14, 30, 10, (176, 176, 184))
    rot_rect(-95, -4, 16, 8, (154, 154, 160))
    rot_rect(-20, -30, 14, 55, (184, 184, 192))
    rot_rect(-60, -6, 130, 6, (154, 154, 160))
    circle(surf, *rot(-95, 2), 5, (138, 42, 42))

    bx2, by2 = 380, 470
    rect(surf, bx2, by2, 190, 14, (138, 106, 58))
    rect(surf, bx2, by2 + 22, 190, 12, (122, 90, 48))
    rect(surf, bx2 + 8, by2 + 34, 10, 34, (58, 58, 58))
    rect(surf, bx2 + 172, by2 + 34, 10, 34, (58, 58, 58))
    rect(surf, bx2, by2 - 38, 190, 10, (138, 106, 58))
    rect(surf, bx2 + 8, by2 - 30, 10, 30, (58, 58, 58))
    rect(surf, bx2 + 172, by2 - 30, 10, 30, (58, 58, 58))

    s = pygame.Surface((W, H - 500), pygame.SRCALPHA)
    s.fill((0, 0, 0, 38))
    surf.blit(s, (0, 500))

    if ui.has_item('marcador'):
        alpha = int((0.8 + math.sin(anim_frame * 0.1) * 0.15) * 255)
        heart = font('body').render('\u2665', True, (192, 80, 106))
        heart.set_alpha(max(0, min(255, alpha)))
        surf.blit(heart, (W // 2 - heart.get_width() // 2, 440 + math.sin(anim_frame * 0.07) * 3))
        for dx in (-32, 32):
            xd = font('tiny').render('XD', True, (42, 58, 106))
            xd.set_alpha(max(0, min(255, alpha)))
            surf.blit(xd, (W // 2 + dx - xd.get_width() // 2, 442))

    draw_walk_character(surf, movement.player.x, movement.player.y, movement.player.scale,
                         PALETTE_BREYNER, movement.player.facing, movement.player.walk_frame,
                         movement.player.moving, anim_frame)
    draw_walk_character_expression(surf, 490, 478, 1.3, PALETTE_CRISTEL, cristel_facing(490),
                                    movement.player.walk_frame, False, cristel_expression(), anim_frame)
    movement.draw_pickup_zones(surf, anim_frame, {'circle': circle, 'font': font('icon')})


def draw_polaroid_scene5(surf, w, h):
    surf.fill((168, 216, 232))
    rect(surf, 0, h * 0.55, w, h * 0.45, (90, 138, 74))
    rect(surf, w * 0.3, h * 0.55, w * 0.4, 10, (106, 74, 48))
    rect(surf, w * 0.42, h * 0.6, 7, 16, (58, 90, 122))
    rect(surf, w * 0.48, h * 0.62, 6, 14, (176, 106, 128))


# ─────────────────────────────────────────────
# ESCENA 6 — Su cumpleaños
# ─────────────────────────────────────────────
def scene6_setup():
    global active_draw_fn
    ui.clear_hotspots()
    active_draw_fn = draw_scene6
    audio.start_ambient(165)

    def after_card():
        movement.enable_movement(300, 540, {'minX': 90, 'maxX': 700, 'groundY': 540})
        ui.hint_text = config.tr('\u2190 \u2192 / A D para moverte \u00b7 camina hacia los objetos', '\u2190 \u2192 / A D to move \u00b7 walk up to objects')

        def cubo():
            def collected():
                ui.collect_fragment(6)
                ui.add_inventory_item('cubo-tomado', '\U0001F4E6', config.tr('El cubo infinito (recuerdo)', 'The infinity cube (memory)'))

            def after_minigame():
                ui.queue_dialogue([
                    {'speaker': config.name_b(), 'text': config.tr('Con esas hojas armé un cubo infinito a mano. Horas de trabajo, solo para ella.', "With those pages I built an infinity cube by hand. Hours of work, just for her.")},
                ], collected)

            def start_minigame():
                minigames.start_cube(after_minigame)

            ui.queue_dialogue([
                {'speaker': config.name_b(), 'text': config.tr('Le pedí a un compañero que me imprimiera hojas con la letra de \"Die With A Smile\" e imágenes de Snoopy.', "I asked a classmate to print me pages with the lyrics of \"Die With A Smile\" and pictures of Snoopy.")},
            ], start_minigame)
        movement.add_pickup_zone(415, 540, 50, 'cubo-infinito', '\U0001F4E6', config.tr('El cubo infinito', 'The infinity cube'), cubo, ui.has_item('cubo-infinito'))

        def rosa():
            ui.queue_dialogue([{'speaker': config.name_b(), 'text': config.tr('Chocolates Ferrero, y una rosa eterna de color morado. Las llevé a su casa después de celebrar un poco en el colegio con sus amigas.', "Ferrero chocolates, and a purple everlasting rose. I brought them to her house after celebrating a bit at school with her friends.")}],
                               lambda: ui.add_inventory_item('rosa', '\U0001F339', config.tr('La rosa eterna morada', 'The purple everlasting rose')))
        movement.add_pickup_zone(540, 540, 50, 'rosa', '\U0001F339', config.tr('La rosa eterna morada', 'The purple everlasting rose'), rosa, ui.has_item('rosa'))

        def cristel_regalo():
            if not ui.has_item('rosa'):
                ui.queue_dialogue([{'speaker': config.name_b(), 'text': config.tr('Debería darle algo antes de acercarme así, sin nada en las manos.', "I should give her something before going over there empty-handed.")}])
                return
            if not _player_near(660, 100):
                ui.queue_dialogue([{'speaker': '', 'text': config.tr('(Acércate más a {c} para entregarle el regalo.)', "(Get closer to {c} to give her the gift.)")}])
                return

            def after_gift_dialogue():
                def on_choice(choice):
                    if choice == 'lift':
                        action = {'speaker': config.name_b(), 'text': config.tr('La abracé fuerte y le di un beso. La alcé entre mis brazos, la subí a mi altura para besarla mejor.', "I hugged her tight and kissed her. I lifted her up in my arms, up to my height, to kiss her better.")}
                    else:
                        action = {'speaker': config.name_b(), 'text': config.tr('La abracé fuerte. Le susurré que siempre estaría para ella, y luego la besé.', "I hugged her tight. I whispered that I'd always be there for her, and then I kissed her.")}

                    def finish():
                        ui.capture_polaroid(6, draw_polaroid_scene6)
                        movement.disable_movement()
                        memory_unlocked(6)
                    ui.queue_dialogue([
                        action,
                        {'speaker': config.name_b(), 'text': config.tr('Ese día sellé algo en mi cabeza: que siempre estaría para ella, sin importar qué pasara.', "That day I sealed something in my mind: that I'd always be there for her, no matter what happened.")},
                        {'speaker': '', 'text': config.tr('\u2726 Die With A Smile sonaba de fondo. Era su cumpleaños, y era perfecto. \u2726', "\u2726 Die With A Smile was playing in the background. It was her birthday, and it was perfect. \u2726")},
                    ], finish)
                ui.show_choice(config.tr('¿Qué hace {b} ahora?', 'What does {b} do now?'), [
                    ('lift', config.tr('La alza entre sus brazos para besarla mejor',
                                        'He lifts her up in his arms to kiss her better')),
                    ('whisper', config.tr('Le susurra algo al oído antes de besarla',
                                           'He whispers something in her ear before kissing her')),
                ], on_choice)
            ui.queue_dialogue([
                {'speaker': config.name_b(), 'text': config.tr('Le di mi regalo de último. Le dije que esperaba que le gustara, que era la mejor mujer que había tenido.', "I gave her my gift last. I told her I hoped she'd like it, that she was the best woman I'd ever had.")},
                {'speaker': config.name_c(), 'text': config.tr('{b}... esto es hermoso.', "{b}... this is beautiful.")},
            ], after_gift_dialogue)
        ui.add_hotspot(620, 320, 160, 220, config.name_c(), cristel_regalo)
        ui.render_progress(5, 6)

    ui.show_scene_card(config.tr('Recuerdo VI', 'Memory VI'), config.tr('Su cumpleaños', 'Her birthday'),
                        config.tr('Un cubo infinito hecho a mano, chocolates, una rosa eterna morada.',
                                  'A hand-made infinity cube, chocolates, a purple everlasting rose.'), after_card)


def draw_scene6(surf):
    gradient_rect(surf, 0, 0, W, 400, (58, 40, 64), (138, 90, 104))
    for i in range(30):
        sx, sy = (i * 97) % W, (i * 53) % 300
        tw = math.sin(anim_frame * 0.05 + i) * 0.5 + 0.5
        alpha = int((0.3 + tw * 0.5) * 255)
        s = pygame.Surface((2, 2), pygame.SRCALPHA)
        s.fill((255, 255, 255, max(0, min(255, alpha))))
        surf.blit(s, (sx, sy))
    tile_ground(surf, 0, 460, W, H - 460, (46, 38, 52), (38, 30, 44), tile_size=26)
    rect(surf, 0, 454, W, 8, (26, 20, 32))
    rect(surf, 420, 140, 220, 320, (74, 58, 48))
    rect(surf, 460, 280, 100, 180, (106, 72, 40))
    glow_a = int((0.5 + math.sin(anim_frame * 0.06) * 0.1) * 255)
    s2 = pygame.Surface((180, 100), pygame.SRCALPHA)
    s2.fill((244, 216, 150, max(0, min(255, glow_a))))
    surf.blit(s2, (440, 160))
    rect(surf, 360, 420, 280, 14, (90, 69, 48))
    rect(surf, 370, 410, 10, 14, (74, 58, 40))
    rect(surf, 620, 410, 10, 14, (74, 58, 40))

    if not ui.has_item('cubo-tomado'):
        cube_y = 340 + math.sin(anim_frame * 0.04) * 3
        rect(surf, 380, cube_y, 70, 70, (244, 236, 224))
        rect(surf, 388, cube_y + 8, 54, 54, (232, 196, 204))
        rect(surf, 396, cube_y + 16, 38, 38, (244, 236, 224))
        note = font('tiny').render('\u266A', True, (138, 90, 104))
        surf.blit(note, (404, cube_y + 32))

    for i in range(3):
        circle(surf, 500 + i * 16, 400, 8, (201, 160, 74))

    if not ui.has_item('rosa'):
        rect(surf, 560, 360, 4, 55, (58, 90, 48))
        circle(surf, 562, 355, 14, (122, 74, 138))
        circle(surf, 556, 348, 9, (138, 90, 154)); circle(surf, 568, 348, 9, (138, 90, 154))

    draw_walk_character(surf, movement.player.x, movement.player.y, movement.player.scale,
                         PALETTE_BREYNER, movement.player.facing, movement.player.walk_frame,
                         movement.player.moving, anim_frame)
    draw_walk_character_expression(surf, 525, 538, 1.5, PALETTE_CRISTEL, cristel_facing(525),
                                    movement.player.walk_frame, False, cristel_expression(), anim_frame)
    movement.draw_pickup_zones(surf, anim_frame, {'circle': circle, 'font': font('icon')})

    for i in range(4):
        t = (anim_frame * 0.6 + i * 50) % 180
        alpha = max(0, int(255 * (1 - t / 180)))
        note = font('small').render('\u266A', True, (232, 196, 204))
        note.set_alpha(alpha)
        surf.blit(note, (480 + i * 20, 480 - t))


def draw_polaroid_scene6(surf, w, h):
    surf.fill((58, 40, 64))
    rect(surf, 0, h * 0.7, w, h * 0.3, (42, 34, 48))
    rect(surf, w * 0.15, h * 0.35, w * 0.25, w * 0.25, (244, 236, 224))
    circle(surf, w * 0.65, h * 0.45, 10, (122, 74, 138))
    rect(surf, w * 0.5, h * 0.55, 7, 16, (58, 90, 122))
    rect(surf, w * 0.57, h * 0.57, 6, 14, (176, 106, 128))


# ─────────────────────────────────────────────
# ESCENA FINAL
# ─────────────────────────────────────────────
def final_setup():
    global active_draw_fn
    ui.clear_hotspots()
    movement.disable_movement()
    active_draw_fn = draw_scene_final
    audio.stop_ambient()
    audio.start_ambient(140)
    ui.render_progress(6, 6)
    ui.show_scene_card(config.tr('Recuerdo final', 'Final memory'), config.tr('Lo que queda', 'What remains'),
                        config.tr(
                            f'{len(ui.fragments)}/6 fragmentos encontrados \u00b7 {len(ui.polaroids)}/6 fotografías reveladas',
                            f'{len(ui.fragments)}/6 fragments found \u00b7 {len(ui.polaroids)}/6 photographs revealed'),
                        lambda: None)

    def start_final_dialogue():
        ui.queue_dialogue([
            {'speaker': '', 'text': config.tr('Habían recorrido los seis recuerdos. {b} se quedó en silencio, esperando.', "They had gone through the six memories. {b} stood in silence, waiting.")},
            {'speaker': config.name_c(), 'text': config.tr('No... no recuerdo nada de eso, {b}. Lo siento mucho.', "No... I don't remember any of that, {b}. I'm so sorry.")},
            {'speaker': config.name_b(), 'text': config.tr('Está bien. Solo quería que lo supieras, aunque no lo recuerdes.', "It's okay. I just wanted you to know, even if you don't remember it.")},
            {'speaker': config.name_c(), 'text': config.tr('Espera...', "Wait...")},
            {'speaker': config.name_c(), 'text': config.tr('¿Por qué de repente siento que el morado me gusta mucho? ¿Y por qué tengo ganas de escuchar una canción que no sé ni cómo se llama, pero la siento conocida?', "Why do I suddenly feel like I really love the color purple? And why do I want to listen to a song I don't even know the name of, but it feels familiar?")},
            {'speaker': config.name_b(), 'text': config.tr('...', "...")},
            {'speaker': config.name_c(), 'text': config.tr('No es un recuerdo. Es más como... una sensación. Como si algo de eso siguiera aquí, aunque no sepa por qué.', "It's not a memory. It's more like... a feeling. Like something from that is still here, even if I don't know why.")},
            {'speaker': config.name_b(), 'text': config.tr('Tal vez no todo se olvida del todo. Tal vez algunas cosas se quedan, aunque ya no tengan nombre.', "Maybe not everything is forgotten completely. Maybe some things stay, even without a name anymore.")},
            {'speaker': '', 'text': config.tr('{b} sonrió. No era el final que había imaginado. Pero no era nada, tampoco.', "{b} smiled. It wasn't the ending he had imagined. But it wasn't nothing, either.")},
            {'speaker': '', 'text': config.tr('\u2726 FIN \u2726', "\u2726 THE END \u2726")},
        ], start_epilogue)

    # arranca ~2.5s después (similar al setTimeout original); usamos el propio
    # scene-card como temporizador: su callback ya se dispara tras ~3.8s,
    # así que encadenamos el diálogo directamente ahí.
    global _final_dialogue_pending
    _final_dialogue_pending = start_final_dialogue


_final_dialogue_pending = None
_credits_shown = False


def start_epilogue():
    """Inicia el epílogo narrativo después del diálogo de la escena final."""
    movement.disable_movement()
    ui.clear_hotspots()
    epilogue.manager.start(show_end_credits)


def epilogue_active():
    """Indica si una pantalla del epílogo está activa."""
    return epilogue.manager.current is not None


def final_update_hook():
    """Llamado cada frame por main.py mientras la escena final está activa."""
    global _final_dialogue_pending
    if _final_dialogue_pending and not ui.scene_card_active and not ui.dialogue_active:
        cb = _final_dialogue_pending
        _final_dialogue_pending = None
        cb()


def show_end_credits():
    global _credits_shown
    _credits_shown = True
    ui.show_persistent_card(
        config.tr('524 días \u00b7 17 meses \u00b7 una historia real', '524 days \u00b7 17 months \u00b7 a real story'),
        config.tr('{b} & {c}', '{b} & {c}'),
        [config.tr('Hecho con los recuerdos reales de dos personas.', 'Made from the real memories of two people.'),
         config.tr('22 de octubre, 2024 \u2014 y todo lo que vino después.',
                    'October 22nd, 2024 \u2014 and everything that came after.')],
    )


def draw_scene_final(surf):
    gradient_rect(surf, 0, 0, W, H, (42, 36, 56), (122, 90, 120))
    radial_glow(surf, W // 2, 380, 400, (232, 196, 206), max_alpha=45)
    rect(surf, 0, 480, W, H - 480, (26, 22, 34))
    rect(surf, 0, 474, W, 8, (15, 12, 22))
    for i in range(40):
        sx, sy = (i * 83) % W, (i * 47) % 350
        tw = math.sin(anim_frame * 0.04 + i * 1.3) * 0.5 + 0.5
        alpha = max(0, min(255, int((0.2 + tw * 0.6) * 255)))
        s = pygame.Surface((2, 2), pygame.SRCALPHA)
        s.fill((255, 255, 255, alpha))
        surf.blit(s, (sx, sy))

    rose_x = W // 2
    rect(surf, rose_x - 2, 420, 4, 60, (42, 58, 32))
    circle(surf, rose_x, 410, 16, (106, 74, 122))
    circle(surf, rose_x - 7, 402, 10, (122, 90, 138)); circle(surf, rose_x + 7, 402, 10, (122, 90, 138))
    glow_a = max(0, min(255, int((0.3 + math.sin(anim_frame * 0.05) * 0.15) * 255)))
    s2 = pygame.Surface((60, 60), pygame.SRCALPHA)
    pygame.draw.circle(s2, (163, 122, 176, glow_a), (30, 30), 30)
    surf.blit(s2, (rose_x - 30, 378))

    draw_walk_character(surf, rose_x - 90, 540, 1.7, PALETTE_BREYNER, 'right', 0, False, anim_frame)
    draw_walk_character_expression(surf, rose_x + 90, 540, 1.5, PALETTE_CRISTEL, 'left', 0, False, 'warm', anim_frame)  # pose final fija, ambos de frente


# ─────────────────────────────────────────────
# REGISTRO DE ESCENAS
# ─────────────────────────────────────────────
SCENES = [
    {'setup': intro_setup},
    {'setup': scene1_setup},
    {'setup': scene2_setup},
    {'setup': scene3_setup},
    {'setup': scene4_setup},
    {'setup': scene5_setup},
    {'setup': scene6_setup},
    {'setup': final_setup},
]


def start():
    """Llamar una vez, al presionar 'Empezar'."""
    ui.reset_all()
    save_system.delete_save()
    goto_scene(0)


POLAROID_DRAW_FNS = {
    1: draw_polaroid_scene1, 2: draw_polaroid_scene2, 3: draw_polaroid_scene3,
    4: draw_polaroid_scene4, 5: draw_polaroid_scene5, 6: draw_polaroid_scene6,
}


def resume_from_save(data):
    """Llamar al presionar 'CONTINUAR': restaura el progreso guardado y salta a esa escena."""
    ui.reset_all()
    ui.memories_found = data.get('memories_found', 0)
    for i in data.get('fragments', []):
        ui.fragments.append(i)
    for i in data.get('polaroid_scenes', []):
        fn = POLAROID_DRAW_FNS.get(i)
        if fn:
            ui.polaroids.append({'scene': i, 'draw': fn})
    for item in data.get('inventory', []):
        ui.inventory.append(item)
    names = data.get('names', {})
    if names.get('breyner'):
        config.set_name_b(names['breyner'])
    if names.get('cristel'):
        config.set_name_c(names['cristel'])
    if data.get('language'):
        config.set_language(data['language'])
    if data.get('volume') is not None:
        config.set_volume(data['volume'])
    if data.get('control_scheme'):
        config.set_control_scheme(data['control_scheme'])
    goto_scene(data.get('resume_index', 1))


def tick(surf, frame):
    """Dibuja la escena activa o, al final, la secuencia de epílogo."""
    global anim_frame
    anim_frame = frame
    if epilogue_active():
        epilogue.manager.draw(surf)
        return
    _drawing.set_pixelate(True)
    if active_draw_fn:
        active_draw_fn(surf)
    if current_scene_index == 7:
        final_update_hook()
