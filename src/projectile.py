"""
Projectiles, guided missiles, sniper laser beams, electric arcs, and explosion effects.
"""

import math
import random
import pygame


class Projectile:
    def __init__(self, x, y, target_enemy, damage, speed, proj_type="kinetic", splash_radius=0):
        self.x = float(x)
        self.y = float(y)
        self.target = target_enemy
        self.damage = damage
        self.speed = speed
        self.proj_type = proj_type
        self.splash_radius = splash_radius
        self.is_dead = False

        # Last known target coordinates (for rockets/bullets if enemy dies mid-flight)
        self.target_x = float(target_enemy.x)
        self.target_y = float(target_enemy.y)

        self.angle = 0.0

    def update(self, dt, all_enemies, sound_mgr, particles):
        if self.is_dead:
            return

        if not self.target.is_dead and not self.target.reached_end:
            self.target_x = self.target.x
            self.target_y = self.target.y

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)

        move_dist = self.speed * dt
        self.angle = math.atan2(dy, dx)

        if dist <= move_dist or dist < 12:
            self.x = self.target_x
            self.y = self.target_y
            self.hit(all_enemies, sound_mgr, particles)
            self.is_dead = True
        else:
            self.x += (dx / dist) * move_dist
            self.y += (dy / dist) * move_dist

            # Rocket smoke trail
            if self.proj_type == "explosive" and random.random() < 0.45:
                particles.append(Particle(self.x, self.y, "smoke"))

    def hit(self, all_enemies, sound_mgr, particles):
        if self.splash_radius > 0:
            sound_mgr.play("explosion")
            # Area of Effect damage
            for e in all_enemies:
                if not e.is_dead and not e.reached_end:
                    d = math.hypot(e.x - self.x, e.y - self.y)
                    if d <= self.splash_radius:
                        falloff = max(0.3, 1.0 - (d / self.splash_radius))
                        e.take_damage(self.damage * falloff)
            # Create explosion visual particles
            for _ in range(14):
                particles.append(Particle(self.x, self.y, "fire"))
        else:
            sound_mgr.play("hit")
            if not self.target.is_dead:
                self.target.take_damage(self.damage)
            for _ in range(4):
                particles.append(Particle(self.x, self.y, "spark"))

    def draw(self, surface):
        if self.is_dead:
            return

        pos = (int(self.x), int(self.y))
        if self.proj_type == "explosive":
            # Missile body
            deg = -math.degrees(self.angle)
            msurf = pygame.Surface((14, 8), pygame.SRCALPHA)
            pygame.draw.polygon(msurf, (220, 220, 220), [(12, 4), (2, 1), (2, 7)])
            pygame.draw.rect(msurf, (220, 40, 40), (0, 1, 3, 6))  # Red warhead/thruster
            rotated = pygame.transform.rotate(msurf, deg)
            surface.blit(rotated, rotated.get_rect(center=pos).topleft)
        else:
            # High velocity bullet / tracer
            end_x = int(self.x - math.cos(self.angle) * 8)
            end_y = int(self.y - math.sin(self.angle) * 8)
            pygame.draw.line(surface, (255, 220, 80), pos, (end_x, end_y), 3)


class Particle:
    def __init__(self, x, y, p_type="spark"):
        self.x = float(x)
        self.y = float(y)
        self.p_type = p_type
        self.life = 1.0

        angle = random.uniform(0, 2 * math.pi)
        if p_type == "fire":
            speed = random.uniform(20, 90)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.decay = random.uniform(2.5, 4.5)
            self.radius = random.uniform(4, 9)
        elif p_type == "smoke":
            speed = random.uniform(5, 25)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.decay = random.uniform(1.2, 2.2)
            self.radius = random.uniform(3, 7)
        elif p_type == "electric":
            speed = random.uniform(30, 120)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.decay = random.uniform(4.0, 7.0)
            self.radius = random.uniform(2, 4)
        else: # spark
            speed = random.uniform(40, 140)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.decay = random.uniform(3.5, 6.0)
            self.radius = random.uniform(2, 3)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= self.decay * dt

    def draw(self, surface):
        if self.life <= 0:
            return
        pos = (int(self.x), int(self.y))
        r = max(1, int(self.radius * self.life))

        if self.p_type == "fire":
            color = (255, int(180 * self.life), int(40 * self.life))
        elif self.p_type == "smoke":
            shade = int(120 + 80 * (1.0 - self.life))
            color = (shade, shade, shade)
        elif self.p_type == "electric":
            color = (100, 200, 255)
        else:
            color = (255, 240, 160)

        pygame.draw.circle(surface, color, pos, r)


class BeamEffect:
    """Instantaneous laser / sniper beam or lightning arc."""
    def __init__(self, start_pos, end_pos, color=(255, 60, 60), duration=0.12, width=3):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        self.duration = duration
        self.timer = duration
        self.width = width

    def update(self, dt):
        self.timer -= dt

    @property
    def is_dead(self):
        return self.timer <= 0

    def draw(self, surface):
        if self.is_dead:
            return
        alpha_pct = max(0.0, self.timer / self.duration)
        w = max(1, int(self.width * alpha_pct))
        pygame.draw.line(surface, self.color, self.start_pos, self.end_pos, w)
