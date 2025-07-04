import pygame
import math

from core.track.base import BaseTrack
from utils.geometry import quadratic_bezier, bezier_derivative, bezier_speed
from utils.numerics import simpson_integral

class CurvedTrack(BaseTrack):
    """
    Represents a quadratic Bezier curve between two endpoints, with control point.
    ENDPOINTS:
        - "A": Start of curve.
        - "C": End of curve.
    """

    ENDPOINTS = ["A", "C"]

    #region --- Constructor ---------------------------------------------------------
    
    def __init__(self, grid, start_row, start_col, control_row, control_col, end_row, end_col, track_id, track_type):
        """
        Initialise a curved track segment.

        Arguments:
            grid: Grid object for coordinate conversion.
            start_row, start_col: Grid coordinates for endpoint "A".
            control_row, control_col: Grid coordinates for Bezier control point.
            end_row, end_col: Grid coordinates for endpoint "C".
            track_id (str, optional): Unique identifier for this track piece.
        """
    
        super().__init__(grid, track_id, track_type)
        self.grid = grid
        self.start_row = start_row
        self.start_col = start_col
        self.control_row = control_row
        self.control_col = control_col
        self.end_row = end_row
        self.end_col = end_col

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

        # Precompute arc length and even-t lookup table for uniform motion
        self.curve_length = self.total_arc_length()
        self.even_t_table = self.build_even_length_table(n_samples=150)

    #endregion
        
    #region --- Geometry and Movement Methods ---------------------------------------

    def get_length(self, entry_ep, exit_ep):
        """
        Return total arc length of this Bezier curve segment.

        Arguments:
            entry_ep (str): Start endpoint label.
            exit_ep (str): End endpoint label.
        Returns:
            float: Arc length in pixels.
        """
        # For a quadratic curve, length is the same in either direction.
        return self.curve_length
    
    def get_position_at_distance(self, entry_ep, exit_ep, s):
        """
        Return (x, y, angle) at distance s along the curve from entry_ep toward exit_ep.

        Arguments:
            entry_ep (str): Start endpoint label.
            exit_ep (str): End endpoint label.
            s (float): Distance along the curve (pixels).

        Returns:
            tuple: (x, y, angle) at the given distance.
        """
        length = self.get_length(entry_ep, exit_ep)
        direction = "A_to_C" if entry_ep == "A" and exit_ep == "C" else "C_to_A"
        # Ensure s in [0, length]
        s = max(0, min(s, length))
        t = self.arc_length_to_t(s, direction=direction)
        (x, y), angle = self.get_point_and_angle(t, direction=direction)
        return (x, y, angle)


    def get_point_and_angle(self, t, direction="A_to_C"):
        """
        Return (x, y) position and tangent angle at parameter t (0=start, 1=end).

        Arguments:
            t (float): Bezier parameter in [0, 1].
            direction (str): "A_to_C" (default) or "C_to_A" (reverse direction).

        Returns:
            tuple: ((x, y), angle in degrees).
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
        Return angle of travel at the start of the curve from entry_ep to exit_ep.

        Arguments:
            entry_ep (str): Entry endpoint label.
            exit_ep (str): Exit endpoint label.

        Returns:
            float: Angle in degrees.
        """
        direction = "A_to_C" if (entry_ep == "A" and exit_ep == "C") else "C_to_A"
        dx, dy = bezier_derivative(0.0, (self.xA, self.yA), (self.xCtrl, self.yCtrl), (self.xC, self.yC))
        if direction == "C_to_A":
            dx, dy = -dx, -dy
        return math.degrees(math.atan2(dy, dx))
            
    def move_along_segment(self, train, speed, entry_ep, exit_ep):
        """
        Advance the train along the Bezier curve based on current progress and speed.

        Arguments:
            train: Train object being moved (should track s_on_curve).
            speed (float): Distance to move (pixels).
            entry_ep (str): Endpoint train entered from ("A" or "C").
            exit_ep (str): Endpoint train is heading toward ("A" or "C").
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

    def has_reached_endpoint(self, train, exit_ep):
        """
        Check if the train has reached the end of the curve in the current direction.

        Arguments:
            train: Train object (should track s_on_curve and entry_ep).
            exit_ep (str): Endpoint label being checked.

        Returns:
            bool: True if train has reached the exit endpoint.
        """
        # We use s_on_curve and the direction
        if train.entry_ep == "A":
            return train.s_on_curve >= self.curve_length
        else:
            return train.s_on_curve <= 0

    #endregion

    #region --- Arc-Length & Parameter Conversion -----------------------------------

    def total_arc_length(self):
        """
        Compute the total arc length of the Bezier curve.
        """
        p0, p1, p2 = self.curve_points()
        f = lambda t: bezier_speed(t, p0, p1, p2)
        return simpson_integral(f, 0, 1, n=64)

    def arc_length_up_to_t(self, t):
        """
        Compute arc length from t=0 up to t (for arc length <-> parameter conversion).
        """
        p0, p1, p2 = self.curve_points()
        f = lambda u: bezier_speed(u, p0, p1, p2)
        return simpson_integral(f, 0, t, n=32)
    
    def arc_length_to_t(self, s, direction="A_to_C", tol=1e-5, max_iter=20):
        """
        Convert arc length s to the corresponding Bezier parameter t.

        Arguments:
            s (float): Distance along the curve.
            direction (str): "A_to_C" or "C_to_A".
            tol (float): Tolerance for iterative solver.
            max_iter (int): Maximum iterations.

        Returns:
            float: Bezier parameter t in [0, 1].
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
        """
        Precompute a lookup table to map uniform arc length to parameter t for even movement.

        Arguments:
            n_samples (int): Number of table entries.

        Returns:
            list: Lookup table of t values corresponding to evenly spaced arc lengths.
        """
        ts = []
        L = self.curve_length
        for i in range(n_samples + 1):
            s = L * i / n_samples
            t = self.arc_length_to_t(s, direction="A_to_C")
            ts.append(t)
        return ts
    
    #endregion
