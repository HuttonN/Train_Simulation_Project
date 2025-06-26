import pygame
import math

from core.track.base import BaseTrack

from utils.geometry import quadratic_bezier, bezier_derivative, bezier_speed
from utils.numerics import simpson_integral

class CurvedTrack(BaseTrack):
    """
    Represents a quadratic Bezier curve between two endpoints, with control point.
    Endpoints are labeled 'A' (start) and 'B' (end).
    """

    ENDPOINTS = ["A", "B"]

    # --- Constructor ---------------------------------------------------------
    
    def __init__(self, grid, start_row, start_col, control_row, control_col, end_row, end_col, track_id = None):
        super().__init__()
        self.grid = grid
        self.start_row = start_row
        self.start_col = start_col
        self.control_row = control_row
        self.control_col = control_col
        self.end_row = end_row
        self.end_col = end_col
        self.track_id = track_id or f"curve{start_row},{start_col}->{end_row},{end_col}"

        # Pixel coordinates
        self.x0, self.y0 = self.grid.grid_to_screen(start_row, start_col)
        self.x1, self.y1 = self.grid.grid_to_screen(control_row, control_col)
        self.x2, self.y2 = self.grid.grid_to_screen(end_row, end_col)

        # Endpoint maps
        self.endpoint_coords = {
            "A": (self.x0, self.y0),
            "B": (self.x2, self.y2)
        }
        self.endpoint_grids = {
            "A": (self.start_row, self.start_col),
            "B": (self.end_row, self.end_col)
        }

        self.curve_length = self.total_arc_length()
        self.even_t_table = self.build_even_length_table(n_samples=150)

    # --- Endpoint Methods ----------------------------------------------------

    def get_endpoints(self):
        """Returns endpoint labels as a class-level constant."""
        return ["A", "B"]

    def get_endpoint_coords(self, endpoint):
        """Returns pixel coordinates for the requested endpoint."""
        if endpoint == "A":
            return self.x0, self.y0
        elif endpoint == "B":
            return self.x2, self.y2
        else:
            raise ValueError("Unknown endpoint for curve track.")

    def get_endpoint_grid(self, endpoint):
        """Returns grid coordinates for the requested endpoint."""
        if endpoint == "A":
            return self.start_row, self.start_col
        elif endpoint == "B":
            return self.end_row, self.end_col
        else:
            raise ValueError("Unknown endpoint for curve track.")
        
    # --- Geometry and Movement Methods ---------------------------------------

    def get_point_and_angle(self, t, direction="A_to_B"):
        """
        Get a point and angle along the curve at parameter t (0 ≤ t ≤ 1).

        Args:
            t: The Bezier parameter (0=start, 1=end)
            direction: "A_to_B" (default) or "B_to_A"

        Returns:
            (point, angle) where point is (x, y), angle is degrees CCW from x-axis
        """
        if direction == "B_to_A":
            t = 1 - t
        point = quadratic_bezier(t, (self.x0, self.y0), (self.x1, self.y1), (self.x2, self.y2))
        dx, dy = bezier_derivative(t, (self.x0, self.y0), (self.x1, self.y1), (self.x2, self.y2))
        if direction == "B_to_A":
            dx, dy = -dx, -dy
        angle = math.degrees(math.atan2(dy, dx))
        return point, angle
    
    def get_angle(self, entry_ep, exit_ep):
        """
        Returns angle of travel when moving from entry_ep to exit_ep at the start of the curve.
        """
        direction = "A_to_B" if (entry_ep == "A" and exit_ep == "B") else "B_to_A"
        dx, dy = bezier_derivative(0.0, (self.x0, self.y0), (self.x1, self.y1), (self.x2, self.y2))
        if direction == "B_to_A":
            dx, dy = -dx, -dy
        return math.degrees(math.atan2(dy, dx))
    
    def total_arc_length(self):
        """
        Computes total arc length of the Bezier curve.
        """
        p0, p1, p2 = self.curve_points()
        f = lambda t: bezier_speed(t, p0, p1, p2)
        return simpson_integral(f, 0, 1, n=64)

    def arc_length_up_to_t(self, t):
        """
        Computes arc length from t=0 up to t.
        """
        p0, p1, p2 = self.curve_points()
        f = lambda u: bezier_speed(u, p0, p1, p2)
        return simpson_integral(f, 0, t, n=32)
    
    def arc_length_to_t(self, s, direction="A_to_B", tol=1e-5, max_iter=20):
        """
        Given arc length s, solve for t along the curve (0 to 1 for A->B, 1 to 0 for B->A).
        """
        if direction == "A_to_B":
            if s <= 0:
                return 0.0
            if s >= self.curve_length:
                return 1.0
            t = s / self.curve_length  # Initial guess
            for _ in range(max_iter):
                L = self.arc_length_up_to_t(t)
                speed = self.bezier_speed(t)
                if speed == 0:
                    break
                t_new = t - (L - s) / speed
                if abs(t_new - t) < tol:
                    return min(max(t_new, 0), 1)
                t = min(max(t_new, 0), 1)
            return t
        elif direction == "B_to_A":
            if s <= 0:
                return 1.0
            if s >= self.curve_length:
                return 0.0
            t = 1.0 - (s / self.curve_length)  # Initial guess
            for _ in range(max_iter):
                L = self.arc_length_up_to_t(t)
                speed = self.bezier_speed(t)
                if speed == 0:
                    break
                t_new = t - (self.curve_length - L - s) / (-speed)
                if abs(t_new - t) < tol:
                    return min(max(t_new, 0), 1)
                t = min(max(t_new, 0), 1)
            return t
        else:
            raise ValueError("direction must be 'A_to_B' or 'B_to_A'.")
        
    def move_along_segment(self, train, speed, entry_ep, exit_ep):
        direction = "A_to_B" if (entry_ep == "A" and exit_ep == "B") else "B_to_A"
        if direction == "A_to_B":
            train.s_on_curve = min(train.s_on_curve + speed, self.curve_length)
        else:
            train.s_on_curve = max(train.s_on_curve - speed, 0)
        t = self.arc_length_to_t(train.s_on_curve)
        (train.x, train.y), train.angle = self.get_point_and_angle(t, direction=direction)

        if direction == "A_to_B" and train.s_on_curve >= self.curve_length:
            train.row, train.col = self.end_row, self.end_col
        elif direction == "B_to_A" and train.s_on_curve <= 0:
            train.row, train.col = self.start_row, self.start_col

    # --- Rendering Methods ---------------------------------------------------

    def draw_track(self, surface, color=(200,180,60), n_points=50):
        """Draw the Bezier curve on the given surface"""
        points = [
            quadratic_bezier(t/(n_points-1), (self.x0, self.y0), (self.x1, self.y1), (self.x2, self.y2)) 
            for t in range(n_points)
        ]
        pygame.draw.lines(surface, color, False, points, 5)

    # --- Private/Helper Methods ---------------------------------------------------

    def curve_points(self):
        """Returns the control points as tuples."""
        return (self.x0, self.y0), (self.x1, self.y1), (self.x2, self.y2)

    def bezier_speed(self, t):
        """Returns the speed along the Bezier curve at parameter t."""
        p0, p1, p2 = self.curve_points()
        return bezier_speed(t, p0, p1, p2)
    
    def build_even_length_table(self, n_samples=150):
        """Precomputes a lookup table to map uniform arc length to parameter t for even movement."""
        ts = []
        L = self.curve_length
        for i in range(n_samples + 1):
            s = L * i / n_samples
            t = self.arc_length_to_t(s, direction="A_to_B")
            ts.append(t)
        return ts