"""
train.py

Defines the Train class, representing a train object in the simulation.
Trains are grid-aligned, move along track pieces (including curves), and update their position and orientation accordingly.
"""

import pygame
from core.track.curve import CurvedTrack
from core.track.junction import JunctionTrack

class Train(pygame.sprite.Sprite):
    """
    Represents a train in the simulation.
    Uses track's compass for orientation.
    """

    def __init__(self, row, col, grid, colour="red", player_controlled=False):
        """
        Initialise a Train object.

        Arguments:
            row: Initial grid row.
            col: Initial grid column.
            grid: Reference to the grid object.
            colour: Train color for image asset (default "red").
            player_controlled: Is this train player-controlled? (currently a placeholder)
        """
        super().__init__()
        self.row = row
        self.col = col
        self.grid = grid
        self.x, self.y = self.grid.grid_to_screen(row, col)
        self.colour = colour
        self.player_controlled = player_controlled
        self.current_track = None
        self.next_track = None
        self.image = None
        self.rotated_image = None
        self.image_rect = None
        self.angle = 0
        self.s_on_curve = 0 # Distance along current curve (if on curved track)
        self.curve_speed = 3 # Speed along curve
        self.load_image()

    def set_current_track(self, track_piece):
        """
        Set the current track piece for the train and update angle.

        Arguments:
            track_piece: The current track piece object.
        """
        self.current_track = track_piece
        self.angle = track_piece.get_angle() if track_piece else 0

        from core.track.curve import CurvedTrack
        if isinstance(track_piece, CurvedTrack):
            self.s_on_curve = 0

    def move_along_straight(self, target_row, target_col, speed=3):
        """
        Move the train towards the target grid cell at a given speed.

        Arguments:
            target_row: Target grid row.
            target_col: Target grid column.
            speed: Pixels per frame.
        """
        target_x, target_y = self.grid.grid_to_screen(target_row, target_col)
        dx = target_x - self.x
        dy = target_y - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist > speed:
            self.x += dx / dist * speed
            self.y += dy / dist * speed
        else:
            self.x, self.y = target_x, target_y
            self.row, self.col = target_row, target_col

    def move_along_curve(self, curved_track, speed):
        self.s_on_curve = min(self.s_on_curve + speed, curved_track.curve_length)
        t = curved_track.arc_length_to_t(self.s_on_curve)
        (self.x, self.y), self.angle = curved_track.get_point_and_angle(t)
        if self.s_on_curve >= curved_track.curve_length:
            self.row, self.col = curved_track.end_row, curved_track.end_col

    def move_along_segment(self, track, speed):
        if isinstance(track, CurvedTrack):
            self.move_along_curve(track, speed)
        if isinstance(track, JunctionTrack):
            if track.branch_activated:
                self.move_along_curve(CurvedTrack(track.grid, track.start_row, track.start_col, track.curve_control_row, track.curve_control_col, track.curve_end_row, track.curve_end_col), speed)
            else:
                self.move_along_straight(track.straight_end_row, track.straight_end_col, speed)
        else:
            self.move_along_straight(track.end_row, track.end_col, speed)

    def draw(self, surface):
        if self.image is None:
            raise RuntimeError("Train image not loaded.")
        self.rotated_image = pygame.transform.rotate(self.image, -self.angle)
        self.image_rect = self.rotated_image.get_rect(center=(self.x, self.y))
        surface.blit(self.rotated_image, self.image_rect)

    def load_image(self):
        self.image = pygame.image.load(
            f"assets/images/train_{self.colour}.png"
        ).convert_alpha()

    def at_cell_center(self):
        expected_x, expected_y = self.grid.grid_to_screen(self.row, self.col)
        return abs(self.x - expected_x) < 1 and abs(self.y - expected_y) < 1
    

    
