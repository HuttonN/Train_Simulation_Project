import pygame
import math

from core.track.base import BaseTrack

class StraightTrack(BaseTrack):
    """
    Represents a straight track piece between two grid cell centers.
    
    ENDPOINTS:
        - "A": One end of the straight segment.
        - "B": The other end of the straight segment.
    """

    ENDPOINTS = ["A", "B"]

    #region --- Constructor ---------------------------------------------------------

    def __init__(self, grid, start_row, start_col, end_row, end_col, track_id=None):
        """
        Initialise a straight track segment.

        Arguments:
            grid: Grid object for coordinate conversion.
            start_row, start_col: Grid coordinates for endpoint "A".
            end_row, end_col: Grid coordinates for endpoint "B".
            track_id (str, optional): Unique identifier for this track piece.
        """
        super().__init__()
        self.grid = grid
        self.start_row = start_row
        self.start_col = start_col
        self.end_row = end_row
        self.end_col = end_col
        self.track_id = track_id or f"Straight:{start_row},{start_col}->{end_row},{end_col}"
        
        # Get pixel coordinates of cell centers
        self.xA, self.yA = self.grid.grid_to_screen(start_row, start_col)
        self.xB, self.yB = self.grid.grid_to_screen(end_row, end_col)
        self.angle = math.degrees(math.atan2(self.yB - self.yA, self.xB - self.xA))

        # DRY endpoint maps
        self.endpoint_coords = {
            "A": (self.xA, self.yA),
            "B": (self.xB, self.yB)
        }
        self.endpoint_grids = {
            "A": (self.start_row, self.start_col),
            "B": (self.end_row, self.end_col)
        }

    #endregion

    #region --- Endpoint Methods ----------------------------------------------------
    
    def get_endpoint_coords(self, endpoint):
        """Return pixel (x, y) coordinates for a given endpoint label."""
        if endpoint == "A":
            return self.xA, self.yA
        elif endpoint == "B":
            return self.xB, self.yB
        else:
            raise ValueError("Unknown endpoint for straight track.")

    def get_endpoint_grid(self, endpoint):
        """Return grid (row, col) coordinates for a given endpoint label."""
        if endpoint == "A":
            return self.start_row, self.start_col
        elif endpoint == "B":
            return self.end_row, self.end_col
        else:
            raise ValueError("Unknown endpoint for straight track.")
        
    #endregion

    #region --- Geometry Methods ----------------------------------------------------

    def get_angle(self, entry_ep, exit_ep):
        """
        Returns angle of travel (in degrees) for movement from entry_ep to exit_ep.

        Arguments:
            entry_ep (str): Entry endpoint label.
            exit_ep (str): Exit endpoint label.
        Returns:
            float: Angle in degrees (0 = right/east, 90 = up/north).
        Raises:
            ValueError: If endpoints do not form a valid pair.
        """
        if entry_ep == "A" and exit_ep == "B":
            return self.angle
        elif entry_ep == "B" and exit_ep == "A":
            return (self.angle + 180) % 360
        else:
            raise ValueError("Invalid endpoint pair for straight track.")
        
    def get_point_and_angle(self, t, direction):
        """
        Return interpolated (x, y) position and angle at parameter t (0=start, 1=end).

        Arguments:
            t (float): Fractional position along the segment (0=start, 1=end).
            direction (str): "A_to_B" or "B_to_A". If "B_to_A", t is reversed.

        Returns:
            tuple: ((x, y), angle)
        """
        if direction == "B_to_A":
            t = 1-t
        return self.get_point_at_t("A", "B", t)
        
    def move_along_segment(self, train, speed, entry_ep, exit_ep):
        """
        Move the train along the segment from entry_ep to exit_ep.

        Arguments:
            train: Train object to move.
            speed (float): Distance to move per frame (pixels).
            entry_ep (str): Entry endpoint label.
            exit_ep (str): Exit endpoint label.
        """
        target_x, target_y = self.get_endpoint_coords(exit_ep)
        target_grid = self.get_endpoint_grid(exit_ep)
        dx = target_x - train.x
        dy = target_y - train.y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist > speed:
            # Normal case where distance to travel is greater than speed
            train.x += dx / dist * speed
            train.y += dy / dist * speed
        else:
            # If distance is less than speed, snap to endpoint and update grid position
            train.x, train.y = target_x, target_y
            train.row, train.col = target_grid

    def has_reached_endpoint(self, train, exit_ep):
        """
        Check if the train has arrived at the exit endpoint.

        Arguments:
            train: Train object.
            exit_ep (str): Target endpoint label.

        Returns:
            bool: True if train is within 1 pixel of endpoint.
        """
        tx, ty = self.get_endpoint_coords(exit_ep)
        return abs(train.x - tx) < 1 and abs(train.y - ty) < 1
    
    def get_length(self, entry_ep, exit_ep):
        """
        Return Euclidean distance between two endpoints.

        Arguments:
            entry_ep (str): Start endpoint label.
            exit_ep (str): End endpoint label.

        Returns:
            float: Distance (pixels) between endpoints.
        """
        x1, y1 = self.get_endpoint_coords(entry_ep)
        x2, y2 = self.get_endpoint_coords(exit_ep)
        return ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5
    
    def get_position_at_distance(self, entry_ep, exit_ep, s):
        """
        Return (x, y, angle) at distance s along the segment from entry_ep to exit_ep.

        Arguments:
            entry_ep (str): Start endpoint label.
            exit_ep (str): End endpoint label.
            s (float): Distance along the segment (pixels).

        Returns:
            tuple: (x, y, angle) where (x, y) is the position and angle in degrees.
        """
        length = self.get_length(entry_ep, exit_ep)
        t = s / length if length != 0 else 0
        t = min(t, 1)
        return self.get_point_at_t(entry_ep, exit_ep, t)
    
    def get_point_at_t(self, entry_ep, exit_ep, t):
        """
        Return (x, y, angle) at normalised parameter t (0=start, 1=end) along the segment.

        Arguments:
            entry_ep (str): Start endpoint label.
            exit_ep (str): End endpoint label.
            t (float): Normalised position (0=start, 1=end).

        Returns:
            tuple: (x, y, angle)
        """
        x1, y1 = self.get_endpoint_coords(entry_ep)
        x2, y2 = self.get_endpoint_coords(exit_ep)
        x = (1-t) * x1 + t * x2
        y = (1-t) * y1 + t * y2
        angle = self.get_angle(entry_ep, exit_ep)
        return (x, y, angle)

    #endregion
        
    #region --- Rendering Methods ---------------------------------------------------

    def draw_track(self, surface, color=(200, 180, 60)):
        """
        Draw the straight track as a thick line on the given surface.

        Arguments:
            surface: Pygame surface to draw onto.
            color (tuple, optional): RGB color for the track.
        """
        pygame.draw.line(surface, color, (self.xA, self.yA), (self.xB, self.yB), 5)

    #endregion
