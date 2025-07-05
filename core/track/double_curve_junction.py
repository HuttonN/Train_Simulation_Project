import pygame
import math

from core.track.base import BaseTrack

from utils.geometry import quadratic_bezier, bezier_derivative, bezier_speed
from utils.numerics import simpson_integral

class DoubleCurveJunctionTrack(BaseTrack):
    """
    Represents a junction with two diverging branches (left and right
    Endpoints: 'A' (start), 'L' (Left end), 'R' (Right end).
    """

    ENDPOINTS = ["A", "L", "R"]

    #region --- Constructor ---------------------------------------------------------

    def __init__(
            self, grid, 
            start_row, start_col,  
            right_curve_control_row, right_curve_control_col, 
            left_curve_control_row, left_curve_control_col, 
            right_curve_end_row, right_curve_end_col, 
            left_curve_end_row, left_curve_end_col, 
            track_id, track_type,
            left_branch_activated = True,
            right_branch_activated = False
        ):
        super().__init__(grid, track_id, track_type)
        self.start_row = start_row
        self.start_col = start_col
        self.right_curve_control_row = right_curve_control_row
        self.right_curve_control_col = right_curve_control_col
        self.right_curve_end_row = right_curve_end_row
        self.right_curve_end_col = right_curve_end_col
        self.left_curve_control_row = left_curve_control_row
        self.left_curve_control_col = left_curve_control_col
        self.left_curve_end_row = left_curve_end_row
        self.left_curve_end_col = left_curve_end_col
        self.left_branch_activated = left_branch_activated
        self.right_branch_activated = right_branch_activated

        # Pixel coordinates of cell centers
        self.xA, self.yA = self.grid.grid_to_screen(start_row, start_col)
        self.xRCtrl, self.yRCtrl = self.grid.grid_to_screen(right_curve_control_row, right_curve_control_col)
        self.xR, self.yR = self.grid.grid_to_screen(right_curve_end_row, right_curve_end_col)
        self.xLCtrl, self.yLCtrl = self.grid.grid_to_screen(left_curve_control_row, left_curve_control_col)
        self.xL, self.yL = self.grid.grid_to_screen(left_curve_end_row, left_curve_end_col)

        # Endpoint maps
        self.endpoint_coords = {
            "A": (self.xA, self.yA),
            "L": (self.xL, self.yL),
            "R": (self.xR, self.yR)
        }
        self.endpoint_grids = {
            "A": (self.start_row, self.start_col),
            "L": (self.left_curve_end_row, self.left_curve_end_col),
            "R": (self.right_curve_end_row, self.right_curve_end_col)
        }

        # Compute total arc length using Simpson's rule
        self.left_curve_length = self.total_arc_length("L")
        self.right_curve_length = self.total_arc_length("R")
        self.left_even_t_table = self.build_even_length_table("A_to_L", n_samples=150)
        self.right_even_t_table = self.build_even_length_table("A_to_R", n_samples=150)

    #endregion

    #region --- Control / State Methods ---------------------------------------------
        
    def activate_branch(self, branch):
        """Activate the input branch and deactivate the other"""
        pygame.time.delay(3000)
        if branch == "L":
            if not self.left_branch_activated:
                self.left_branch_activated = True
                self.right_branch_activated = False
        elif branch == "R":
            if not self.right_branch_activated:
                self.left_branch_activated = False
                self.right_branch_activated = True

    def is_branch_set_for(self, entry_ep, exit_ep):
        """
        Check if the current branch activation matches the desired route.
        """
        if {entry_ep, exit_ep} == {"A", "L"}:
            return self.left_branch_activated
        if {entry_ep, exit_ep} == {"A", "R"}:
            return self.right_branch_activated
    
    #endregion

    #region --- Geometry & Movement Methods -----------------------------------------
        
    def get_angle(self, entry_ep, exit_ep):
        """Returns the angle of travel for a movement from entry_ep to exit_ep."""
        if {entry_ep, exit_ep} == {"A", "R"} or {entry_ep, exit_ep} == {"A", "L"}:
            # For curve, angle at t=0 if from A, at t=1 if from R or L
            t = 0.0 if entry_ep == "A" else 1.0
            if {entry_ep, exit_ep} == {"A", "R"}:
                dx, dy = bezier_derivative(
                    t,
                    (self.xA, self.yA),
                    (self.xRCtrl, self.yRCtrl),
                    (self.xR, self.yR)
                )
            else:
                dx, dy = bezier_derivative(
                    t,
                    (self.xA, self.yA),
                    (self.xLCtrl, self.yLCtrl),
                    (self.xL, self.yL)
                )
            if entry_ep != "A":
                dx, dy = -dx, -dy
            return math.degrees(math.atan2(dy, dx))
        else:
            # Not a direct segment: return angle towards A
            x_from, y_from = self.get_endpoint_coords(entry_ep)
            x_to, y_to = self.get_endpoint_coords(exit_ep)
            return math.degrees(math.atan2(y_to - y_from, x_to - x_from))
        
    def get_point_and_angle(self, t, branch, direction):
        """Returns a point and angle on the curve at parameter t (0 ≤ t ≤ 1)."""
        if direction == "R_to_A" or direction == "L_to_A":
            t = 1 - t
        point = quadratic_bezier(t, *self.curve_points(branch))
        dx, dy = bezier_derivative(t, *self.curve_points(branch))
        if direction == "R_to_A" or direction == "L_to_A":
            dx, dy = -dx, -dy
        angle = math.degrees(math.atan2(dy, dx))
        return point, angle
    
    def move_along_segment(self, train, speed, entry_ep, exit_ep):
        """
        Moves the train along the segment between the given endpoints.
        (Consistent API with StraightTrack/CurvedTrack)
        """
        if {entry_ep, exit_ep} == {"A", "R"}:
            # Curve movement
            if entry_ep == "A":
                train.s_on_curve = min(train.s_on_curve + speed, self.right_curve_length)
                t = self.arc_length_to_t(train.s_on_curve, direction="A_to_R")
                (train.x, train.y), train.angle = self.get_point_and_angle(t, "R", direction="A_to_R")
                if train.s_on_curve >= self.right_curve_length:
                    train.row, train.col = self.right_curve_end_row, self.right_curve_end_col
            else:
                train.s_on_curve = max(train.s_on_curve - speed, 0)
                t = self.arc_length_to_t(train.s_on_curve, direction="R_to_A")
                (train.x, train.y), train.angle = self.get_point_and_angle(t, "R", direction="R_to_A")
                if train.s_on_curve <= 0:
                    train.row, train.col = self.start_row, self.start_col
        elif {entry_ep, exit_ep} == {"A", "L"}:
            # Curve movement
            if entry_ep == "A":
                train.s_on_curve = min(train.s_on_curve + speed, self.left_curve_length)
                t = self.arc_length_to_t(train.s_on_curve, direction="A_to_L")
                (train.x, train.y), train.angle = self.get_point_and_angle(t, "L", direction="A_to_L")
                if train.s_on_curve >= self.left_curve_length:
                    train.row, train.col = self.left_curve_end_row, self.left_curve_end_col
            else:
                train.s_on_curve = max(train.s_on_curve - speed, 0)
                t = self.arc_length_to_t(train.s_on_curve, direction="L_to_A")
                (train.x, train.y), train.angle = self.get_point_and_angle(t, "L", direction="L_to_A")
                if train.s_on_curve <= 0:
                    train.row, train.col = self.start_row, self.start_col

    def has_reached_endpoint(self, train, exit_ep):
        """
        Returns True if the train has arrived at the requested exit endpoint on the junction.
        Handles both straight and curve branches.
        """
        if train.entry_ep == "A":
            return train.s_on_curve >= self.left_curve_length
        else:
            return train.s_on_curve <= 0

    #endregion

    #region --- Curve Length/Arc Methods --------------------------------------------

    def curve_points(self, branch):
        if branch == "L":
            return (self.xA, self.yA), (self.xLCtrl, self.yLCtrl), (self.xL, self.yL)
        elif branch == "R":
            return (self.xA, self.yA), (self.xRCtrl, self.yRCtrl), (self.xR, self.yR)
        else:
            raise ValueError("branch must be 'L' or 'R'")

    def bezier_speed(self, t, branch):
        """Returns the speed along the Bezier curve at parameter t."""
        p0, p1, p2 = self.curve_points(branch)
        return bezier_speed(t, p0, p1, p2)

    def total_arc_length(self, branch):
        # Accurate curve length via Simpson's rule
        p0, p1, p2 = self.curve_points(branch)
        f = lambda t: bezier_speed(t, p0, p1, p2)
        return simpson_integral(f, 0, 1, n=64)
    
    def arc_length_up_to_t(self, t, branch):
        # Returns arc length from t=0 to t (again via Simpson)
        p0, p1, p2 = self.curve_points(branch)
        f = lambda u: bezier_speed(u, p0, p1, p2)
        return simpson_integral(f, 0, t, n=32)
    
    def arc_length_to_t(self, s, direction, tol=1e-5, max_iter=20):
        """Given arc length s, solve for t along the curve (0 to 1 for A->L/R, 1 to 0 for L/R->A)."""
        if direction == "A_to_L" or direction == "A_to_R":
            if s <= 0:
                return 0.0
            if direction == "A_to_L":
                if s >= self.left_curve_length:
                    return 1.0
                t = s / self.left_curve_length  # Initial guess
                for _ in range(max_iter):
                    L = self.arc_length_up_to_t(t, "L")
                    speed = self.bezier_speed(t, "L")
                    if speed == 0:
                        break
                    t_new = t - (L - s) / speed
                    if abs(t_new - t) < tol:
                        return min(max(t_new, 0), 1)
                    t = min(max(t_new, 0), 1)
            if direction == "A_to_R":
                if s >= self.right_curve_length:
                    return 1.0
                t = s / self.right_curve_length  # Initial guess
                for _ in range(max_iter):
                    L = self.arc_length_up_to_t(t, "R")
                    speed = self.bezier_speed(t, "R")
                    if speed == 0:
                        break
                    t_new = t - (L - s) / speed
                    if abs(t_new - t) < tol:
                        return min(max(t_new, 0), 1)
                    t = min(max(t_new, 0), 1)
            return t
        elif direction == "L_to_A" or direction == "R_to_A":
            if s <= 0:
                return 1.0
            if direction == "L_to_A":
                if s >= self.left_curve_length:
                    return 0.0
                t = 1.0 - (s / self.left_curve_length)  # Initial guess
                for _ in range(max_iter):
                    L = self.arc_length_up_to_t(t, "L")
                    speed = self.bezier_speed(t, "L")
                    if speed == 0:
                        break
                    t_new = t - (self.left_curve_length - L - s) / (-speed)
                    if abs(t_new - t) < tol:
                        return min(max(t_new, 0), 1)
                    t = min(max(t_new, 0), 1)
            if direction == "R_to_A":
                if s >= self.right_curve_length:
                    return 0.0
                t = 1.0 - (s / self.right_curve_length)  # Initial guess
                for _ in range(max_iter):
                    L = self.arc_length_up_to_t(t, "R")
                    speed = self.bezier_speed(t, "R")
                    if speed == 0:
                        break
                    t_new = t - (self.right_curve_length - L - s) / (-speed)
                    if abs(t_new - t) < tol:
                        return min(max(t_new, 0), 1)
                    t = min(max(t_new, 0), 1)
            return t
        else:
            raise ValueError("direction must be 'A_to_L/R' or 'L/R_to_A'.")

    def build_even_length_table(self, direction, n_samples=150):
        """Precompute a list of t values corresponding to evenly-spaced distances along the curve."""
        if direction == "A_to_L" or direction == "L_to_A":
            ts = []
            L = self.left_curve_length
            for i in range(n_samples + 1):
                s = L * i / n_samples
                t = self.arc_length_to_t(s, direction)
                ts.append(t)
            return ts
        elif direction == "A_to_R" or direction == "R_to_A":
            ts = []
            L = self.right_curve_length
            for i in range(n_samples + 1):
                s = L * i / n_samples
                t = self.arc_length_to_t(s, direction)
                ts.append(t)
            return ts
        else:
            raise ValueError("direction must be 'A_to_L/R' or 'L/R_to_A'.")

    #endregion
    
    #region --- Rendering Methods ---------------------------------------------------

    def draw_track(self, surface, activated_color=(200, 180, 60), non_activated_color=(255, 0, 0), n_curve_points=50):
        """Draws the curve and straight, highlighting the active branch."""
        left_curve_points = [quadratic_bezier(
            t/(n_curve_points-1),
            (self.xA, self.yA), (self.xLCtrl, self.yLCtrl), (self.xL, self.yL)
        ) for t in range(n_curve_points)]
        right_curve_points = [quadratic_bezier(
            t/(n_curve_points-1),
            (self.xA, self.yA), (self.xRCtrl, self.yRCtrl), (self.xR, self.yR)
        ) for t in range(n_curve_points)]
        if self.left_branch_activated and not self.right_branch_activated:
            pygame.draw.lines(surface, activated_color, False, left_curve_points, 5)
            pygame.draw.lines(surface, non_activated_color, False, right_curve_points, 5)
        if not self.left_branch_activated and self.right_branch_activated:
            pygame.draw.lines(surface, non_activated_color, False, left_curve_points, 5)
            pygame.draw.lines(surface, activated_color, False, right_curve_points, 5)
        else:
            ValueError("adsjkads")

    #endregion

    def get_length(self, entry_ep, exit_ep):
        """
        Return total arc length of the Bezier curve of the chosen branch.

        Arguments:
            entry_ep (str): Start endpoint label.
            exit_ep (str): End endpoint label.
        Returns:
            float: Arc length in pixels.
        """
        # For a quadratic curve, length is the same in either direction.
        if {entry_ep, exit_ep} == {"A", "L"}:
            return self.left_curve_length
        return self.right_curve_length

    def get_position_at_distance(self, entry_ep, exit_ep, s):
        if {entry_ep, exit_ep} == {"A", "L"} or {entry_ep, exit_ep} == {"A", "R"}:
            length = self.get_length(entry_ep, exit_ep)
            if {entry_ep, exit_ep} == {"A", "L"}:
                direction = "A_to_L" if entry_ep == "A" and exit_ep == "L" else "L_to_A"
            else: 
                direction = "A_to_R" if entry_ep == "A" and exit_ep == "R" else "R_to_A"
            s = max(0, min(s, length))
            t = self.arc_length_to_t(s, direction=direction)
            (x, y), angle = self.get_point_and_angle(t, direction=direction)
            return (x, y, angle)
        else:
            # Not a direct connection
            x, y = self.get_endpoint_coords(entry_ep)
            angle = self.get_angle(entry_ep, exit_ep)
            return (x, y, angle)
