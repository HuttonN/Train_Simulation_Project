import pygame

class BaseTrack(pygame.sprite.Sprite):
    """
    Base class for all track pieces, providing common endpoint methods.
    Subclasses must define:
      - ENDPOINTS: list of valid endpoint labels
      - _endpoint_coords: dict mapping endpoint -> (x, y)
      - _endpoint_grids: dict mapping endpoint -> (row, col)
    """

    ENDPOINTS = []

    def get_endpoints(self):
        """Returns endpoint labels as a class-level constant"""
        return self.ENDPOINTS
    
    def get_endpoint_coords(self, endpoint):
        """Returns pixel coordinates for the requested endpoint label."""
        try:
            return self.endpoint_coords[endpoint]
        except KeyError:
            raise ValueError(f"Unknown endpoint: {endpoint}")

    def get_endpoint_grid(self, endpoint):
        """Returns grid coordinates for the requested endpoint label."""
        try:
            return self.endpoint_grids[endpoint]
        except KeyError:
            raise ValueError(f"Unknown endpoint: {endpoint}")