"""
Main Game State Controller: manages loop, input routing, state transitions, and rendering.
"""

import sys
import pygame

from src.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS,
    STARTING_CASH, STARTING_LIVES, TOWER_SPECS, GRID_SIZE
)
from src.map_grid import MapGrid
from src.tower import Tower
from src.wave_manager import WaveManager
from src.sound import SoundManager
from src.ui import UI


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Modern Military Tower Defence")

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.sound_mgr = SoundManager()
        self.reset_game()

    def reset_game(self):
        self.map_grid = MapGrid()
        self.wave_mgr = WaveManager(self.map_grid.pixel_waypoints)
        self.ui = UI()

        self.cash = STARTING_CASH
        self.lives = STARTING_LIVES

        self.active_enemies = []
        self.projectiles = []
        self.beams = []
        self.particles = []

        self.selected_shop_tower = None
        self.selected_grid_tower = None

        self.game_speed = 1.0  # 1.0x, 2.0x, 3.0x
        self.is_paused = False
        self.state = "PLAYING"  # PLAYING, GAME_OVER, VICTORY

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds

            # Handle SDL events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                    elif event.button == 3:  # Right click
                        self.selected_shop_tower = None
                        self.selected_grid_tower = None

            # Update & render
            self.update(dt)
            self.draw()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def handle_keydown(self, key):
        if key == pygame.K_SPACE:
            if self.state == "PLAYING" and not self.wave_mgr.wave_in_progress:
                self.wave_mgr.start_next_wave()
            elif self.state in ["GAME_OVER", "VICTORY"]:
                self.reset_game()
        elif key == pygame.K_p:
            self.is_paused = not self.is_paused
        elif key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
            t_types = ["vulcan", "missile", "sniper", "tesla"]
            idx = key - pygame.K_1
            self.selected_shop_tower = t_types[idx]
            self.selected_grid_tower = None
        elif key == pygame.K_ESCAPE:
            self.selected_shop_tower = None
            self.selected_grid_tower = None

    def handle_click(self, mouse_pos):
        mx, my = mouse_pos

        # Check UI button clicks on the right sidebar
        if mx >= self.ui.sidebar_x:
            # Wave button
            if self.ui.btn_wave.collidepoint(mx, my):
                if not self.wave_mgr.wave_in_progress and self.state == "PLAYING":
                    self.wave_mgr.start_next_wave()
                return

            # Speed toggle button
            if self.ui.btn_speed.collidepoint(mx, my):
                speeds = [1.0, 2.0, 3.0]
                curr_idx = speeds.index(self.game_speed) if self.game_speed in speeds else 0
                self.game_speed = speeds[(curr_idx + 1) % len(speeds)]
                return

            # Pause button
            if self.ui.btn_pause.collidepoint(mx, my):
                self.is_paused = not self.is_paused
                return

            # Shop cards
            for card in self.ui.shop_cards:
                if card["rect"].collidepoint(mx, my):
                    if self.selected_shop_tower == card["type"]:
                        self.selected_shop_tower = None
                    else:
                        self.selected_shop_tower = card["type"]
                        self.selected_grid_tower = None
                    return

            # Upgrade button
            if self.selected_grid_tower and self.ui.btn_upgrade.collidepoint(mx, my):
                cost = self.selected_grid_tower.upgrade_cost
                if self.cash >= cost:
                    self.cash -= cost
                    self.selected_grid_tower.upgrade()
                    self.sound_mgr.play("build")
                return

            # Sell button
            if self.selected_grid_tower and self.ui.btn_sell.collidepoint(mx, my):
                refund = self.selected_grid_tower.sell_value
                self.cash += refund
                del self.map_grid.towers[(self.selected_grid_tower.col, self.selected_grid_tower.row)]
                self.sound_mgr.play("sell")
                self.selected_grid_tower = None
                return

        # Otherwise clicked on the battlefield grid
        else:
            grid_pos = self.map_grid.get_grid_pos(mx, my)
            if not grid_pos:
                return
            col, row = grid_pos

            # If placing a tower from shop
            if self.selected_shop_tower:
                cost = TOWER_SPECS[self.selected_shop_tower]["cost"]
                if self.map_grid.is_tile_buildable(col, row) and self.cash >= cost:
                    self.cash -= cost
                    new_tower = Tower(self.selected_shop_tower, col, row)
                    self.map_grid.towers[(col, row)] = new_tower
                    self.sound_mgr.play("build")
                    # Keep selected for rapid multi-placement unless out of cash
                    if self.cash < cost:
                        self.selected_shop_tower = None
            else:
                # Selecting existing tower or empty tile
                if (col, row) in self.map_grid.towers:
                    self.selected_grid_tower = self.map_grid.towers[(col, row)]
                else:
                    self.selected_grid_tower = None

    def update(self, dt):
        if self.state != "PLAYING" or self.is_paused:
            return

        effective_dt = dt * self.game_speed

        # Update Wave Manager
        self.wave_mgr.update(effective_dt, self.active_enemies)

        # Update Enemies
        for enemy in self.active_enemies[:]:
            enemy.update(effective_dt)
            if enemy.is_dead:
                self.cash += enemy.bounty
                self.active_enemies.remove(enemy)
            elif enemy.reached_end:
                self.lives -= enemy.penalty
                self.active_enemies.remove(enemy)
                if self.lives <= 0:
                    self.lives = 0
                    self.state = "GAME_OVER"
                    self.sound_mgr.play("game_over")
                    return

        # Check Victory
        if self.wave_mgr.current_wave >= self.wave_mgr.max_waves and not self.wave_mgr.wave_in_progress and len(self.active_enemies) == 0:
            self.state = "VICTORY"
            self.sound_mgr.play("victory")
            return

        # Update Towers
        for tower in self.map_grid.towers.values():
            tower.update(
                effective_dt,
                self.active_enemies,
                self.projectiles,
                self.beams,
                self.particles,
                self.sound_mgr
            )

        # Update Projectiles
        for proj in self.projectiles[:]:
            proj.update(effective_dt, self.active_enemies, self.sound_mgr, self.particles)
            if proj.is_dead:
                self.projectiles.remove(proj)

        # Update Beams
        for beam in self.beams[:]:
            beam.update(effective_dt)
            if beam.is_dead:
                self.beams.remove(beam)

        # Update Particles
        for particle in self.particles[:]:
            particle.update(effective_dt)
            if particle.life <= 0:
                self.particles.remove(particle)

    def draw_placement_preview(self):
        if not self.selected_shop_tower:
            return

        mx, my = pygame.mouse.get_pos()
        grid_pos = self.map_grid.get_grid_pos(mx, my)
        if not grid_pos:
            return

        col, row = grid_pos
        is_valid = self.map_grid.is_tile_buildable(col, row)
        specs = TOWER_SPECS[self.selected_shop_tower]
        px, py = self.map_grid.get_center_pixel(col, row)

        # Draw Range Preview
        r = specs["range"]
        range_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        color_fill = (60, 200, 100, 35) if is_valid else (220, 40, 40, 35)
        color_stroke = (60, 220, 100, 150) if is_valid else (220, 40, 40, 150)
        pygame.draw.circle(range_surf, color_fill, (r, r), r)
        pygame.draw.circle(range_surf, color_stroke, (r, r), r, 2)
        self.screen.blit(range_surf, (px - r, py - r))

        # Highlight cell
        cell_rect = pygame.Rect(col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(self.screen, color_stroke, cell_rect, 2)

    def draw_overlays(self):
        if self.state in ["GAME_OVER", "VICTORY"]:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 14, 18, 210))
            self.screen.blit(overlay, (0, 0))

            f_large = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 46, bold=True)
            f_sub = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 20)

            if self.state == "GAME_OVER":
                title_surf = f_large.render("BASE OVERRUN - MISSION FAILED", True, (220, 40, 40))
                sub_surf = f_sub.render("Hostile military forces breached the perimeter. Press SPACE to Restart.", True, (220, 220, 220))
            else:
                title_surf = f_large.render("DEFENSE SUCCESSFUL - SECTOR SECURED!", True, (60, 210, 100))
                sub_surf = f_sub.render(f"All {self.wave_mgr.max_waves} hostile waves repelled! Press SPACE to Play Again.", True, (220, 220, 220))

            self.screen.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30)))
            self.screen.blit(sub_surf, sub_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30)))

    def draw(self):
        # 1. Map & Path
        self.map_grid.draw(self.screen)

        # 2. Towers
        for tower in self.map_grid.towers.values():
            is_sel = (tower == self.selected_grid_tower)
            tower.draw(self.screen, is_selected=is_sel)

        # 3. Enemies
        for enemy in self.active_enemies:
            enemy.draw(self.screen)

        # 4. Projectiles & Visual FX
        for proj in self.projectiles:
            proj.draw(self.screen)
        for beam in self.beams:
            beam.draw(self.screen)
        for particle in self.particles:
            particle.draw(self.screen)

        # 5. Cursor Placement Preview
        self.draw_placement_preview()

        # 6. Sidebar HUD & Shop
        self.ui.draw(
            self.screen,
            self.cash,
            self.lives,
            self.wave_mgr.current_wave,
            self.wave_mgr.max_waves,
            self.wave_mgr.wave_in_progress,
            self.selected_shop_tower,
            self.selected_grid_tower,
            self.game_speed,
            self.is_paused
        )

        # 7. Modal Overlays (Game Over / Victory)
        self.draw_overlays()
