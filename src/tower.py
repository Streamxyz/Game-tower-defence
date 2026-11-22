"""
Tower base class and specialized military weapon platforms (Gatling, Missile, Sniper, Tesla).
"""

import math
import pygame
from src.config import TOWER_SPECS, GRID_SIZE
from src.projectile import Projectile, BeamEffect, Particle


class Tower:
    def __init__(self, tower_type, col, row):
        self.type = tower_type
        self.col = col
        self.row = row
        self.specs = TOWER_SPECS[tower_type]

        self.x = col * GRID_SIZE + GRID_SIZE // 2
        self.y = row * GRID_SIZE + GRID_SIZE // 2

        self.level = 1
        self.total_invested = self.specs["cost"]

        self.damage = self.specs["damage"]
        self.range = self.specs["range"]
        self.fire_rate = self.specs["fire_rate"]
        self.bullet_speed = self.specs["bullet_speed"]

        self.cooldown = 0.0
        self.angle = 0.0
        self.current_target = None
        self.kills = 0
        self.damage_dealt = 0

    @property
    def upgrade_cost(self):
        return int(self.specs["upgrade_cost"] * (1.4 ** (self.level - 1)))

    @property
    def sell_value(self):
        return int(self.total_invested * 0.70)

    def upgrade(self):
        cost = self.upgrade_cost
        self.total_invested += cost
        self.level += 1
        self.damage = int(self.damage * 1.35)
        self.range = int(self.range * 1.12)
        self.fire_rate = max(0.08, self.fire_rate * 0.90)

    def find_target(self, enemies):
        """Picks the enemy furthest along the path within range."""
        best_enemy = None
        best_dist_traveled = -1.0

        for enemy in enemies:
            if enemy.is_dead or enemy.reached_end:
                continue
            dist_to_tower = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist_to_tower <= self.range:
                if enemy.distance_traveled > best_dist_traveled:
                    best_dist_traveled = enemy.distance_traveled
                    best_enemy = enemy

        return best_enemy

    def update(self, dt, enemies, projectiles, beams, particles, sound_mgr):
        if self.cooldown > 0:
            self.cooldown -= dt

        target = self.find_target(enemies)
        self.current_target = target

        if target:
            dx = target.x - self.x
            dy = target.y - self.y
            self.angle = math.atan2(dy, dx)

            if self.cooldown <= 0:
                self.shoot(target, projectiles, beams, particles, sound_mgr)
                self.cooldown = self.fire_rate

    def shoot(self, target, projectiles, beams, particles, sound_mgr):
        if self.type == "vulcan":
            sound_mgr.play("gatling")
            projectiles.append(
                Projectile(self.x, self.y, target, self.damage, self.bullet_speed, proj_type="kinetic")
            )
            # Muzzle flash
            for _ in range(2):
                particles.append(Particle(self.x, self.y, "spark"))

        elif self.type == "missile":
            sound_mgr.play("missile_launch")
            splash = self.specs.get("splash_radius", 60)
            projectiles.append(
                Projectile(self.x, self.y, target, self.damage, self.bullet_speed, proj_type="explosive", splash_radius=splash)
            )

        elif self.type == "sniper":
            sound_mgr.play("sniper")
            # Instant kinetic rail hit
            target.take_damage(self.damage)
            beams.append(BeamEffect((self.x, self.y), (target.x, target.y), color=(80, 240, 160), duration=0.15, width=4))
            for _ in range(5):
                particles.append(Particle(target.x, target.y, "spark"))

        elif self.type == "tesla":
            sound_mgr.play("tesla")
            target.take_damage(self.damage)
            target.apply_slow(self.specs.get("slow_factor", 0.5), self.specs.get("slow_duration", 2.0))
            beams.append(BeamEffect((self.x, self.y), (target.x, target.y), color=(100, 200, 255), duration=0.18, width=5))
            for _ in range(6):
                particles.append(Particle(target.x, target.y, "electric"))

    def draw(self, surface, is_selected=False):
        center = (self.x, self.y)

        # Draw range circle if selected
        if is_selected:
            range_surf = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surf, (80, 180, 240, 45), (self.range, self.range), self.range)
            pygame.draw.circle(range_surf, (100, 200, 255, 160), (self.range, self.range), self.range, 2)
            surface.blit(range_surf, (self.x - self.range, self.y - self.range))

        # Base Platform
        base_size = int(GRID_SIZE * 0.8)
        base_rect = pygame.Rect(self.x - base_size // 2, self.y - base_size // 2, base_size, base_size)
        pygame.draw.rect(surface, (40, 48, 55), base_rect, border_radius=6)
        pygame.draw.rect(surface, (70, 80, 90), base_rect, 2, border_radius=6)

        # Level indicator pips
        for lvl in range(min(5, self.level)):
            pip_x = self.x - base_size // 2 + 5 + lvl * 6
            pip_y = self.y + base_size // 2 - 5
            pygame.draw.circle(surface, (255, 215, 0), (pip_x, pip_y), 2)

        # Turret Rotational Mount
        turret_surf = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        t_center = (GRID_SIZE // 2, GRID_SIZE // 2)

        color = self.specs["color"]
        if self.type == "vulcan":
            # Twin barrels
            pygame.draw.line(turret_surf, (180, 180, 180), t_center, (t_center[0] + 16, t_center[1] - 3), 3)
            pygame.draw.line(turret_surf, (180, 180, 180), t_center, (t_center[0] + 16, t_center[1] + 3), 3)
            pygame.draw.circle(turret_surf, color, t_center, 9)

        elif self.type == "missile":
            # Missile pod (quad box)
            pod_rect = pygame.Rect(t_center[0] - 6, t_center[1] - 8, 18, 16)
            pygame.draw.rect(turret_surf, color, pod_rect, border_radius=3)
            pygame.draw.circle(turret_surf, (220, 40, 40), (t_center[0] + 8, t_center[1] - 4), 3)
            pygame.draw.circle(turret_surf, (220, 40, 40), (t_center[0] + 8, t_center[1] + 4), 3)

        elif self.type == "sniper":
            # Long railgun barrel
            pygame.draw.line(turret_surf, (220, 220, 220), t_center, (t_center[0] + 22, t_center[1]), 4)
            pygame.draw.circle(turret_surf, color, t_center, 8)

        elif self.type == "tesla":
            # Tesla coil dome
            pygame.draw.circle(turret_surf, color, t_center, 11)
            pygame.draw.circle(turret_surf, (200, 240, 255), t_center, 5)

        # Rotate turret towards angle
        deg = -math.degrees(self.angle)
        rotated_turret = pygame.transform.rotate(turret_surf, deg)
        rot_rect = rotated_turret.get_rect(center=center)
        surface.blit(rotated_turret, rot_rect.topleft)
