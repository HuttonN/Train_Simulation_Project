import pygame
import math

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

        def quadratic_bezier(t, p0, p1, p2):
            """Return the (x,y) point on a quadratic bezier curve for parameter t"""
            return (
                ((1-t)**2)*p0[0] + 2*(1-t)*t*p1[0] + (t**2)*p2[0],
                ((1-t)**2)*p0[1] + 2*(1-t)*t*p1[1] + (t**2)*p2[1]
            )
        
        def bezier_derivative(t, p0, p1, p2):
            dx = 2*(1-t)*(p1[0] - p0[0]) + 2*t*(p2[0] - p1[0])
            dy = 2*(1-t)*(p1[1] - p0[1]) + 2*t*(p2[1] - p1[1])
            return dx, dy