"""
OLVIDO — versión Python/Pygame (compilable a web con pygbag)
Puerto fiel de olvido-v3-final.html: mismos diálogos, mecánicas, escenas.
Ahora con nombres de personajes personalizables, idioma ES/EN, volumen y
esquema de control (teclado / botones estilo GBA / touchpad) configurables
desde el menú principal.

Cómo probar en tu PC:
    pip install pygame-ce
    python main.py

Cómo generar la versión web (necesita internet, la descarga pygbag la hace):
    pip install pygbag
    pygbag main.py
    (abre la URL local que te muestre, típicamente http://localhost:8000)
"""
import asyncio
import pygame

import config
import save_system
from engine import audio, ui, movement
from engine.constants import W, H, FPS, PIXEL_SCALE, init_fonts
from engine import drawing
from engine.drawing import pixelate
import controls
import menus
import minigames
import scenes

app_state = 'start'   # 'start' | 'names' | 'settings' | 'game'
anim_frame = 0


async def main():
    global anim_frame, app_state

    audio.init_mixer()
    pygame.init()
    pygame.key.start_text_input()
    init_fonts()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption(config.tr('Olvido \u00b7 un recuerdo de {b} y {c}',
                                          'Olvido \u00b7 a memory of {b} and {c}'))
    clock = pygame.time.Clock()

    game_surf = pygame.Surface((W, H))
    world_surf = pygame.Surface((W, H))  # fondo + personajes: se pixela aparte del texto de UI

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if app_state == 'start':
                    nxt = menus.click_start(pos)
                    if nxt == 'continue':
                        data = save_system.load_game()
                        if data:
                            scenes.resume_from_save(data)
                            app_state = 'game'
                    elif nxt:
                        app_state = nxt
                        if nxt == 'game':
                            scenes.start()
                elif app_state == 'names':
                    nxt = menus.click_names(pos)
                    if nxt:
                        app_state = nxt
                elif app_state == 'settings':
                    nxt = menus.click_settings(pos)
                    if nxt:
                        app_state = nxt
                else:  # 'game'
                    if minigames.active():
                        minigames.handle_mousedown(pos)
                    else:
                        if scenes.epilogue_active() and scenes.epilogue.manager.handle_click(pos):
                            pass
                        else:
                            controls_active = movement.movement_enabled and not ui.blocking_ui()
                            if not (controls_active and controls.handle_mousedown(pos)):
                                consumed = ui.handle_click(pos)
                                if not consumed:
                                    movement.click_to_walk(pos[0])

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if app_state == 'game':
                    if minigames.active():
                        minigames.handle_mouseup()
                    else:
                        controls.handle_mouseup()

            elif event.type == pygame.MOUSEMOTION:
                if app_state == 'game':
                    if minigames.active():
                        minigames.handle_mousemotion(event.pos)
                    else:
                        controls.handle_mousemotion(event.pos)

            elif event.type == pygame.KEYDOWN:
                if app_state == 'names':
                    menus.keydown_names(event.key)

            elif event.type == pygame.TEXTINPUT:
                if app_state == 'names':
                    menus.textinput_names(event.text)

        if app_state == 'game':
            ui.handle_mousemotion(pygame.mouse.get_pos())
            if not minigames.active():
                keys = pygame.key.get_pressed()
                movement.update_player_movement(keys, controls.touch_dir)

        anim_frame += 1
        now = pygame.time.get_ticks()

        game_surf.fill((0, 0, 0))
        if app_state == 'start':
            menus.draw_start(game_surf)
        elif app_state == 'names':
            menus.draw_names(game_surf)
        elif app_state == 'settings':
            menus.draw_settings(game_surf)
        else:
            if scenes.epilogue_active():
                # El epílogo se dibuja directamente para conservar texto e imagen nítidos.
                scenes.tick(game_surf, anim_frame)
            else:
                world_surf.fill((0, 0, 0))
                scenes.tick(world_surf, anim_frame)
                frame_img = pixelate(world_surf, PIXEL_SCALE) if drawing.pixelate_world else world_surf
                game_surf.blit(frame_img, (0, 0))
            ui.update(now)
            ui.draw(game_surf, anim_frame)
            if movement.movement_enabled and not ui.blocking_ui() and not minigames.active():
                controls.draw(game_surf)
            minigames.update(now)
            minigames.draw(game_surf)
            audio.update_audio()

        screen.blit(game_surf, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)   # cede el control al navegador (requerido por pygbag)

    pygame.quit()


if __name__ == '__main__':
    asyncio.run(main())
