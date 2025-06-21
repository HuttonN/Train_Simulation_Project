import pygame
import math

from utils.bezier import quadratic_bezier, bezier_derivative

class CurvedTrack(pygame.sprite.Sprite):
    """
    Represents a curved track between ant two grid cell centers
    """

    def __init__(self, grid, start_row, start_col, control_row, control_col, end_row, end_col, track_id = None, branch="1"):
        super().__init__()
        self.grid = grid
        self.start_row = start_row
        self.start_col = start_col
        self.control_row = control_row
        self.control_col = control_col
        self.end_row = end_row
        self.end_col = end_col
        self.track_id = track_id or f"curve{start_row},{start_col}->{end_row},{end_col}"
        self.branch = branch

        # Get pixel coordinates of cell center
        self.x0, self.y0 = self.grid.grid_to_screen(start_row, start_col)
        self.x1, self.y1 = self.grid.grid_to_screen(control_row, control_col)
        self.x2, self.y2 = self.grid.grid_to_screen(end_row, end_col)
    
    def draw_track(self, surface, color=(200,180,60), t=50):
        steps = [p/(t-1) for p in range(t)]
        points = []
        for step in steps:
            point = quadratic_bezier(step, (self.x0, self.y0), (self.x1, self.y1), (self.x2, self.y2))
            points.append(point)
        pygame.draw.lines(surface, color, False, points, 5)
