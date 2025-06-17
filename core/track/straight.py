import pygame
import math

class StraightTrack(pygame.sprite.Sprite):
    """
    Represents a straight track piece of arbitrary length.
    """

    def __init__(self, track_id, prev_id, next_id, branch, length=75):
        """
        Initialise a StraightTrack piece.

        Arguments:
            track_id: Unique identifier for this piece.
            prev_id: ID of the previous track piece.
            next_id: ID of the next track piece.
            branch: Branch information if relevant.
            length: The length of the straight piece (default: 75).
        """
        super().__init__()
        self.track_id = track_id
        self.prev_id = prev_id
        self.next_id = next_id
        self.branch = branch
        self.length = length
        self.x = None
        self.y = None
        self.occupied = False

    def set_occupied(self, occupied=True):
        """Set whether this piece is occupied by a train."""
        self.occupied = occupied

    def is_occupied(self):
        """Return True if this piece is occupied by a train."""
        return self.occupied

    def get_id(self):
        """Return this track's unique ID."""
        return self.track_id

    def get_prev_id(self):
        """Return the previous track's ID."""
        return self.prev_id

    def get_next_id(self):
        """Return the next track's ID."""
        return self.next_id

    def get_coordinates(self):
        """Return (x, y) coordinates (if set)."""
        return self.x, self.y

    def set_coordinates(self, x, y):
        """Set the piece's (x, y) position."""
        self.x = x
        self.y = y

    def get_branch(self):
        """Return the branch identifier."""
        return self.branch

    def get_type(self):
        """Return the type of this track piece."""
        return "StraightTrack"

    def adjust_compass(self, compass):
        """For a straight, the compass usually doesn't change."""
        return compass

    def draw_track(self, x, y, compass, surface, track_colour=(255, 128, 0)):
        """
        Draw the straight track piece at (x, y) in the given compass direction.

        Args:
            x (float): Start X position.
            y (float): Start Y position.
            compass (str): One of N, NE, E, SE, S, SW, W, NW.
            surface (pygame.Surface): Surface to draw on.
            track_colour (tuple): RGB color for the track line.

        Returns:
            tuple: (new_x, new_y), the end coordinates of the track.
        """
        line_width = 5
        length = self.length
        true_diagonal = math.sqrt(2 * (length ** 2)) / 2

        directions = {
            "N":  (0, -length),
            "NE": (true_diagonal, -true_diagonal),
            "E":  (length, 0),
            "SE": (true_diagonal, true_diagonal),
            "S":  (0, length),
            "SW": (-true_diagonal, true_diagonal),
            "W":  (-length, 0),
            "NW": (-true_diagonal, -true_diagonal)
        }

        dx, dy = directions.get(compass, (0, 0))
        end_x, end_y = x + dx, y + dy

        # Draw the track
        pygame.draw.line(surface, track_colour, (x, y), (end_x, end_y), line_width)
        self.set_coordinates(x, y)

        return end_x, end_y
