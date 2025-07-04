import pygame
from abc import ABC, abstractmethod

class BaseTrack(pygame.sprite.Sprite, ABC):
    """
    Abstract base class for all track pieces.

    Common interface:
      - track_id: unique string identifier (from JSON)
      - track_type: type string (e.g., "straight", "curve", "station", "junction")
      - ENDPOINTS: class-level list of valid endpoint labels
      - endpoint_coords: dict mapping endpoint -> (x, y)
      - endpoint_grids: dict mapping endpoint -> (row, col)
      - connections: dict mapping endpoint -> connection info (set after construction)

    Subclasses must implement geometry and movement methods.
    """

    ENDPOINTS = []

    def __init__(self, grid, track_id, track_type):
        super().__init__()
        self.grid = grid
        self.track_id = track_id
        self.track_type = track_type
        self.connections = {} # Will be set by loader after initialisation

    def get_endpoints(self):
        """Returns endpoint labels as a class-level constant"""
        return self.ENDPOINTS
    
    def get_endpoint_coords(self, endpoint):
        """
        Return pixel (x, y) coordinates for a given endpoint label.
        Raises ValueError if endpoint is not valid for this track piece.
        """
        if endpoint not in self.ENDPOINTS:
            raise ValueError(
                f"Unknown endpoint '{endpoint}' for {self.__class__.__name__} (ID: {self.track_id})."
            )
        return self.endpoint_coords[endpoint]
    
    def get_endpoint_grid(self, endpoint):
        """
        Return grid (row, col) coordinates for a given endpoint label.
        Raises ValueError if endpoint is not valid for this track piece.
        """
        if endpoint not in self.ENDPOINTS:
            raise ValueError(
                f"Unknown endpoint '{endpoint}' for {self.__class__.__name__} (ID: {self.track_id})."
            )
        return self.endpoint_grids[endpoint]

    @abstractmethod
    def get_angle(self, entry_ep, exit_ep):
        """Return angle in degrees when travelling from entry to exit."""
        pass

    @abstractmethod
    def move_along_segment(self, train, speed, entry_ep, exit_ep):
        """Advance the train along track segment."""
        pass

    @abstractmethod
    def get_point_and_angle(self, t, direction):
        """Return a point and angle along a curve or segment (if applicable)."""
        pass

    def has_reached_endpoint(self, train, exit_ep):
        """Check if the train has reached the exit endpoint on this track."""
        pass
    
    def __repr__(self):
        return f"<{self.__class__.__name__} id='{self.track_id}' type='{self.track_type}'>"