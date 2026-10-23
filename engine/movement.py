"""
Sistema de movimiento fluido, puerto 1:1 de movement-system.js.
Breyner (el jugador) gira a la dirección real en la que camina.
"""
import math
import pygame

WALK_FRAMES = 8


class Player:
    def __init__(self):
        self.x = 460.0
        self.y = 540.0
        self.target_x = 460.0
        self.vx = 0.0
        self.max_speed = 4.5
        self.acceleration = 0.38
        self.friction = 0.72
        self.moving = False
        self.facing = 'right'
        self.walk_frame = 0
        self.walk_timer = 0.0
        self.scale = 1.7


player = Player()
movement_enabled = False
walk_bounds = {'minX': 80, 'maxX': 880, 'groundY': 540}
pickup_zones = []  # dicts: x,y,radius,id,icon,name,on_pickup,collected


def enable_movement(start_x, ground_y, bounds):
    global movement_enabled, walk_bounds, pickup_zones
    movement_enabled = True
    player.x = start_x
    player.target_x = start_x
    player.vx = 0.0
    player.y = ground_y
    walk_bounds = bounds
    pickup_zones = []


def disable_movement():
    global movement_enabled, pickup_zones
    movement_enabled = False
    player.vx = 0.0
    player.moving = False
    pickup_zones = []


def add_pickup_zone(x, y, radius, item_id, icon, name, on_pickup, already_collected):
    pickup_zones.append({
        'x': x, 'y': y, 'radius': radius, 'id': item_id, 'icon': icon,
        'name': name, 'on_pickup': on_pickup, 'collected': already_collected,
    })


def update_player_movement(keys_held, touch_dir=0):
    if not movement_enabled:
        return

    input_dir = 0
    if keys_held[pygame.K_LEFT] or keys_held[pygame.K_a]:
        input_dir -= 1
    if keys_held[pygame.K_RIGHT] or keys_held[pygame.K_d]:
        input_dir += 1
    if input_dir == 0 and touch_dir != 0:
        input_dir = 1 if touch_dir > 0 else -1

    if input_dir != 0:
        player.vx += input_dir * player.acceleration * 1.5
        player.target_x = player.x + input_dir * 200
        player.facing = 'left' if input_dir < 0 else 'right'
    else:
        dx = player.target_x - player.x
        if abs(dx) > 3:
            want_dir = 1 if dx > 0 else -1
            player.vx += want_dir * player.acceleration
            player.facing = 'left' if want_dir < 0 else 'right'
            if abs(dx) < 50:
                player.vx *= 0.7
        else:
            player.vx *= player.friction
            if abs(player.vx) < 0.1:
                player.vx = 0.0
                player.target_x = player.x

    player.vx = max(-player.max_speed, min(player.max_speed, player.vx))
    if input_dir == 0:
        player.vx *= player.friction
    player.x += player.vx
    player.x = max(walk_bounds['minX'], min(walk_bounds['maxX'], player.x))

    player.moving = abs(player.vx) > 0.3
    if player.moving:
        player.walk_timer += abs(player.vx) * 0.18
        if player.walk_timer >= 1:
            player.walk_timer = 0.0
            player.walk_frame = (player.walk_frame + 1) % WALK_FRAMES
    else:
        player.walk_frame = 0
        player.walk_timer = 0.0

    for zone in pickup_zones:
        if zone['collected']:
            continue
        if abs(player.x - zone['x']) < zone['radius']:
            zone['collected'] = True
            zone['on_pickup']()


def click_to_walk(mx):
    if not movement_enabled:
        return
    player.target_x = max(walk_bounds['minX'], min(walk_bounds['maxX'], mx))


def draw_pickup_zones(surf, anim_frame, draw_fns):
    """draw_fns: dict con 'circle' y 'font' para dibujar el icono/anillo."""
    circle = draw_fns['circle']
    font = draw_fns['font']
    for zone in pickup_zones:
        if zone['collected']:
            continue
        bob = math.sin(anim_frame * 0.09) * 5
        alpha = int(46 + math.sin(anim_frame * 0.08) * 20)
        circle(surf, zone['x'], zone['y'] - 2, zone['radius'] * 0.35, (232, 163, 176, max(0, alpha)))

        label = font.render(zone['icon'], True, (244, 233, 216))
        rect_ = label.get_rect(center=(int(zone['x']), int(zone['y'] - 36 + bob)))
        surf.blit(label, rect_)

        dist = abs(player.x - zone['x'])
        prox_radius = zone['radius'] + 40
        if dist < prox_radius:
            ring_alpha = max(0, int(140 * (1 - dist / prox_radius)))
            ring_surf = pygame.Surface((zone['radius'] * 2, zone['radius'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (232, 163, 176, ring_alpha),
                                (int(zone['radius']), int(zone['radius'])), int(zone['radius']), width=2)
            surf.blit(ring_surf, (zone['x'] - zone['radius'], zone['y'] - 20 - zone['radius']))
