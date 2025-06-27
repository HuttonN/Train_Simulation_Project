import pygame
import math

from core.track.base import BaseTrack

from utils.geometry import quadratic_bezier, bezier_derivative, bezier_speed
from utils.numerics import simpson_integral

class CurvedTrack(BaseTrack):
    """
    Represents a quadratic Bezier curve between two endpoints, with control point.
    Endpoints are labeled 'A' (start) and 'C' (end).
    """

    ENDPOINTS = ["A", "C"]

    #region --- Constructor ---------------------------------------------------------
    
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
        self.xA, self.yA = self.grid.grid_to_screen(start_row, start_col)
        self.xCtrl, self.yCtrl = self.grid.grid_to_screen(control_row, control_col)
        self.xC, self.yC = self.grid.grid_to_screen(end_row, end_col)

        # Endpoint maps
        self.endpoint_coords = {
            "A": (self.xA, self.yA),
            "C": (self.xC, self.yC)
        }
        self.endpoint_grids = {
            "A": (self.start_row, self.start_col),
            "C": (self.end_row, self.end_col)
        }

        self.curve_length = self.total_arc_length()
        self.even_t_table = self.build_even_length_table(n_samples=150)

    #endregion

    #region --- Endpoint Methods ----------------------------------------------------

    def get_endpoints(self):
        """Returns endpoint labels as a class-level constant."""
        return ["A", "C"]

    def get_endpoint_coords(self, endpoint):
        """Returns pixel coordinates for the requested endpoint."""
        if endpoint == "A":
            return self.xA, self.yA
        elif endpoint == "C":
            return self.xC, self.yC
        else:
            raise ValueError("Unknown endpoint for curve track.")

    def get_endpoint_grid(self, endpoint):
        """Returns grid coordinates for the requested endpoint."""
        if endpoint == "A":
            return self.start_row, self.start_col
        elif endpoint == "C":
            return self.end_row, self.end_col
        else:
            raise ValueError("Unknown endpoint for curve track.")
        
    #endregion
        
    #region --- Geometry and Movement Methods ---------------------------------------

    def get_point_and_angle(self, t, direction="A_to_C"):
        """
        Get a point and angle along the curve at parameter t (0 ≤ t ≤ 1).

        Args:
            t: The Bezier parameter (0=start, 1=end)
            direction: "A_to_C" (default) or "C_to_A"

        Returns:
            (point, angle) where point is (x, y), angle is degrees CCW from x-axis
        """
        if direction == "C_to_A":
            t = 1 - t
        point = quadratic_bezier(t, (self.xA, self.yA), (self.xCtrl, self.yCtrl), (self.xC, self.yC))
        dx, dy = bezier_derivative(t, (self.xA, self.yA), (self.xCtrl, self.yCtrl), (self.xC, self.yC))
        if direction == "C_to_A":
            dx, dy = -dx, -dy
        angle = math.degrees(math.atan2(dy, dx))
        return point, angle
    
    def get_angle(self, entry_ep, exit_ep):
        """
        Returns angle of travel when moving from entry_ep to exit_ep at the start of the curve.
        """
        direction = "A_to_C" if (entry_ep == "A" and exit_ep == "C") else "C_to_A"
        dx, dy = bezier_derivative(0.0, (self.xA, self.yA), (self.xCtrl, self.yCtrl), (self.xC, self.yC))
        if direction == "C_to_A":
            dx, dy = -dx, -dy
        return math.degrees(math.atan2(dy, dx))
            
    def move_along_segment(self, train, speed, entry_ep, exit_ep):
        """
        Moves the train along the curved track segment based on its current progress.

        This method is called on each update tick while the train is on this track.
        It advances the train's arc length parameter (s), converts it to the corresponding
        Bezier parameter (t), and updates the train's position and angle accordingly.

        Arguments:
            train: The train object moving along this segment.
            speed: The number of pixels the train should travel this tick.
            entry_ep: The endpoint the train entered from ("A" or "C").
            exit_ep: The endpoint the train is heading toward ("A" or "C").

        Notes:
            - The train uses arc length (not parameter t) for uniform motion.
            - The direction is inferred from the entry/exit endpoints.
            - Updates train.x, train.y, train.angle, and train.grid position.
        """
        direction = "A_to_C" if (entry_ep == "A" and exit_ep == "C") else "C_to_A"
        if direction == "A_to_C":
            train.s_on_curve = min(train.s_on_curve + speed, self.curve_length)
        else:
            train.s_on_curve = max(train.s_on_curve - speed, 0)
        t = self.arc_length_to_t(train.s_on_curve)
        (train.x, train.y), train.angle = self.get_point_and_angle(t, direction=direction)

        if direction == "A_to_C" and train.s_on_curve >= self.curve_length:
            train.row, train.col = self.end_row, self.end_col
        elif direction == "C_to_A" and train.s_on_curve <= 0:
            train.row, train.col = self.start_row, self.start_col

    #endregion

    #region --- Arc-Length & Parameter Conversion -----------------------------------

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
    
    def arc_length_to_t(self, s, direction="A_to_C", tol=1e-5, max_iter=20):
        """
        Given arc length s, solve for t along the curve (0 to 1 for A->C, 1 to 0 for C->A).
        """
        if direction == "A_to_C":
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
        elif direction == "C_to_A":
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
            raise ValueError("direction must be 'A_to_C' or 'C_to_A'.")
        
    #endregion

    #region --- Rendering Methods ---------------------------------------------------

    def draw_track(self, surface, color=(200,180,60), n_points=50):
        """Draw the Bezier curve on the given surface"""
        points = [
            quadratic_bezier(t/(n_points-1), (self.xA, self.yA), (self.xCtrl, self.yCtrl), (self.xC, self.yC)) 
            for t in range(n_points)
        ]
        pygame.draw.lines(surface, color, False, points, 5)

    #endregion

    #region --- Private/Helper Methods ----------------------------------------------

    def curve_points(self):
        """Returns the control points as tuples."""
        return (self.xA, self.yA), (self.xCtrl, self.yCtrl), (self.xC, self.yC)

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
            t = self.arc_length_to_t(s, direction="A_to_C")
            ts.append(t)
        return ts
    
    #endregion