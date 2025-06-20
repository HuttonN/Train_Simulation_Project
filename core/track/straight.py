import pygame
import math

class StraightTrack(pygame.sprite.Sprite):
    """
    Represents a straight track piece that always connects the center of its own cell
    to the center of an adjacent cell in the specified compass direction.
    """
    ALLOWED_DIRECTIONS = {"N", "S", "E", "W", "NE", "SE", "SW", "NW"}

    def __init__(self, grid, row, col, compass, track_id=None, branch="1"):
        super().__init__()
        self.grid = grid
        self.row = row
        self.col = col
        self.track_id = track_id or f"{row},{col}_{compass}"
        self.branch = branch
        self.compass = compass.upper()
        if self.compass not in self.ALLOWED_DIRECTIONS:
            raise ValueError(f"Compass '{self.compass}' not allowed. Must be one of {self.ALLOWED_DIRECTIONS}")

        # Set length so the track spans exactly from center to center of two adjacent cells
        if self.compass in {"N", "S", "E", "W"}:
            self.length = self.grid.cell_size
        else:
            self.length = self.grid.cell_size * math.sqrt(2)

    def draw_track(self, surface, color=(200, 180, 60)):
        x0, y0 = self.grid.grid_to_screen(self.row, self.col)
        dx, dy = {
            "N":  (0, -self.length),
            "S":  (0, self.length),
            "E":  (self.length, 0),
            "W":  (-self.length, 0),
            "NE": (self.length / math.sqrt(2), -self.length / math.sqrt(2)),
            "SE": (self.length / math.sqrt(2), self.length / math.sqrt(2)),
            "SW": (-self.length / math.sqrt(2), self.length / math.sqrt(2)),
            "NW": (-self.length / math.sqrt(2), -self.length / math.sqrt(2)),
        }[self.compass]
        x1 = x0 + dx
        y1 = y0 + dy
        pygame.draw.line(surface, color, (x0, y0), (x1, y1), 5)

    def get_next_cell(self):
        # Returns (row, col) of next cell in compass direction
        delta = {
            "N":  (-1, 0),
            "S":  (1, 0),
            "E":  (0, 1),
            "W":  (0, -1),
            "NE": (-1, 1),
            "SE": (1, 1),
            "SW": (1, -1),
            "NW": (-1, -1),
        }[self.compass]
        return self.row + delta[0], self.col + delta[1]

    def get_angle(self):
        # Used for train orientation
        return {
            "E": 0,
            "NE": -45,
            "N": -90,
            "NW": -135,
            "W": 180,
            "SW": 135,
            "S": 90,
            "SE": 45
        }[self.compass]
