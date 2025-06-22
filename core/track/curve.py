import pygame
import math

from utils.geometry import quadratic_bezier, bezier_derivative, distance

class CurvedTrack(pygame.sprite.Sprite):
    """
    Represents a curved track between any two grid cell centers
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

        # Arc-length table
        self.arc_table, self.curve_length = self.compute_arc_length_table(n=800)

    def compute_arc_length_table(self, n =800):
        # Sample n ponts along bezier curve, computes distances
        points = [quadratic_bezier(t/(n-1), (self.x0, self.y0), (self.x1, self.y1), (self.x2, self.y2)) for t in range(n)]
        arc_lengths = [0]
        total = 0
        for i in range(1, len(points)):
            seg = distance(points[i-1], points[i])
            total += seg
            arc_lengths.append(total)
        ts = [i / (n-1) for i in range(n)]
        return list(zip(ts, arc_lengths)), total
    
    def arc_length_to_t(self, s):
        """Given arc length s, return the corresponding t"""
        if s <= 0:
            return 0
        if s >= self.curve_length:
            return 1
        table = self.arc_table
        for i in range(1, len(table)):
            if table[i][1] >= s:
                t0, s0 = table[i-1]
                t1, s1 = table[i]
                if s1 != s0:
                    t = t0 + (s-s0) * ((t1-t0) / (s1-s0))
                else:
                    t = t0
                return t
        return table [-1][0]
    
    def get_point_and_angle(self, t):
        point = quadratic_bezier(t, (self.x0, self.y0), (self.x1, self.y1), (self.x2, self.y2))
        dx, dy = bezier_derivative(t, (self.x0, self.y0), (self.x1, self.y1), (self.x2, self.y2))
        angle = math.degrees(math.atan2(dy, dx))
        return point, angle
    
    def get_angle(self):
        dx, dy = bezier_derivative(0.0, (self.x0, self.y0), (self.x1, self.y1), (self.x2, self.y2))
        return math.degrees(math.atan2(dy, dx))
    
    def draw_track(self, surface, color=(200,180,60), n_points=50):
        points = [quadratic_bezier(t/(n_points-1), (self.x0, self.y0), (self.x1, self.y1), (self.x2, self.y2)) for t in range(n_points)]
        pygame.draw.lines(surface, color, False, points, 5)