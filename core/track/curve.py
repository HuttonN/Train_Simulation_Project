import pygame
import math
from utils.geometry import quadratic_bezier, bezier_derivative, distance, bezier_speed, simpson_integral

class CurvedTrack(pygame.sprite.Sprite):
    """
    Represents a curved track between any two grid cell centers, with
    robust constant-speed arc-length parameterization (Simpson + Newton).
    """

    def __init__(self, grid, start_row, start_col, control_row, control_col, end_row, end_col, track_id=None, branch="1"):
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

        # Pixel coordinates of curve points
        self.x0, self.y0 = self.grid.grid_to_screen(start_row, start_col)
        self.x1, self.y1 = self.grid.grid_to_screen(control_row, control_col)
        self.x2, self.y2 = self.grid.grid_to_screen(end_row, end_col)

        # Compute total arc length using Simpson's rule
        self.curve_length = self._total_arc_length()

        # Optionally: precompute a table of evenly-spaced t values for lightning-fast animation
        self.even_t_table = self._build_even_length_table(n_samples=150)

    def _curve_points(self):
        return (self.x0, self.y0), (self.x1, self.y1), (self.x2, self.y2)

    def _bezier_speed(self, t):
        p0, p1, p2 = self._curve_points()
        return bezier_speed(t, p0, p1, p2)

    def _total_arc_length(self):
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

    def draw_track(self, surface, color=(200,180,60), n_points=50):
        points = [quadratic_bezier(t/(n_points-1), (self.x0, self.y0), (self.x1, self.y1), (self.x2, self.y2)) for t in range(n_points)]
        pygame.draw.lines(surface, color, False, points, 5)
