import pygame
from core.track.straight import StraightTrack
from core.track.curve import CurvedTrack
from core.track.junction import JunctionTrack  # For future use!

class Train(pygame.sprite.Sprite):
    """
    Represents a train that can traverse any track segment, in any direction.
    Uses entry/exit endpoints to abstract direction.
    """

    def __init__(self, row, col, grid, colour="red", player_controlled=False):
        super().__init__()
        self.row = row
        self.col = col
        self.grid = grid
        self.x, self.y = self.grid.grid_to_screen(row, col)
        self.colour = colour
        self.player_controlled = player_controlled
        self.current_track = None
        self.entry_ep = None
        self.exit_ep = None
        self.image = None
        self.rotated_image = None
        self.image_rect = None
        self.angle = 0
        self.s_on_curve = 0      # For curves
        self.curve_speed = 3
        self.reverse = False     # Whether traversing in reverse direction
        self.load_image()

    def enter_segment(self, track_piece, entry_ep, exit_ep):
        """
        Called when train enters a new track segment.
        Initializes direction, curve position, pixel/grid position, and orientation.
        """
        self.current_track = track_piece
        self.entry_ep = entry_ep
        self.exit_ep = exit_ep

        if isinstance(track_piece, StraightTrack):
            grid_pos = track_piece.get_endpoint_grid(entry_ep)
            pixel_pos = track_piece.get_endpoint_coords(entry_ep)
            self.row, self.col = grid_pos
            self.x, self.y = pixel_pos
            self.angle = track_piece.get_angle(entry_ep, exit_ep)
        elif isinstance(track_piece, CurvedTrack):
            grid_pos = track_piece.get_endpoint_grid(entry_ep)
            pixel_pos = track_piece.get_endpoint_coords(entry_ep)
            self.row, self.col = grid_pos
            self.x, self.y = pixel_pos
            if entry_ep == "A" and exit_ep == "B":
                self.s_on_curve = 0
            elif entry_ep == "B" and exit_ep == "A":
                self.s_on_curve = track_piece.curve_length
            else:
                raise ValueError("Invalid endpoint pair for CurvedTrack.")
            self.angle = track_piece.get_angle(entry_ep, exit_ep)
        elif isinstance(track_piece, JunctionTrack):
            grid_pos = track_piece.get_endpoint_grid(entry_ep)
            pixel_pos = track_piece.get_endpoint_coords(entry_ep)
            self.row, self.col = grid_pos
            self.x, self.y = pixel_pos
            # Set s_on_curve if entering on curve
            if {entry_ep, exit_ep} == {"A", "S"}:
                self.angle = track_piece.get_angle(entry_ep, exit_ep)
            elif {entry_ep, exit_ep} == {"A", "C"}:
                if entry_ep == "A":
                    self.s_on_curve = 0
                else:
                    self.s_on_curve = track_piece.curve_length
                self.angle = track_piece.get_angle(entry_ep, exit_ep)
            elif {entry_ep, exit_ep} == {"S", "A"}:
                self.angle = track_piece.get_angle(entry_ep, exit_ep)
            elif {entry_ep, exit_ep} == {"C", "A"}:
                if entry_ep == "C":
                    self.s_on_curve = track_piece.curve_length
                else:
                    self.s_on_curve = 0
                self.angle = track_piece.get_angle(entry_ep, exit_ep)
            else:
                # For unsupported pairs, just set angle toward exit
                self.angle = track_piece.get_angle(entry_ep, exit_ep)

    def move_along_segment(self, speed):
        """
        Move the train along its current track segment (straight, curve, or junction).
        Uses entry_ep and exit_ep to determine direction.
        """
        track = self.current_track
        if isinstance(track, StraightTrack):
            # Move toward exit endpoint
            target_grid = track.get_endpoint_grid(self.exit_ep)
            target_x, target_y = track.get_endpoint_coords(self.exit_ep)
            dx = target_x - self.x
            dy = target_y - self.y
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist > speed:
                self.x += dx / dist * speed
                self.y += dy / dist * speed
            else:
                self.x, self.y = target_x, target_y
                self.row, self.col = target_grid
        elif isinstance(track, CurvedTrack):
            direction = "A_to_B" if (self.entry_ep == "A" and self.exit_ep == "B") else "B_to_A"
            if direction == "A_to_B":
                self.s_on_curve = min(self.s_on_curve + speed, track.curve_length)
                t = track.arc_length_to_t(self.s_on_curve, direction="A_to_B")
            else:
                self.s_on_curve = max(self.s_on_curve - speed, 0)
                t = track.arc_length_to_t(self.s_on_curve, direction="B_to_A")
            (self.x, self.y), self.angle = track.get_point_and_angle(t, direction=direction)
            if direction == "A_to_B" and self.s_on_curve >= track.curve_length:
                self.row, self.col = track.get_endpoint_grid("B")
            elif direction == "B_to_A" and self.s_on_curve <= 0:
                self.row, self.col = track.get_endpoint_grid("A")
        elif isinstance(track, JunctionTrack):
            # Delegate all movement/direction logic to JunctionTrack
            track.move_along_segment(self, speed, self.entry_ep, self.exit_ep)

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
