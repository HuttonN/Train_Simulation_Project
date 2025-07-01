import pygame
import math

from core.track.base import BaseTrack

class StraightTrack(BaseTrack):
    """
    Represents a straight track piece between two grid cell centers.
    Endpoints are labeled 'A' and 'B'.
    """

    ENDPOINTS = ["A", "B"]

    #region --- Constructor ---------------------------------------------------------

    def __init__(self, grid, start_row, start_col, end_row, end_col, track_id=None):
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

    def get_endpoints(self):
        return ["A", "B"]
    
    def get_endpoint_coords(self, endpoint):
        """Returns pixel coordinates for the requested endpoint label."""
        if endpoint == "A":
            return self.xA, self.yA
        elif endpoint == "B":
            return self.xB, self.yB
        else:
            raise ValueError("Unknown endpoint for straight track.")

    def get_endpoint_grid(self, endpoint):
        """Returns grid coordinates for the requested endpoint label."""
        if endpoint == "A":
            return self.start_row, self.start_col
        elif endpoint == "B":
            return self.end_row, self.end_col
        else:
            raise ValueError("Unknown endpoint for straight track.")
        
    #endregion

    #region --- Geometry Methods ----------------------------------------------------

    def get_angle(self, entry_ep, exit_ep):
        """Returns angle of travel when moving from entry_ep to exit_ep."""
        if entry_ep == "A" and exit_ep == "B":
            return self.angle
        elif entry_ep == "B" and exit_ep == "A":
            return (self.angle + 180) % 360
        else:
            raise ValueError("Invalid endpoint pair for straight track.")
        
    def get_point_and_angle(self, t, direction):
        """
        For compatibility with base API. Straight tracks do not support Bezier curves,
        so this returns interpolated point and angle along the straight segment.
        """
        if direction == "B_to_A":
            t = 1-t

        x = (1-t) * self.xA + t * self.xB
        y = (1-t) * self.yA + t * self.yB

        angle = self.get_angle("A", "B")
        return (x, y), angle
        
    def move_along_segment(self, train, speed, entry_ep, exit_ep):
        """
        Moves the train along the segment between the given endpoints.
        (Consistent API with StraightTrack/CurvedTrack)
        """
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
        Returns True if the train has arrived at the exit endpoint.
        """
        tx, ty = self.get_endpoint_coords(exit_ep)
        return abs(train.x - tx) < 1 and abs(train.y - ty) < 1

    #endregion
        
    #region --- Rendering Methods ---------------------------------------------------

    def draw_track(self, surface, color=(200, 180, 60)):
        """Draws the straight track on the given surface"""
        pygame.draw.line(surface, color, (self.xA, self.yA), (self.xB, self.yB), 5)

    #endregion

    def get_length(self, entry_ep, exit_ep):
        x1, y1 = self.get_endpoint_coords(entry_ep)
        x2, y2 = self.get_endpoint_coords(exit_ep)
        return ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5
    
    def get_position_at_distance(self, entry_ep, exit_ep, s):
        length = self.get_length(entry_ep, exit_ep)
        t = s / length if length != 0 else 0
        if t > 1: t = 1
        x1, y1 = self.get_endpoint_coords(entry_ep)
        x2, y2 = self.get_endpoint_coords(exit_ep)
        x = (1 - t) * x1 + t * x2
        y = (1 - t) * y1 + t * y2
        angle = self.get_angle(entry_ep, exit_ep)
        return (x, y, angle)
