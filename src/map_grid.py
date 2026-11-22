"""
Battlefield map, grid coordinates, path finding, and tile validation.
"""

import pygame
from src.config import (
    GRID_SIZE, GRID_COLS, GRID_ROWS,
    COLOR_BG, COLOR_GRID_LINE, COLOR_PATH, COLOR_PATH_BORDER
)


class MapGrid:
    def __init__(self):
        self.cols = GRID_COLS
        self.rows = GRID_ROWS
        self.grid_size = GRID_SIZE

        # Tactical S-curve military supply route waypoints in grid (col, row)
        self.grid_waypoints = [
            (0, 3),
            (6, 3),
            (6, 8),
            (12, 8),
            (12, 4),
            (18, 4),
            (18, 14),
            (8, 14),
            (8, 11),
            (2, 11),
            (2, 16),
            (23, 16)
        ]

        # Convert to pixel centers
        self.pixel_waypoints = [
            (col * self.grid_size + self.grid_size // 2, row * self.grid_size + self.grid_size // 2)
            for (col, row) in self.grid_waypoints
        ]

        # Determine all path tiles
        self.path_tiles = set()
        for i in range(len(self.grid_waypoints) - 1):
            c1, r1 = self.grid_waypoints[i]
            c2, r2 = self.grid_waypoints[i + 1]

            step_c = 1 if c2 >= c1 else -1
            step_r = 1 if r2 >= r1 else -1

            if c1 == c2:
                for r in range(r1, r2 + step_r, step_r):
                    self.path_tiles.add((c1, r))
            elif r1 == r2:
                for c in range(c1, c2 + step_c, step_c):
                    self.path_tiles.add((c, r1))

        # Placed towers lookup: (col, row) -> Tower instance
        self.towers = {}

    def is_tile_buildable(self, col, row):
        """Returns True if the tile is within bounds, not on path, and has no tower."""
        if not (0 <= col < self.cols and 0 <= row < self.rows):
            return False
        if (col, row) in self.path_tiles:
            return False
        if (col, row) in self.towers:
            return False
        return True

    def get_grid_pos(self, pixel_x, pixel_y):
        """Converts mouse screen coordinates to grid (col, row). Returns None if outside battlefield."""
        if pixel_x < 0 or pixel_x >= self.cols * self.grid_size or pixel_y < 0 or pixel_y >= self.rows * self.grid_size:
            return None
        return (pixel_x // self.grid_size, pixel_y // self.grid_size)

    def get_center_pixel(self, col, row):
        return (col * self.grid_size + self.grid_size // 2, row * self.grid_size + self.grid_size // 2)

    def draw(self, surface):
        battlefield_rect = pygame.Rect(0, 0, self.cols * self.grid_size, self.rows * self.grid_size)
        pygame.draw.rect(surface, COLOR_BG, battlefield_rect)

        # Draw path tiles
        for (col, row) in self.path_tiles:
            rect = pygame.Rect(col * self.grid_size, row * self.grid_size, self.grid_size, self.grid_size)
            pygame.draw.rect(surface, COLOR_PATH, rect)

        # Draw path borders & lane centerline
        for (col, row) in self.path_tiles:
            px = col * self.grid_size
            py = row * self.grid_size
            # Neighbor checks to draw subtle border
            for dc, dr, x1, y1, x2, y2 in [
                (0, -1, px, py, px + self.grid_size, py),
                (0, 1, px, py + self.grid_size, px + self.grid_size, py + self.grid_size),
                (-1, 0, px, py, px, py + self.grid_size),
                (1, 0, px + self.grid_size, py, px + self.grid_size, py + self.grid_size)
            ]:
                if (col + dc, row + dr) not in self.path_tiles:
                    pygame.draw.line(surface, COLOR_PATH_BORDER, (x1, y1), (x2, y2), 2)

        # Draw path direction guideline / runway dashed line
        if len(self.pixel_waypoints) > 1:
            pygame.draw.lines(surface, (60, 68, 72), False, self.pixel_waypoints, 2)

        # Draw battlefield subtle grid
        for c in range(self.cols + 1):
            x = c * self.grid_size
            pygame.draw.line(surface, COLOR_GRID_LINE, (x, 0), (x, self.rows * self.grid_size), 1)
        for r in range(self.rows + 1):
            y = r * self.grid_size
            pygame.draw.line(surface, COLOR_GRID_LINE, (0, y), (self.cols * self.grid_size, y), 1)

        # Draw Base / Exit indicator
        end_px, end_py = self.pixel_waypoints[-1]
        pygame.draw.circle(surface, (200, 40, 40), (end_px, end_py), self.grid_size // 2, 3)
        # Draw Spawn indicator
        start_px, start_py = self.pixel_waypoints[0]
        pygame.draw.circle(surface, (60, 180, 100), (start_px, start_py), self.grid_size // 2, 3)
