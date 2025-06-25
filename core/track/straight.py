import pygame
import math

from core.track.base import BaseTrack

class StraightTrack(BaseTrack):
    """
    Represents a straight track piece between two grid cell centers.
    Endpoints are labeled 'A' and 'B'.
    """

    ENDPOINTS = ["A", "B"]

    # --- Constructor ---------------------------------------------------------

    def __init__(self, grid, start_row, start_col, end_row, end_col, track_id=None):
        super().__init__()
        self.grid = grid
        self.start_row = start_row
        self.start_col = start_col
        self.end_row = end_row
        self.end_col = end_col
        self.track_id = track_id or f"Straight:{start_row},{start_col}->{end_row},{end_col}"
        
        # Get pixel coordinates of cell centers
        self.x0, self.y0 = self.grid.grid_to_screen(start_row, start_col)
        self.x1, self.y1 = self.grid.grid_to_screen(end_row, end_col)
        self.angle = math.degrees(math.atan2(self.y1 - self.y0, self.x1 - self.x0))

        # DRY endpoint maps
        self._endpoint_coords = {
            "A": (self.x0, self.y0),
            "B": (self.x1, self.y1)
        }
        self._endpoint_grids = {
            "A": (self.start_row, self.start_col),
            "B": (self.end_row, self.end_col)
        }

    # --- Endpoint Methods ----------------------------------------------------

    def get_endpoints(self):
        return ["A", "B"]
    
    def get_endpoint_coords(self, endpoint):
        """Returns pixel coordinates for the requested endpoint label."""
        if endpoint == "A":
            return self.x0, self.y0
        elif endpoint == "B":
            return self.x1, self.y1
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
        
    # --- Geometry Methods ----------------------------------------------------

    def get_angle(self, entry_ep, exit_ep):
        """Returns angle of travel when moving from entry_ep to exit_ep."""
        if entry_ep == "A" and exit_ep == "B":
            return self.angle
        elif entry_ep == "B" and exit_ep == "A":
            return (self.angle + 180) % 360
        else:
            raise ValueError("Invalid endpoint pair for straight track.")
        
    # --- Rendering Methods ----------------------------------------------------

    def draw_track(self, surface, color=(200, 180, 60)):
        """Draws the straight track on the given surface"""
        pygame.draw.line(surface, color, (self.x0, self.y0), (self.x1, self.y1), 5)