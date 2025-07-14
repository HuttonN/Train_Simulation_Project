import pygame
import math

from core.track.base import BaseTrack

from utils.geometry import quadratic_bezier, bezier_derivative, bezier_speed
from utils.numerics import simpson_integral
from utils.signals import draw_signal_indicator

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
            active_branch = "L"
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
        
        self.active_branch = active_branch

        self.occupied_by = None

        self.is_switching = False
        self.switching_until = 0
        self.pending_branch = None
        self.switch_delay = 2000  # 2 seconds

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

    def request_branch(self, branch):
        """
        Start switching process to a branch ('L' or 'R').
        Non-blocking: switch completes after self.switch_delay ms.
        """
        if self.is_switching or self.active_branch == branch:
            return
        self.is_switching = True
        self.switching_until = pygame.time.get_ticks() + self.switch_delay
        self.pending_branch = branch

    def finish_switch(self):
        """Complete the switch to the pending branch."""
        if self.pending_branch in ("L", "R"):
            self.active_branch = self.pending_branch
            self.pending_branch = None

    def update(self):
        if self.is_switching and pygame.time.get_ticks() >= self.switching_until:
            self.is_switching = False
            self.finish_switch()

    def can_proceed(self, entry_ep, exit_ep):
        """
        Should the train proceed (through this branch)?
        Returns True if active branch matches desired; triggers switch if needed.
        """
        if self.is_switching:
            return False
        needed_branch = None
        if {entry_ep, exit_ep} == {"A", "L"}:
            needed_branch = "L"
        elif {entry_ep, exit_ep} == {"A", "R"}:
            needed_branch = "R"
        if needed_branch is None:
            # Allow if not a valid branch (shouldn't happen in normal routing)
            return True
        if self.active_branch == needed_branch:
            return True
        self.request_branch(needed_branch)
        return False

    def is_branch_set_for(self, entry_ep, exit_ep):
        """Compatibility with train API (legacy, not really used)."""
        if {entry_ep, exit_ep} == {"A", "L"}:
            return self.active_branch == "L"
        if {entry_ep, exit_ep} == {"A", "R"}:
            return self.active_branch == "R"
        return True

    # -------------- Geometry & Movement ---------------

    def curve_points(self, branch):
        if branch == "L":
            return (self.xA, self.yA), (self.xLCtrl, self.yLCtrl), (self.xL, self.yL)
        elif branch == "R":
            return (self.xA, self.yA), (self.xRCtrl, self.yRCtrl), (self.xR, self.yR)
        else:
            raise ValueError("branch must be 'L' or 'R'")

    def get_angle(self, entry_ep, exit_ep):
        if {entry_ep, exit_ep} == {"A", "L"}:
            t = 0.0 if entry_ep == "A" else 1.0
            dx, dy = bezier_derivative(t, *self.curve_points("L"))
            if entry_ep != "A":
                dx, dy = -dx, -dy
            return math.degrees(math.atan2(dy, dx))
        if {entry_ep, exit_ep} == {"A", "R"}:
            t = 0.0 if entry_ep == "A" else 1.0
            dx, dy = bezier_derivative(t, *self.curve_points("R"))
            if entry_ep != "A":
                dx, dy = -dx, -dy
            return math.degrees(math.atan2(dy, dx))
        # Fallback for odd routing
        x_from, y_from = self.get_endpoint_coords(entry_ep)
        x_to, y_to = self.get_endpoint_coords(exit_ep)
        return math.degrees(math.atan2(y_to - y_from, x_to - x_from))

    def get_point_and_angle(self, t, branch, direction):
        if direction in ("L_to_A", "R_to_A"):
            t = 1 - t
        point = quadratic_bezier(t, *self.curve_points(branch))
        dx, dy = bezier_derivative(t, *self.curve_points(branch))
        if direction in ("L_to_A", "R_to_A"):
            dx, dy = -dx, -dy
        angle = math.degrees(math.atan2(dy, dx))
        return point, angle

    def move_along_track_piece(self, train, speed, entry_ep, exit_ep):
        # Only allow movement if active branch matches desired
        if {entry_ep, exit_ep} == {"A", "R"}:
            branch = "R"
            curve_length = self.right_curve_length
            direction = "A_to_R" if entry_ep == "A" else "R_to_A"
        elif {entry_ep, exit_ep} == {"A", "L"}:
            branch = "L"
            curve_length = self.left_curve_length
            direction = "A_to_L" if entry_ep == "A" else "L_to_A"
        else:
            # Not a direct branch, just jump
            target_x, target_y = self.get_endpoint_coords(exit_ep)
            train.x, train.y = target_x, target_y
            train.row, train.col = self.get_endpoint_grid(exit_ep)
            return

        if entry_ep == "A":
            train.s_on_curve = min(train.s_on_curve + speed, curve_length)
        else:
            train.s_on_curve = max(train.s_on_curve - speed, 0)
        t = self.arc_length_to_t(train.s_on_curve, direction=direction)
        (train.x, train.y), train.angle = self.get_point_and_angle(t, branch, direction)
        # Update grid position if reached end
        if entry_ep == "A" and train.s_on_curve >= curve_length:
            if branch == "L":
                train.row, train.col = self.left_curve_end_row, self.left_curve_end_col
            else:
                train.row, train.col = self.right_curve_end_row, self.right_curve_end_col
        elif entry_ep != "A" and train.s_on_curve <= 0:
            train.row, train.col = self.start_row, self.start_col

    def has_reached_endpoint(self, train, exit_ep):
        # Checks for completion of branch traversal
        if {train.entry_ep, exit_ep} == {"A", "L"}:
            if train.entry_ep == "A":
                return train.s_on_curve >= self.left_curve_length
            else:
                return train.s_on_curve <= 0
        if {train.entry_ep, exit_ep} == {"A", "R"}:
            if train.entry_ep == "A":
                return train.s_on_curve >= self.right_curve_length
            else:
                return train.s_on_curve <= 0
        # fallback for non-branch movement
        tx, ty = self.get_endpoint_coords(exit_ep)
        return abs(train.x - tx) < 1 and abs(train.y - ty) < 1

    # ------- Curve Length, Arc, and Rendering -------

    def bezier_speed(self, t, branch):
        p0, p1, p2 = self.curve_points(branch)
        return bezier_speed(t, p0, p1, p2)

    def total_arc_length(self, branch):
        p0, p1, p2 = self.curve_points(branch)
        f = lambda t: bezier_speed(t, p0, p1, p2)
        return simpson_integral(f, 0, 1, n=64)

    def arc_length_up_to_t(self, t, branch):
        p0, p1, p2 = self.curve_points(branch)
        f = lambda u: bezier_speed(u, p0, p1, p2)
        return simpson_integral(f, 0, t, n=32)

    def arc_length_to_t(self, s, direction, tol=1e-5, max_iter=20):
        if direction == "A_to_L":
            curve_length = self.left_curve_length
            branch = "L"
        elif direction == "A_to_R":
            curve_length = self.right_curve_length
            branch = "R"
        elif direction == "L_to_A":
            curve_length = self.left_curve_length
            branch = "L"
        elif direction == "R_to_A":
            curve_length = self.right_curve_length
            branch = "R"
        else:
            raise ValueError("direction must be 'A_to_L/R' or 'L/R_to_A'.")

        if direction.startswith("A_to"):
            if s <= 0:
                return 0.0
            if s >= curve_length:
                return 1.0
            t = s / curve_length  # Initial guess
            for _ in range(max_iter):
                L = self.arc_length_up_to_t(t, branch)
                speed = self.bezier_speed(t, branch)
                if speed == 0:
                    break
                t_new = t - (L - s) / speed
                if abs(t_new - t) < tol:
                    return min(max(t_new, 0), 1)
                t = min(max(t_new, 0), 1)
            return t
        else:
            # direction ends with _to_A
            if s <= 0:
                return 1.0
            if s >= curve_length:
                return 0.0
            t = 1.0 - (s / curve_length)
            for _ in range(max_iter):
                L = self.arc_length_up_to_t(t, branch)
                speed = self.bezier_speed(t, branch)
                if speed == 0:
                    break
                t_new = t - (curve_length - L - s) / (-speed)
                if abs(t_new - t) < tol:
                    return min(max(t_new, 0), 1)
                t = min(max(t_new, 0), 1)
            return t

    def build_even_length_table(self, direction, n_samples=150):
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

    def draw_track(self, surface, track_objects, activated_color=(200, 180, 60), non_activated_color=(255, 0, 0), n_curve_points=50):
        left_curve_points = [quadratic_bezier(
            t/(n_curve_points-1),
            (self.xA, self.yA), (self.xLCtrl, self.yLCtrl), (self.xL, self.yL)
        ) for t in range(n_curve_points)]
        right_curve_points = [quadratic_bezier(
            t/(n_curve_points-1),
            (self.xA, self.yA), (self.xRCtrl, self.yRCtrl), (self.xR, self.yR)
        ) for t in range(n_curve_points)]
        if self.active_branch == "L":
            pygame.draw.lines(surface, activated_color, False, left_curve_points, 5)
            pygame.draw.lines(surface, non_activated_color, False, right_curve_points, 5)
            self.draw_signals(surface, track_objects)
        else:
            pygame.draw.lines(surface, non_activated_color, False, left_curve_points, 5)
            pygame.draw.lines(surface, activated_color, False, right_curve_points, 5)
            self.draw_signals(surface, track_objects)

    def get_length(self, entry_ep, exit_ep):
        if {entry_ep, exit_ep} == {"A", "L"}:
            return self.left_curve_length
        elif {entry_ep, exit_ep} == {"A", "R"}:
            return self.right_curve_length
        return 0

    def get_position_at_distance(self, entry_ep, exit_ep, s):
        if {entry_ep, exit_ep} == {"A", "L"} or {entry_ep, exit_ep} == {"A", "R"}:
            length = self.get_length(entry_ep, exit_ep)
            if {entry_ep, exit_ep} == {"A", "L"}:
                direction = "A_to_L" if entry_ep == "A" and exit_ep == "L" else "L_to_A"
                branch = "L"
            else:
                direction = "A_to_R" if entry_ep == "A" and exit_ep == "R" else "R_to_A"
                branch = "R"
            s = max(0, min(s, length))
            t = self.arc_length_to_t(s, direction=direction)
            (x, y), angle = self.get_point_and_angle(t, branch, direction)
            return (x, y, angle)
        else:
            x, y = self.get_endpoint_coords(entry_ep)
            angle = self.get_angle(entry_ep, exit_ep)
            return (x, y, angle)
        
    def can_reserve_junction(self, train, exit_segment):
        """
        Attempt to atomically reserve both this junction and the exit segment.
        Returns True if reservation successful, False if blocked.
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

    def get_segment_for_branch(self, track_objects, endpoint_label):
        id = self.connections[endpoint_label]["track"]
        return track_objects[id].segment

    def get_signal_states(self, track_objects):
        """
        Returns a dictionary mapping each branch to its signal state (allowed, active, in_progress).

        Returns:
            dict: For example, {'straight': {...}, 'curve': {...}}
        """
        signal_states = {
            "signal_AL": {
                "allowed": self.active_branch == "L" and not self.get_segment_for_branch(track_objects, "left_curve_end").occupied_by and not self.is_switching,
                "active": self.active_branch == "L",
                "in_progress": self.is_switching
            },
            "signal_AR": {
                "allowed": self.active_branch == "R" and not self.get_segment_for_branch(track_objects, "right_curve_end").occupied_by and not self.is_switching,
                "active": self.active_branch == "R",
                "in_progress": self.is_switching
            },
            "signal_LA": {
                "allowed": self.active_branch == "L" and not self.get_segment_for_branch(track_objects, "start").occupied_by and not self.is_switching,
                "active": self.active_branch == "L",
                "in_progress": self.is_switching
            },
            "signal_RA": {
                "allowed": self.active_branch == "R" and not self.get_segment_for_branch(track_objects, "start").occupied_by and not self.is_switching,
                "active": self.active_branch == "R",
                "in_progress": self.is_switching
            }
        }

        return signal_states
    
    def draw_signals(self, surface, track_objects):
        """
        Draws all signal indicators for this junction on the given surface.

        Args:
            surface: Pygame surface to draw on.
        """

        # Get endpoint coordinates
        xA, yA = self.endpoint_coords["A"]
        xL, yL = self.endpoint_coords["L"]
        xR, yR = self.endpoint_coords["R"]

        # Get angle of direction at entrances (in radians)
        angle_Astart = math.radians(self.get_point_and_angle(0, "R", direction="A_to_R")[1]) # Don't think branch choice will matter, as straight ahead when t=0
        angle_Lstart = math.radians(self.get_point_and_angle(0, "L", direction="L_to_A")[1])
        angle_Rstart = math.radians(self.get_point_and_angle(0, "R", direction="R_to_A")[1])
        
        # Set offset
        signal_offset = 22

        # Set up the required vectors
        dxAstart, dyAstart = math.cos(angle_Astart), math.sin(angle_Astart)
        dxLstart, dyLstart = math.cos(angle_Lstart), math.sin(angle_Lstart)
        dxRstart, dyRstart = math.cos(angle_Rstart), math.sin(angle_Rstart)
        dxAL, dyAL = xL - xA, yL - yA
        dxAR, dyAR = xR - xA, yR - yA
        dxLA, dyLA = -dxAL, -dyAL
        dxRA, dyRA = -dxAR, -dyAR
        
        # Calculate the required angles
        angle_AL = math.atan2(dyAL, dxAL)
        angle_AR = math.atan2(dyAR, dxAR)
        angle_LA = math.atan2(dyLA, dxLA)
        angle_RA = math.atan2(dyRA, dxRA)

        # Determine perpendicular vectors for signal position
        perp_dxAstartL, perp_dyAstartL = dyAstart, -dxAstart 
        perp_dxAstartR, perp_dyAstartR = -dyAstart, dxAstart 
        perp_dxLstart, perp_dyLstart = dyLstart, -dxLstart 
        perp_dxRstart, perp_dyRstart = -dyRstart, dxRstart 

        # Calculate vector lengths
        len_perp_AstartL = math.hypot(perp_dxAstartL, perp_dyAstartL)
        len_perp_AstartR = math.hypot(perp_dxAstartR, perp_dyAstartR)
        len_perp_Lstart = math.hypot(perp_dxLstart, perp_dyLstart)
        len_perp_Rstart = math.hypot(perp_dxRstart, perp_dyRstart)

        # Define unit vectors in same direction
        perp_uxAstartL, perp_uyAstartL = perp_dxAstartL / len_perp_AstartL, perp_dyAstartL / len_perp_AstartL
        perp_uxAstartR, perp_uyAstartR = perp_dxAstartR / len_perp_AstartR, perp_dyAstartR / len_perp_AstartR
        perp_uxLstart, perp_uyLstart = perp_dxLstart / len_perp_Lstart, perp_dyLstart / len_perp_Lstart
        perp_uxRstart, perp_uyRstart = perp_dxRstart / len_perp_Rstart, perp_dyRstart / len_perp_Rstart

        # Determine centers of signal centers
        center_AL = (
            int(xA + perp_uxAstartL * signal_offset),
            int(yA + perp_uyAstartL * signal_offset)
        )
        center_AR = (
            int(xA + perp_uxAstartR * signal_offset),
            int(yA + perp_uyAstartR * signal_offset)
        )
        center_LA = (
            int(xL + perp_uxLstart * signal_offset),
            int(yL + perp_uyLstart * signal_offset)
        )
        center_RA = (
            int(xR + perp_uxRstart * signal_offset),
            int(yR + perp_uyRstart * signal_offset)
        )
        # center_RA = (
        #     int(xR + perp_uxCstart * signal_offset),
        #     int(yR+ perp_uyCstart * signal_offset)
        # )

        # Compute signal states
        states = self.get_signal_states(track_objects)

        # Draw the signals
        draw_signal_indicator(surface, center_AL, states["signal_AL"])
        draw_signal_indicator(surface, center_AR, states["signal_AR"])
        draw_signal_indicator(surface, center_LA, states["signal_LA"])
        draw_signal_indicator(surface, center_RA, states["signal_RA"])