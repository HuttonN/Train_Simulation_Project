import pygame
from core.track.straight import StraightTrack

class StationTrack(StraightTrack):
    PLATFORM_COLOR = (220, 170, 50)
    TEXT_COLOUR = (30, 30, 30)
    PLATFORM_WIDTH = 22

    def __init__(self, grid, start_row, start_col, end_row, end_col, name, passenger_count = 0, track_id = None, branch ="1"):
        super().__init__(grid, start_row, start_col, end_row, end_col, track_id=track_id or f"STN:{name}", branch=branch)
        self.name = name
        self.passenger_count = passenger_count

        pad = 4
        x_min = min(self.x0, self.x1) - pad
        y_min = min(self.y0, self.y1) - pad
        w = abs(self.x1 - self.x0) + pad * 2
        h = abs(self.y1 - self.y0) + pad * 2
        self.bounds = pygame.Rect(x_min, y_min, w , h)

    def draw_track(self, surface):
        super().draw_track(surface)
        
        pygame.draw.rect(surface, self.PLATFORM_COLOR, self.bounds)

        label = f"{self.name} ({self.passenger_count})"
        text = pygame.font.SysFont(None, 16).render(label, True, self.TEXT_COLOUR)
        text_rect = text.get_rect(center=self.bounds.center)
        surface.blit(text, text_rect)
    
