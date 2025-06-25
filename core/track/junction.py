import pygame
import math

from core.track.base import BaseTrack

from utils.geometry import quadratic_bezier, bezier_derivative, bezier_speed
from utils.numerics import simpson_integral

class JunctionTrack(BaseTrack):
    """
    Represents a simple junction with a main (straight) branch and a diverging (left or right) branch.
    Endpoints: 'A' (start), 'S' (straight end), 'C' (curve end).
    """

    ENDPOINTS = ["A", "S", "C"]

    # --- Constructor ---------------------------------------------------------

    def __init__(
            self, grid, 
            start_row, start_col, 
            straight_end_row, straight_end_col, 
            curve_control_row, curve_control_col, 
            curve_end_row, curve_end_col, 
            track_id="None", 
            branch_activated = False
        ):
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
        self.track_id = (
            track_id or 
            f"junction{start_row},{start_col}->{straight_end_row},{straight_end_col}or{curve_end_row}, {curve_end_col}"
        )
        self.branch_activated = branch_activated

        # Pixel coordinates of cell centers
        self.xA, self.yA = self.grid.grid_to_screen(start_row, start_col)
        self.xS, self.yS = self.grid.grid_to_screen(straight_end_row, straight_end_col)
        self.xCtrl, self.yCtrl = self.grid.grid_to_screen(curve_control_row, curve_control_col)
        self.xC, self.yC = self.grid.grid_to_screen(curve_end_row, curve_end_col)

        # Endpoint maps
        self._endpoint_coords = {
            "A": (self.xA, self.yA),
            "S": (self.xS, self.yS),
            "C": (self.xC, self.yC)
        }
        self._endpoint_grids = {
            "A": (self.start_row, self.start_col),
            "S": (self.straight_end_row, self.straight_end_col),
            "C": (self.curve_end_row, self.curve_end_col)
        }

        # Compute total arc length using Simpson's rule
        self.curve_length = self.total_arc_length()
        self.even_t_table = self.build_even_length_table(n_samples=150)

        # Precompute straight angle
        self.straight_angle = math.degrees(math.atan2(self.yS - self.yA, self.xS - self.xA))

    # --- Endpoint Methods ----------------------------------------------------

    def get_endpoints(self):
        return ["A", "S", "C"]
    
    def get_endpoint_coords(self, ep):
        """Returns pixel coordinates for the requested endpoint."""
        if ep == "A":
            return self.xA, self.yA
        elif ep == "S":
            return self.xS, self.yS
        elif ep == "C":
            return self.xC, self.yC
        else:
            raise ValueError("Unknown endpoint: " + ep)
        
    def get_endpoint_grid(self, ep):
        """Returns grid coordinates for the requested endpoint."""
        if ep == "A":
            return self.start_row, self.start_col
        elif ep == "S":
            return self.straight_end_row, self.straight_end_col
        elif ep == "C":
            return self.curve_end_row, self.curve_end_col
        else:
            raise ValueError("Unknown endpoint: " + ep)
        
    # --- Geometry and Movement Methods ---------------------------------------
        
    def get_angle(self, entry_ep, exit_ep):
        """Returns the angle of travel for a movement from entry_ep to exit_ep."""
        if {entry_ep, exit_ep} == {"A", "S"}:
            # Forward: A->S (t=0), Reverse: S->A (t=1)
            if entry_ep == "A":
                return self.straight_angle
            else:
                return (self.straight_angle + 180) % 360
        elif {entry_ep, exit_ep} == {"A", "C"}:
            # For curve, angle at t=0 if from A->C, at t=1 if from C->A
            t = 0.0 if entry_ep == "A" else 1.0
            dx, dy = bezier_derivative(
                t,
                (self.xA, self.yA),
                (self.xCtrl, self.yCtrl),
                (self.xC, self.yC)
            )
            if entry_ep == "C":
                dx, dy = -dx, -dy
            return math.degrees(math.atan2(dy, dx))
        else:
            # Not a direct segment: return angle towards A
            x_from, y_from = self.get_endpoint_coords(entry_ep)
            x_to, y_to = self.get_endpoint_coords(exit_ep)
            return math.degrees(math.atan2(y_to - y_from, x_to - x_from))
        
    def get_curve_point_and_angle(self, t, direction="A_to_C"):
        """Returns a point and angle on the curve at parameter t (0 ≤ t ≤ 1)."""
        if direction == "C_to_A":
            t = 1 - t
        point = quadratic_bezier(t, (self.xA, self.yA), (self.xCtrl, self.yCtrl), (self.xC, self.yC))
        dx, dy = bezier_derivative(t, (self.xA, self.yA), (self.xCtrl, self.yCtrl), (self.xC, self.yC))
        if direction == "C_to_A":
            dx, dy = -dx, -dy
        angle = math.degrees(math.atan2(dy, dx))
        return point, angle
    
    def move_along_segment(self, train, speed, entry_ep, exit_ep):
        """
        Moves the train along the segment between the given endpoints.
        (Consistent API with StraightTrack/CurvedTrack)
        """
        if {entry_ep, exit_ep} == {"A", "S"}:
            # Straight movement
            if entry_ep == "A":
                # Forward
                target_x, target_y = self.xS, self.yS
                target_grid = (self.straight_end_row, self.straight_end_col)
            else:
                # Reverse
                target_x, target_y = self.xA, self.yA
                target_grid = (self.start_row, self.start_col)
            dx = target_x - train.x
            dy = target_y - train.y
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist > speed:
                train.x += dx / dist * speed
                train.y += dy / dist * speed
            else:
                train.x, train.y = target_x, target_y
                train.row, train.col = target_grid
        elif {entry_ep, exit_ep} == {"A", "C"}:
            # Curve movement
            if entry_ep == "A":
                train.s_on_curve = min(train.s_on_curve + speed, self.curve_length)
                t = self.arc_length_to_t(train.s_on_curve, direction="A_to_C")
                (train.x, train.y), train.angle = self.get_curve_point_and_angle(t, direction="A_to_C")
                if train.s_on_curve >= self.curve_length:
                    train.row, train.col = self.curve_end_row, self.curve_end_col
            else:
                train.s_on_curve = max(train.s_on_curve - speed, 0)
                t = self.arc_length_to_t(train.s_on_curve, direction="C_to_A")
                (train.x, train.y), train.angle = self.get_curve_point_and_angle(t, direction="C_to_A")
                if train.s_on_curve <= 0:
                    train.row, train.col = self.start_row, self.start_col
        else:
            # Fallback for other endpoint pairs (e.g. S <-> C): just jump
            # In future, handle as two-segment traversal via "A"
            target_x, target_y = self.get_endpoint_coords(exit_ep)
            target_grid = self.get_endpoint_grid(exit_ep)
            dx = target_x - train.x
            dy = target_y - train.y
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist > speed:
                train.x += dx / dist * speed
                train.y += dy / dist * speed
            else:
                train.x, train.y = target_x, target_y
                train.row, train.col = target_grid

    # --- Curve Length/Arc Methods --------------------------------------------

    def curve_points(self):
        """Returns the control points as tuples for the curve."""
        return (self.xA, self.yA), (self.xCtrl, self.yCtrl), (self.xC, self.yC)

    def bezier_speed(self, t):
        """Returns the speed along the Bezier curve at parameter t."""
        p0, p1, p2 = self.curve_points()
        return bezier_speed(t, p0, p1, p2)

    def total_arc_length(self):
        # Accurate curve length via Simpson's rule
        p0, p1, p2 = self.curve_points()
        f = lambda t: bezier_speed(t, p0, p1, p2)
        return simpson_integral(f, 0, 1, n=64)
    
    def arc_length_up_to_t(self, t):
        # Returns arc length from t=0 to t (again via Simpson)
        p0, p1, p2 = self.curve_points()
        f = lambda u: bezier_speed(u, p0, p1, p2)
        return simpson_integral(f, 0, t, n=32)
    
    def arc_length_to_t(self, s, direction="A_to_C", tol=1e-5, max_iter=20):
        """Given arc length s, solve for t along the curve (0 to 1 for A->C, 1 to 0 for C->A)."""
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

    def build_even_length_table(self, n_samples=150):
        """Precompute a list of t values corresponding to evenly-spaced distances along the curve."""
        ts = []
        L = self.curve_length
        for i in range(n_samples + 1):
            s = L * i / n_samples
            t = self.arc_length_to_t(s, direction="A_to_C")
            ts.append(t)
        return ts
    
    # --- Rendering Methods ---------------------------------------------------

    def draw_track(self, surface, activated_color=(200, 180, 60), non_activated_color=(255, 0, 0), n_curve_points=50):
        """Draws the curve and straight, highlighting the active branch."""
        curve_points = [quadratic_bezier(
            t/(n_curve_points-1),
            (self.xA, self.yA), (self.xCtrl, self.yCtrl), (self.xC, self.yC)
        ) for t in range(n_curve_points)]
        if self.branch_activated:
            pygame.draw.lines(surface, activated_color, False, curve_points, 5)
            pygame.draw.line(surface, non_activated_color, (self.xA, self.yA), (self.xS, self.yS), 5)
        else:
            pygame.draw.lines(surface, non_activated_color, False, curve_points, 5)
            pygame.draw.line(surface, activated_color, (self.xA, self.yA), (self.xS, self.yS), 5)
