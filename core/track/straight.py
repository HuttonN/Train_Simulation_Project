import pygame
import math

class StraightTrack(pygame.sprite.Sprite):
    """
    Represents a straight track piece between any two grid cell centers.
    """

    def __init__(self, grid, start_row, start_col, end_row, end_col, track_id = None, branch="1"):
        super().__init__()
        self.grid = grid
        self.start_row = start_row
        self.start_col = start_col
        self.end_row = end_row
        self.end_col = end_col
        self.track_id = track_id or f"{start_row},{start_col}->{end_row},{end_col}"
        self.branch = branch
        
        # Get pixel coordinates of cell center
        self.x0, self.y0 = self.grid.grid_to_screen(start_row, start_col)
        self.x1, self.y1 = self.grid.grid_to_screen(end_row, end_col)

        # Store direction as an angle for the train
        self.angle = math.degrees(math.atan2(self.y1 - self.y0, self.x1 - self.x0))

    def draw_track(self, surface, color=(200, 180, 60)):
        pygame.draw.line(surface, color, (self.x0, self.y0), (self.x1, self.y1), 5)

    def get_angle(self):
        # Used for train orientation
        return self.angle