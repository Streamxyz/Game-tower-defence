"""
Modern Command Center HUD, Tower Purchase Shop, Selection & Upgrade Panel, Speed Controls.
"""

import pygame
from src.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE, GRID_COLS, SIDEBAR_WIDTH,
    COLOR_SIDEBAR_BG, COLOR_PANEL_HEADER, COLOR_ACCENT_GREEN,
    COLOR_ACCENT_AMBER, COLOR_ACCENT_RED, COLOR_ACCENT_BLUE,
    COLOR_TEXT_LIGHT, COLOR_TEXT_MUTED, TOWER_SPECS
)


class UI:
    def __init__(self):
        self.sidebar_x = GRID_COLS * GRID_SIZE
        self.sidebar_width = SIDEBAR_WIDTH
        self.sidebar_height = WINDOW_HEIGHT

        pygame.font.init()
        self.font_title = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 20, bold=True)
        self.font_main = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 15, bold=True)
        self.font_small = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 13)
        self.font_tiny = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 11)

        # Shop buttons configuration
        self.shop_cards = []
        shop_y = 120
        card_h = 62
        for t_type in ["vulcan", "missile", "sniper", "tesla"]:
            rect = pygame.Rect(self.sidebar_x + 12, shop_y, self.sidebar_width - 24, card_h)
            self.shop_cards.append({
                "type": t_type,
                "rect": rect,
                "specs": TOWER_SPECS[t_type]
            })
            shop_y += card_h + 10

        # Action Buttons
        self.btn_wave = pygame.Rect(self.sidebar_x + 12, 60, self.sidebar_width - 24, 42)
        self.btn_speed = pygame.Rect(self.sidebar_x + 12, shop_y + 10, (self.sidebar_width - 28) // 2, 36)
        self.btn_pause = pygame.Rect(self.sidebar_x + 16 + (self.sidebar_width - 28) // 2, shop_y + 10, (self.sidebar_width - 28) // 2, 36)

        # Tower selection upgrade/sell buttons
        panel_y = shop_y + 60
        self.btn_upgrade = pygame.Rect(self.sidebar_x + 12, panel_y + 80, (self.sidebar_width - 28) // 2, 36)
        self.btn_sell = pygame.Rect(self.sidebar_x + 16 + (self.sidebar_width - 28) // 2, panel_y + 80, (self.sidebar_width - 28) // 2, 36)

    def draw_status_bar(self, surface, cash, lives, wave, max_waves):
        # Top banner on sidebar
        header_rect = pygame.Rect(self.sidebar_x, 0, self.sidebar_width, 50)
        pygame.draw.rect(surface, COLOR_PANEL_HEADER, header_rect)
        pygame.draw.line(surface, (60, 75, 85), (self.sidebar_x, 50), (WINDOW_WIDTH, 50), 2)

        # Cash display
        cash_txt = self.font_main.render(f"${cash}", True, (255, 215, 0))
        surface.blit(cash_txt, (self.sidebar_x + 15, 15))

        # Lives display
        lives_color = COLOR_ACCENT_GREEN if lives > 8 else COLOR_ACCENT_RED
        lives_txt = self.font_main.render(f"HP: {lives}", True, lives_color)
        surface.blit(lives_txt, (self.sidebar_x + 120, 15))

        # Wave display
        wave_txt = self.font_main.render(f"WAVE: {wave}/{max_waves}", True, COLOR_TEXT_LIGHT)
        surface.blit(wave_txt, (self.sidebar_x + 210, 15))

    def draw_shop(self, surface, cash, selected_shop_tower):
        for card in self.shop_cards:
            rect = card["rect"]
            specs = card["specs"]
            can_afford = cash >= specs["cost"]
            is_active = selected_shop_tower == card["type"]

            # Background & border
            bg_color = (40, 50, 60) if is_active else ((28, 36, 42) if can_afford else (22, 26, 30))
            border_color = COLOR_ACCENT_GREEN if is_active else ((70, 85, 95) if can_afford else (45, 52, 58))

            pygame.draw.rect(surface, bg_color, rect, border_radius=6)
            pygame.draw.rect(surface, border_color, rect, 2 if is_active else 1, border_radius=6)

            # Color icon chip
            pygame.draw.circle(surface, specs["color"], (rect.x + 22, rect.y + rect.height // 2), 12)

            # Name & Cost
            text_color = COLOR_TEXT_LIGHT if can_afford else COLOR_TEXT_MUTED
            name_surf = self.font_main.render(specs["name"], True, text_color)
            surface.blit(name_surf, (rect.x + 44, rect.y + 10))

            cost_color = (255, 215, 0) if can_afford else COLOR_ACCENT_RED
            cost_surf = self.font_small.render(f"${specs['cost']}", True, cost_color)
            surface.blit(cost_surf, (rect.x + rect.width - 50, rect.y + 10))

            # Role / description
            desc_surf = self.font_tiny.render(f"DMG: {specs['damage']} | RNG: {specs['range']} | {specs['type'].upper()}", True, COLOR_TEXT_MUTED)
            surface.blit(desc_surf, (rect.x + 44, rect.y + 34))

    def draw_controls(self, surface, wave_in_progress, game_speed, is_paused):
        # Next Wave Button
        btn_color = (45, 60, 50) if wave_in_progress else COLOR_ACCENT_GREEN
        txt_color = COLOR_TEXT_MUTED if wave_in_progress else (255, 255, 255)
        label = "COMBAT IN PROGRESS..." if wave_in_progress else "DEPLOY NEXT WAVE (SPACE)"

        pygame.draw.rect(surface, btn_color, self.btn_wave, border_radius=6)
        pygame.draw.rect(surface, (80, 120, 90), self.btn_wave, 2, border_radius=6)
        txt = self.font_main.render(label, True, txt_color)
        surface.blit(txt, txt.get_rect(center=self.btn_wave.center))

        # Speed Button (1x / 2x / 3x)
        speed_label = f"SPEED: {game_speed}x"
        pygame.draw.rect(surface, (38, 48, 56), self.btn_speed, border_radius=6)
        pygame.draw.rect(surface, (70, 85, 95), self.btn_speed, 1, border_radius=6)
        stxt = self.font_main.render(speed_label, True, COLOR_TEXT_LIGHT)
        surface.blit(stxt, stxt.get_rect(center=self.btn_speed.center))

        # Pause Button
        pause_label = "RESUME" if is_paused else "PAUSE"
        p_color = COLOR_ACCENT_AMBER if is_paused else (38, 48, 56)
        pygame.draw.rect(surface, p_color, self.btn_pause, border_radius=6)
        pygame.draw.rect(surface, (70, 85, 95), self.btn_pause, 1, border_radius=6)
        ptxt = self.font_main.render(pause_label, True, COLOR_TEXT_LIGHT)
        surface.blit(ptxt, ptxt.get_rect(center=self.btn_pause.center))

    def draw_tower_details(self, surface, selected_tower, cash):
        if not selected_tower:
            # Tip box
            tip_rect = pygame.Rect(self.sidebar_x + 12, 480, self.sidebar_width - 24, 210)
            pygame.draw.rect(surface, (20, 25, 28), tip_rect, border_radius=6)
            pygame.draw.rect(surface, (40, 48, 54), tip_rect, 1, border_radius=6)

            tips = [
                "TACTICAL BRIEFING:",
                "- Click a tower card above to select it.",
                "- Click any empty green grid tile to build.",
                "- Click an existing tower to inspect & upgrade.",
                "- Gatling is best against swarm scouts.",
                "- Missiles deal AoE splash to clusters.",
                "- Railgun Snipers pierce armored tanks.",
                "- EMP Coils slow enemies for AoE rockets.",
                "- Press SPACE to start wave, ESC to deselect."
            ]
            for idx, line in enumerate(tips):
                col = COLOR_ACCENT_AMBER if idx == 0 else COLOR_TEXT_MUTED
                fnt = self.font_main if idx == 0 else self.font_tiny
                surf = fnt.render(line, True, col)
                surface.blit(surf, (tip_rect.x + 10, tip_rect.y + 12 + idx * 21))
            return

        # Tower Inspector Card
        panel_rect = pygame.Rect(self.sidebar_x + 12, 480, self.sidebar_width - 24, 210)
        pygame.draw.rect(surface, (30, 38, 45), panel_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_ACCENT_BLUE, panel_rect, 2, border_radius=6)

        # Title
        t_name = f"{selected_tower.specs['name']} (LVL {selected_tower.level})"
        title_surf = self.font_main.render(t_name, True, COLOR_TEXT_LIGHT)
        surface.blit(title_surf, (panel_rect.x + 12, panel_rect.y + 12))

        # Stats
        stats = [
            f"Damage: {selected_tower.damage}",
            f"Range: {selected_tower.range} px",
            f"Fire Rate: {1.0 / selected_tower.fire_rate:.1f} / sec",
            f"Target Priority: Furthest",
        ]
        for idx, stat in enumerate(stats):
            ssurf = self.font_small.render(stat, True, COLOR_TEXT_MUTED)
            surface.blit(ssurf, (panel_rect.x + 12, panel_rect.y + 40 + idx * 20))

        # Upgrade Button
        can_afford_up = cash >= selected_tower.upgrade_cost
        up_bg = (40, 80, 50) if can_afford_up else (35, 40, 45)
        self.btn_upgrade.y = panel_rect.y + 140
        pygame.draw.rect(surface, up_bg, self.btn_upgrade, border_radius=6)
        pygame.draw.rect(surface, COLOR_ACCENT_GREEN if can_afford_up else (60, 70, 75), self.btn_upgrade, 1, border_radius=6)
        up_txt = self.font_small.render(f"UPGRADE (${selected_tower.upgrade_cost})", True, COLOR_TEXT_LIGHT)
        surface.blit(up_txt, up_txt.get_rect(center=self.btn_upgrade.center))

        # Sell Button
        self.btn_sell.y = panel_rect.y + 140
        pygame.draw.rect(surface, (70, 35, 35), self.btn_sell, border_radius=6)
        pygame.draw.rect(surface, COLOR_ACCENT_RED, self.btn_sell, 1, border_radius=6)
        sell_txt = self.font_small.render(f"SELL (${selected_tower.sell_value})", True, COLOR_TEXT_LIGHT)
        surface.blit(sell_txt, sell_txt.get_rect(center=self.btn_sell.center))

    def draw(self, surface, cash, lives, wave, max_waves, wave_in_progress, selected_shop_tower, selected_grid_tower, game_speed, is_paused):
        # Draw sidebar background
        sidebar_rect = pygame.Rect(self.sidebar_x, 0, self.sidebar_width, self.sidebar_height)
        pygame.draw.rect(surface, COLOR_SIDEBAR_BG, sidebar_rect)
        pygame.draw.line(surface, (45, 55, 65), (self.sidebar_x, 0), (self.sidebar_x, WINDOW_HEIGHT), 2)

        self.draw_status_bar(surface, cash, lives, wave, max_waves)
        self.draw_controls(surface, wave_in_progress, game_speed, is_paused)
        self.draw_shop(surface, cash, selected_shop_tower)
        self.draw_tower_details(surface, selected_grid_tower, cash)
