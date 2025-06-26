import pygame
import math
from core.track.straight import StraightTrack

class StationTrack(StraightTrack):
    PLATFORM_COLOR = (220, 170, 50)
    TEXT_COLOUR = (30, 30, 30)
    PLATFORM_WIDTH = 22
    PLATFORM_LENGTH = 100
    GAP_SIZE = 8

    def __init__(self, grid, start_row, start_col, end_row, end_col, name, passenger_count=0, track_id=None, position = True):
        super().__init__(grid, start_row, start_col, end_row, end_col, track_id=track_id or f"STN:{name}")
        self.name = name
        self.passenger_count = passenger_count
        self.position = bool(position)

        # Precompute endpoints in screen coordinates
        self.x0, self.y0 = grid.grid_to_screen(start_row, start_col)
        self.x1, self.y1 = grid.grid_to_screen(end_row, end_col)

    def draw_track(self, surface):
        super().draw_track(surface)

        # 1. Direction and perpendicular vectors
        dx = self.x1 - self.x0
        dy = self.y1 - self.y0
        length = math.hypot(dx, dy)
        if length == 0:
            return

        # Unit vectors
        ux, uy = dx / length, dy / length
        side = 1 if self.position else -1
        perp_x, perp_y = -uy * side, ux * side

        # 2. Track midpoint
        mx, my = (self.x0 + self.x1) / 2, (self.y0 + self.y1) / 2

        # 3. Move perpendicularly from midpoint by GAP_SIZE + half platform width (to ensure GAP is from track to edge)
        offset = self.GAP_SIZE + self.PLATFORM_WIDTH / 2
        px = mx + perp_x * offset
        py = my + perp_y * offset

        # 4. Create the platform surface (unrotated)
        platform_surf = pygame.Surface((self.PLATFORM_LENGTH, self.PLATFORM_WIDTH), pygame.SRCALPHA)
        pygame.draw.rect(platform_surf, self.PLATFORM_COLOR, (0, 0, self.PLATFORM_LENGTH, self.PLATFORM_WIDTH))

        # 5. Draw label in center
        label = f"{self.name} ({self.passenger_count})"
        font = pygame.font.SysFont(None, 16)
        text = font.render(label, True, self.TEXT_COLOUR)
        text_rect = text.get_rect(center=(self.PLATFORM_LENGTH / 2, self.PLATFORM_WIDTH / 2))
        platform_surf.blit(text, text_rect)

        # 6. Rotate platform surface to match track angle (note: negative for pygame)
        angle = math.degrees(math.atan2(dy, dx))
        rotated_surf = pygame.transform.rotate(platform_surf, -angle)

        # 7. Place rotated surface centered at (px, py)
        rotated_rect = rotated_surf.get_rect(center=(px, py))
        surface.blit(rotated_surf, rotated_rect.topleft)
