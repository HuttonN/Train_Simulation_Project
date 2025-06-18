import pygame
import math

class StraightTrack(pygame.sprite.Sprite):
    """
    Represents a straight track piece of arbitrary length and orientation.
    """

    ALLOWED_DIRECTIONS = {"N", "S", "E", "W", "NE", "SW", "NW", "SE"}

    def __init__(self, track_id, prev_id, next_id, branch, length=75, compass="E"):
        """
        Initialize a StraightTrack piece.

        Arguments:
            track_id: Unique identifier for this piece.
            prev_id: ID of the previous track piece.
            next_id: ID of the next track piece.
            branch: Branch information if relevant.
            length: The length of the straight piece (default: 75).
            compass: Orientation of the track ("N", "E", "S", "W", "NE", "SW", "NW", "SE").
        """
        super().__init__()
        self.track_id = track_id
        self.prev_id = prev_id
        self.next_id = next_id
        self.branch = branch
        self.length = length
        self.compass = compass.upper()
        if self.compass not in self.ALLOWED_DIRECTIONS:
            raise ValueError(f"Compass '{self.compass}' not allowed. Must be one of {self.ALLOWED_DIRECTIONS}")
        self.x = None
        self.y = None
        self.occupied = False

    def set_occupied(self, occupied=True):
        self.occupied = occupied

    def is_occupied(self):
        return self.occupied

    def get_id(self):
        return self.track_id

    def get_prev_id(self):
        return self.prev_id

    def get_next_id(self):
        return self.next_id

    def get_coordinates(self):
        return self.x, self.y

    def set_coordinates(self, x, y):
        self.x = x
        self.y = y

    def get_branch(self):
        return self.branch

    def get_type(self):
        return "StraightTrack"

    def adjust_compass(self, compass):
        # For straight tracks, compass does not change
        return compass

    def draw_track(self, x, y, surface, track_colour=(255, 128, 0)):
        """
        Draw the straight track piece at (x, y) using its compass orientation.

        Args:
            x (float): Start X position.
            y (float): Start Y position.
            surface (pygame.Surface): Surface to draw on.
            track_colour (tuple): RGB color for the track line.

        Returns:
            tuple: (end_x, end_y), the end coordinates of the track.
        """
        line_width = 5
        length = self.length
        true_diagonal = math.sqrt(2 * (length ** 2)) / 2

        direction_map = {
            "N":  (0, -length),
            "S":  (0, length),
            "E":  (length, 0),
            "W":  (-length, 0),
            "NE": (true_diagonal, -true_diagonal),
            "SW": (-true_diagonal, true_diagonal),
            "NW": (-true_diagonal, -true_diagonal),
            "SE": (true_diagonal, true_diagonal),
        }

        dx, dy = direction_map[self.compass]
        end_x, end_y = x + dx, y + dy

        pygame.draw.line(surface, track_colour, (x, y), (end_x, end_y), line_width)
        self.set_coordinates(x, y)

        return end_x, end_y

    def covered_cells(self, grid):
        """
        Returns a list of (row, col) cells covered by this track, given a grid object.
        (Assumes x, y have been set to the grid start cell center.)
        """
        if self.x is None or self.y is None:
            return []
        row, col = grid.screen_to_grid(self.x, self.y)
        covered = [(row, col)]
        # Optionally, you could interpolate cells along the line for longer pieces
        # For now, just include the start cell
        return covered
