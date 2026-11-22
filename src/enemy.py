"""
Hostile military vehicle / drone units with path traversal, health bars, and status effects.
"""

import math
import pygame
from src.config import ENEMY_SPECS


class Enemy:
    def __init__(self, enemy_type, waypoints, wave_scale=1.0):
        self.type = enemy_type
        self.specs = ENEMY_SPECS[enemy_type]

        self.waypoints = waypoints
        self.waypoint_index = 0

        self.x = float(waypoints[0][0])
        self.y = float(waypoints[0][1])

        # Apply wave scaling to HP and speed
        self.max_hp = self.specs["max_hp"] * wave_scale
        self.hp = self.max_hp
        self.base_speed = self.specs["speed"]
        self.bounty = int(self.specs["bounty"] * max(1.0, math.sqrt(wave_scale)))
        self.penalty = self.specs["penalty"]
        self.size = self.specs["size"]
        self.color = self.specs["color"]

        self.angle = 0.0
        self.reached_end = False
        self.is_dead = False

        # Status modifiers (e.g. EMP slow)
        self.slow_timer = 0.0
        self.slow_factor = 1.0

        # Total distance traveled along the path (for tower targeting priority)
        self.distance_traveled = 0.0

    @property
    def current_speed(self):
        if self.slow_timer > 0:
            return self.base_speed * self.slow_factor
        return self.base_speed

    def apply_slow(self, factor, duration):
        self.slow_factor = factor
        self.slow_timer = max(self.slow_timer, duration)

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.is_dead = True

    def update(self, dt):
        if self.is_dead or self.reached_end:
            return

        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slow_factor = 1.0

        target_x, target_y = self.waypoints[self.waypoint_index]
        dx = target_x - self.x
        dy = target_y - self.y
        dist_to_wp = math.hypot(dx, dy)

        move_dist = self.current_speed * dt

        if dist_to_wp <= move_dist:
            # Reached this waypoint
            self.x = target_x
            self.y = target_y
            self.distance_traveled += dist_to_wp
            self.waypoint_index += 1
            if self.waypoint_index >= len(self.waypoints):
                self.reached_end = True
                return
        else:
            # Advance towards waypoint
            self.angle = math.atan2(dy, dx)
            step_x = (dx / dist_to_wp) * move_dist
            step_y = (dy / dist_to_wp) * move_dist
            self.x += step_x
            self.y += step_y
            self.distance_traveled += move_dist

    def draw(self, surface):
        if self.is_dead or self.reached_end:
            return

        pos = (int(self.x), int(self.y))

        # Vehicle hull rendering rotated according to movement direction
        hull_surf = pygame.Surface((self.size * 2 + 4, self.size * 2 + 4), pygame.SRCALPHA)
        center = (self.size + 2, self.size + 2)

        # Body shape based on vehicle type
        hull_color = self.color
        if self.slow_timer > 0:
            # Electric blue tint when EMP-slowed
            hull_color = (
                min(255, int(self.color[0] * 0.4 + 40)),
                min(255, int(self.color[1] * 0.5 + 80)),
                min(255, int(self.color[2] * 0.5 + 200))
            )

        if self.type == "scout":
            # Diamond / drone shape
            points = [
                (center[0] + self.size, center[1]),
                (center[0], center[1] - self.size * 0.7),
                (center[0] - self.size * 0.7, center[1]),
                (center[0], center[1] + self.size * 0.7),
            ]
            pygame.draw.polygon(hull_surf, hull_color, points)
            pygame.draw.polygon(hull_surf, (255, 255, 255), points, 1)

        elif self.type == "tank" or self.type == "boss":
            # Heavy Tank with treads
            rect = pygame.Rect(center[0] - self.size, center[1] - self.size * 0.75, self.size * 2, self.size * 1.5)
            pygame.draw.rect(hull_surf, (30, 30, 30), rect) # Treads
            inner_rect = pygame.Rect(center[0] - self.size * 0.8, center[1] - self.size * 0.55, self.size * 1.6, self.size * 1.1)
            pygame.draw.rect(hull_surf, hull_color, inner_rect)
            # Turret
            pygame.draw.circle(hull_surf, (40, 45, 50), center, int(self.size * 0.45))
            pygame.draw.line(hull_surf, (20, 20, 20), center, (center[0] + self.size * 1.2, center[1]), 4)

        else: # Technical or APC
            rect = pygame.Rect(center[0] - self.size, center[1] - self.size * 0.6, self.size * 2, self.size * 1.2)
            pygame.draw.rect(hull_surf, hull_color, rect, border_radius=4)
            pygame.draw.rect(hull_surf, (30, 30, 30), rect, 2, border_radius=4)
            # Windshield / Cabin
            cabin_rect = pygame.Rect(center[0] - self.size * 0.2, center[1] - self.size * 0.4, self.size * 0.8, self.size * 0.8)
            pygame.draw.rect(hull_surf, (40, 60, 80), cabin_rect)

        # Rotate hull
        deg = -math.degrees(self.angle)
        rotated_surf = pygame.transform.rotate(hull_surf, deg)
        rot_rect = rotated_surf.get_rect(center=pos)
        surface.blit(rotated_surf, rot_rect.topleft)

        # Health bar
        bar_width = max(24, int(self.size * 1.8))
        bar_height = 4
        bar_x = pos[0] - bar_width // 2
        bar_y = pos[1] - self.size - 8

        # Background
        pygame.draw.rect(surface, (20, 20, 20), (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
        # Health fill
        pct = max(0.0, self.hp / self.max_hp)
        fill_color = (60, 200, 80) if pct > 0.5 else ((220, 180, 40) if pct > 0.25 else (220, 40, 40))
        pygame.draw.rect(surface, fill_color, (bar_x, bar_y, int(bar_width * pct), bar_height))
