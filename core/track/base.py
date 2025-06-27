import pygame
from abc import ABC, abstractmethod

class BaseTrack(pygame.sprite.Sprite, ABC):
    """
    Base class for all track pieces, providing common endpoint methods.
    Subclasses must define:
      - ENDPOINTS: list of valid endpoint labels
      - _endpoint_coords: dict mapping endpoint -> (x, y)
      - _endpoint_grids: dict mapping endpoint -> (row, col)
    """

    ENDPOINTS = []

    def __init__(self):
        super().__init__()

    def get_endpoints(self):
        """Returns endpoint labels as a class-level constant"""
        return self.ENDPOINTS
    
    @abstractmethod
    def get_endpoint_coords(self, endpoint):
        """Returns (x, y) pixel coordinates for the given endpoint."""
        pass

    @abstractmethod
    def get_endpoint_grid(self, endpoint):
        """Returns (row, col) grid coordinates for the given endpoint."""
        pass

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