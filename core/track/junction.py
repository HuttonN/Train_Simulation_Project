import pygame
import math

from utils.geometry import quadratic_bezier, bezier_derivative, distance, bezier_speed
from utils.numerics import simpson_integral

class JunctionTrack(pygame.sprite.Sprite):
    """
    Represents a simple junction with a main (straight) branch and a diverging (left or right) branch.
    """

    def __init__(self, grid, start_row, start_col, straight_end_row, straight_end_col, curve_control_row, curve_control_col, curve_end_row, curve_end_col, track_id="None", branch_activated = False):
        super().__init__()
        self.grid = grid
        self.start_row = start_row
        self.start_col = start_col
        self.straight_end_row = straight_end_row
        self.straight_end_col = straight_end_col
        self.curve_control_row = curve_control_row
        self.curve_control_col = curve_control_col
        self.curve_end_row = curve_end_row
        self.curve_end_col = curve_end_col
        self.track_id = track_id or f"curve{start_row},{start_col}->{straight_end_row},{straight_end_col}or{curve_end_row}, {curve_end_col}"
        self.branch_activated = branch_activated

        # Pixel coordinates of straight points
        self.x0, self.y0 = self.grid.grid_to_screen(start_row, start_col)
        self.x1, self.y1 = self.grid.grid_to_screen(straight_end_row, straight_end_col)

        # Pixel coordinates of curve points
        self.x2, self.y2 = self.grid.grid_to_screen(curve_control_row, curve_control_col)
        self.x3, self.y3 = self.grid.grid_to_screen(curve_end_row, curve_end_col)

        # Compute total arc length using Simpson's rule
        self.curve_length = self.total_arc_length()

        # Optionally: precompute a table of evenly-spaced t values for lightning-fast animation
        self.even_t_table = self._build_even_length_table(n_samples=150)

    def _curve_points(self):
        return (self.x0, self.y0), (self.x2, self.y2), (self.x3, self.y3)
    
    def _bezier_speed(self, t):
        p0, p1, p2 = self._curve_points()
        return bezier_speed(t, p0, p1, p2)

    def total_arc_length(self):
        # Accurate curve length via Simpson's rule
        p0, p1, p2 = self._curve_points()
        f = lambda t: bezier_speed(t, p0, p1, p2)
        return simpson_integral(f, 0, 1, n=64)
    
    def arc_length_up_to_t(self, t):
        # Returns arc length from t=0 to t (again via Simpson)
        p0, p1, p2 = self._curve_points()
        f = lambda u: bezier_speed(u, p0, p1, p2)
        return simpson_integral(f, 0, t, n=32)
    
    def arc_length_to_t(self, s, tol=1e-5, max_iter=20):
        """
        Given arc length s, numerically solve for t so that arc length from 0 to t is s.
        Uses Newton–Raphson for robust, smooth mapping even for difficult curves.
        """
        if s <= 0:
            return 0.0
        if s >= self.curve_length:
            return 1.0

        t = s / self.curve_length  # Initial guess
        for _ in range(max_iter):
            L = self.arc_length_up_to_t(t)
            speed = self._bezier_speed(t)
            if speed == 0:
                break
            t_new = t - (L - s) / speed
            if abs(t_new - t) < tol:
                return min(max(t_new, 0), 1)
            t = min(max(t_new, 0), 1)
        return t

    def _build_even_length_table(self, n_samples=150):
        """
        Precompute a list of t values corresponding to evenly-spaced distances along the curve.
        (Optional, but useful for fast lookup and uniform train stepping.)
        """
        ts = []
        L = self.curve_length
        for i in range(n_samples + 1):
            s = L * i / n_samples
            t = self.arc_length_to_t(s)
            ts.append(t)
        return ts
    
    def get_point_and_angle(self, t):
        point = quadratic_bezier(t, (self.x0, self.y0), (self.x1, self.y1), (self.x2, self.y2))
        dx, dy = bezier_derivative(t, (self.x0, self.y0), (self.x1, self.y1), (self.x2, self.y2))
        angle = math.degrees(math.atan2(dy, dx))
        return point, angle

    def get_angle(self):
        dx, dy = bezier_derivative(0.0, (self.x0, self.y0), (self.x1, self.y1), (self.x2, self.y2))
        return math.degrees(math.atan2(dy, dx))

    def draw_track(self, surface, activated_color=(200, 180, 60), non_activated_color=(255, 0, 0), n_curve_points=50):
        points = [quadratic_bezier(t/(n_curve_points-1), (self.x0, self.y0), (self.x2, self.y2), (self.x3, self.y3)) for t in range(n_curve_points)]
        if self.branch_activated:
            pygame.draw.lines(surface, activated_color, False, points, 5)
            pygame.draw.line(surface, non_activated_color, (self.x0, self.y0), (self.x1, self.y1), 5)
        else:
            pygame.draw.lines(surface, non_activated_color, False, points, 5)
            pygame.draw.line(surface, activated_color, (self.x0, self.y0), (self.x1, self.y1), 5)



