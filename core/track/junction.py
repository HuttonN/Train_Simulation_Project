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

    #region --- Constructor ---------------------------------------------------------

    def __init__(
            self, grid, 
            start_row, start_col, 
            straight_end_row, straight_end_col, 
            curve_control_row, curve_control_col, 
            curve_end_row, curve_end_col, 
            track_id, track_type,
            branch_activated = False
        ):

        """
        Initialise a JunctionTrack

        Arguments:
            grid: Grid object.
            start_row, start_col: Grid coordinates for endpoint 'A'.
            straight_end_row, straight_end_col: Grid coordinates for endpoint 'S'.
            curve_control_row, curve_control_col: Grid coordinates for Bezier control point.
            curve_end_row, curve_end_col: Grid coordinates for endpoint 'C'.
            track_id: Unique identifier.
            track_type: String track type.
            branch_activated: Whether the curve branch is active (default: False).
        """

        super().__init__(grid, track_id, track_type)
        self.start_row = start_row
        self.start_col = start_col
        self.straight_end_row = straight_end_row
        self.straight_end_col = straight_end_col
        self.curve_control_row = curve_control_row
        self.curve_control_col = curve_control_col
        self.curve_end_row = curve_end_row
        self.curve_end_col = curve_end_col

        self.branch_activated = branch_activated # True if curve active, false if straight active
        self.is_switching = False
        self.switching_until = 0
        self.pending_branch = None
        self.switch_delay = 2000 # 2 seconds

        self.occupied_by = None

        # Convert grid coordinates to pixel coordinates for rendering and geometry
        self.xA, self.yA = self.grid.grid_to_screen(start_row, start_col)
        self.xS, self.yS = self.grid.grid_to_screen(straight_end_row, straight_end_col)
        self.xCtrl, self.yCtrl = self.grid.grid_to_screen(curve_control_row, curve_control_col)
        self.xC, self.yC = self.grid.grid_to_screen(curve_end_row, curve_end_col)

        # Endpoint maps
        self.endpoint_coords = {
            "A": (self.xA, self.yA),
            "S": (self.xS, self.yS),
            "C": (self.xC, self.yC)
        }
        self.endpoint_grids = {
            "A": (self.start_row, self.start_col),
            "S": (self.straight_end_row, self.straight_end_col),
            "C": (self.curve_end_row, self.curve_end_col)
        }

        # Compute total arc length using Simpson's rule
        self.curve_length = self.total_arc_length()
        self.even_t_table = self.build_even_length_table(n_samples=150)

        # Precompute straight angle
        self.straight_angle = math.degrees(math.atan2(self.yS - self.yA, self.xS - self.xA))

    #endregion

    #region --- Control / State Methods ---------------------------------------------
        
    def request_branch(self, target_branch):
        """
        Begin switching process to target branch (non-blocking).

        Arguments:
            target_branch: True for curve, False for straight
        """
        if self.is_switching or self.branch_activated == target_branch:
            return
        self.is_switching = True
        self.switching_until = pygame.time.get_ticks() + self.switch_delay
        self.pending_branch = target_branch

    def finish_switch(self):
        """
        Complete the branch switch after the time finishes.
        """
        if self.pending_branch is not None:
            self.branch_activated = self.pending_branch
            self.pending_branch = None

    def update(self):
        """
        Update method for switching branch after the delay.
        Should be called every frame/tick.
        """
        if self.is_switching and pygame.time.get_ticks() >= self.switching_until:
            self.is_switching = False
            self.finish_switch()

    def can_proceed(self, entry_ep, exit_ep):
        """
        Determine if a train can traverse the junction, entering entry_ep and exiting at exit_ep.
        Returns True if traversal is allowed, False if waiting for switch
        """
        if self.is_switching:
            return False
        if self.is_branch_set_for(entry_ep, exit_ep):
            return True
        target_branch = True if {entry_ep, exit_ep} == {"A", "C"} else False
        self.request_branch(target_branch)
        return False


    def is_branch_set_for(self, entry_ep, exit_ep):
        """
        Check if the current branch activation matches the desired route.
        """
        if {entry_ep, exit_ep} == {"A", "S"}:
            return not self.branch_activated
        if {entry_ep, exit_ep} == {"A", "C"}:
            return self.branch_activated
        return True
    
    #endregion

    #region --- Geometry & Movement Methods -----------------------------------------
        
    def get_angle(self, entry_ep, exit_ep):
        """
        Returns the angle of travel for a movement from entry_ep to exit_ep.
        """
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
        
    def get_point_and_angle(self, t, direction="A_to_C"):
        """
        Returns a point and angle on the curve at parameter t (0 ≤ t ≤ 1).

        Arguments:
            t: curve parameter in [0,1]
            direction: "A_to_C" or "C_to_A"
        """
        if direction == "C_to_A":
            t = 1 - t
        point = quadratic_bezier(
            t, (self.xA, self.yA), (self.xCtrl, self.yCtrl), (self.xC, self.yC)
        )
        dx, dy = bezier_derivative(
            t, (self.xA, self.yA), (self.xCtrl, self.yCtrl), (self.xC, self.yC)
        )
        if direction == "C_to_A":
            dx, dy = -dx, -dy
        angle = math.degrees(math.atan2(dy, dx))
        return point, angle
    
    def move_along_track_piece(self, train, speed, entry_ep, exit_ep):
        """
        Moves the train along the track piece between the given endpoints.
        
        Arguments:
            train: Train object to move.
            speed: Distance per frame
            entry_ep: Entry endpoint label
            exit_ep: Exit endpoint label
        """
        # Straight branch
        if {entry_ep, exit_ep} == {"A", "S"}:
            if entry_ep == "A":
                target_x, target_y = self.xS, self.yS
                target_grid = (self.straight_end_row, self.straight_end_col)
            else:
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
        # Curve branch
        elif {entry_ep, exit_ep} == {"A", "C"}:
            if entry_ep == "A":
                train.s_on_curve = min(train.s_on_curve + speed, self.curve_length)
                t = self.arc_length_to_t(train.s_on_curve, direction="A_to_C")
                (train.x, train.y), train.angle = self.get_point_and_angle(t, direction="A_to_C")
                if train.s_on_curve >= self.curve_length:
                    train.row, train.col = self.curve_end_row, self.curve_end_col
            else:
                train.s_on_curve = max(train.s_on_curve - speed, 0)
                t = self.arc_length_to_t(train.s_on_curve, direction="C_to_A")
                (train.x, train.y), train.angle = self.get_point_and_angle(t, direction="C_to_A")
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

    def has_reached_endpoint(self, train, exit_ep):
        """
        Returns True if the train has arrived at the requested exit endpoint on the junction.
        
        Arguments:
            train: Train object
            exit_ep: Target endpoint label
        """
        if {train.entry_ep, exit_ep} == {"A", "S"}:
            tx, ty = self.get_endpoint_coords(exit_ep)
            return abs(train.x - tx) < 1 and abs(train.y - ty) < 1
        elif {train.entry_ep, exit_ep} == {"A", "C"}:
            if train.entry_ep == "A":
                return train.s_on_curve >= self.curve_length
            else:
                return train.s_on_curve <= 0
        else:
            # Fallback for rare/complex endpoint pairs (e.g., S <-> C): use coordinate check
            tx, ty = self.get_endpoint_coords(exit_ep)
            return abs(train.x - tx) < 1 and abs(train.y - ty) < 1
        
    def get_length(self, entry_ep, exit_ep):
        """
        Get the length (pixels) between endpoints.

        Arguments:
            entry_ep (str): Start endpoint.
            exit_ep (str): End endpoint.

        """
        # Handle straight (A<->S)
        if {entry_ep, exit_ep} == {"A", "S"}:
            x1, y1 = self.get_endpoint_coords(entry_ep)
            x2, y2 = self.get_endpoint_coords(exit_ep)
            return ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5
        # Handle curve (A<->C)
        elif {entry_ep, exit_ep} == {"A", "C"}:
            return self.curve_length
        else:
            # Not a direct connection: could be extended, for now just return 0
            return 0

    def get_position_at_distance(self, entry_ep, exit_ep, s):
        """
        Return (x, y, angle) at distance s along the track from entry_ep to exit_ep.

        Args:
            entry_ep (str): Start endpoint.
            exit_ep (str): End endpoint.
            s (float): Distance along the track.

        Returns:
            tuple: (x, y, angle)
        """
        if {entry_ep, exit_ep} == {"A", "S"}:
            length = self.get_length(entry_ep, exit_ep)
            t = s / length if length != 0 else 0
            if t > 1: t = 1
            x1, y1 = self.get_endpoint_coords(entry_ep)
            x2, y2 = self.get_endpoint_coords(exit_ep)
            x = (1 - t) * x1 + t * x2
            y = (1 - t) * y1 + t * y2
            angle = self.get_angle(entry_ep, exit_ep)
            return (x, y, angle)
        elif {entry_ep, exit_ep} == {"A", "C"}:
            length = self.get_length(entry_ep, exit_ep)
            direction = "A_to_C" if entry_ep == "A" and exit_ep == "C" else "C_to_A"
            s = max(0, min(s, length))
            t = self.arc_length_to_t(s, direction=direction)
            (x, y), angle = self.get_point_and_angle(t, direction=direction)
            return (x, y, angle)
        else:
            # Not a direct connection
            x, y = self.get_endpoint_coords(entry_ep)
            angle = self.get_angle(entry_ep, exit_ep)
            return (x, y, angle)

    #endregion

    #region --- Curve Length/Arc Methods --------------------------------------------

    def curve_points(self):
        """
        Returns the control points as tuples for the curve.
        """
        return (self.xA, self.yA), (self.xCtrl, self.yCtrl), (self.xC, self.yC)

    def bezier_speed(self, t):
        """
        Returns the speed along the Bezier curve at parameter t.
        """
        p0, p1, p2 = self.curve_points()
        return bezier_speed(t, p0, p1, p2)

    def total_arc_length(self):
        """
        Compute the total arc length of the Bezier curve.
        """
        p0, p1, p2 = self.curve_points()
        f = lambda t: bezier_speed(t, p0, p1, p2)
        return simpson_integral(f, 0, 1, n=64)
    
    def arc_length_up_to_t(self, t):
        """
        Compute arc length from t=0 up to t for the curve.
        """
        p0, p1, p2 = self.curve_points()
        f = lambda u: bezier_speed(u, p0, p1, p2)
        return simpson_integral(f, 0, t, n=32)
    
    def arc_length_to_t(self, s, direction="A_to_C", tol=1e-5, max_iter=20):
        """
        Given arc length s, solve for t along the curve (0 to 1 for A->C, 1 to 0 for C->A).

        Arguments:
            s: Arc length.
            direction: "A_to_C" or "C_to_A".
            tol: Tolerance for iterative solver.
            max_iter: Max number of iterations.
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

    def build_even_length_table(self, n_samples=150):
        """
        Precompute a list of t values corresponding to evenly-spaced distances along the curve.

        Arguments:
            n_samples: Number of samples
        """
        ts = []
        L = self.curve_length
        for i in range(n_samples + 1):
            s = L * i / n_samples
            t = self.arc_length_to_t(s, direction="A_to_C")
            ts.append(t)
        return ts
    
    #endregion
    
    #region --- Rendering Methods ---------------------------------------------------

    def draw_track(self, surface, activated_color=(200, 180, 60), non_activated_color=(255, 0, 0), n_curve_points=50):
        """
        Draw the junction on the given surface, highlighting the active branch.

        Arguments:
            surface: Pygame surface.
            activated_color: Color for the active branch.
            non_activated_color: Color for the inactive branch.
            n_curve_points: Number of points for curve rendering.
        """
        curve_points = [
            quadratic_bezier(
                t/(n_curve_points-1),
                (self.xA, self.yA), (self.xCtrl, self.yCtrl), (self.xC, self.yC)
        ) for t in range(n_curve_points)
        ]
        if self.branch_activated:
            pygame.draw.lines(surface, activated_color, False, curve_points, 5)
            pygame.draw.line(surface, non_activated_color, (self.xA, self.yA), (self.xS, self.yS), 5)
        else:
            pygame.draw.lines(surface, non_activated_color, False, curve_points, 5)
            pygame.draw.line(surface, activated_color, (self.xA, self.yA), (self.xS, self.yS), 5)

    #endregion

    #region --- Reservation/Segment Methods ---------------------------------------------------

    def can_reserve_junction(self, train, exit_segment):
        """
        Attempt to atomically reserve both this junction and the exit segment.
        Returns True if reservation successful, False if blocked.

        Arguments:
            train: Train object.
            exit_segment: Next track segment object.
        """
        if self.occupied_by is None and exit_segment.occupied_by is None:
            self.occupied_by = train
            exit_segment.occupied_by = train
            return True
        return False
    
    def release_junction(self, train):
        """
        Release the junction reservation if occupied by the given train.

        Arguments:
            train: Train object.
        """
        if self.occupied_by == train:
            self.occupied_by = None