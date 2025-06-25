import pygame
from core.track.straight import StraightTrack
from core.track.curve import CurvedTrack
from core.track.junction import JunctionTrack  # For future use!

class Train(pygame.sprite.Sprite):
    """
    Represents a train that can traverse any track segment, in any direction.
    Uses entry/exit endpoints to abstract direction.
    """

    # --- Constructor ---------------------------------------------------------

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

        self.speed = 3
        self.angle = 0
        self.s_on_curve = 0      # For curves
        self.curve_speed = 3
        self.reverse = False     # Whether traversing in reverse direction
        self.stopped = False

        self.image = None
        self.rotated_image = None
        self.image_rect = None
        self.load_image()

    # --- Start/Stop Methods --------------------------------------------------

    def stop(self):
        self.stopped = True
        self.speed = 0

    def start(self):
        self.stopped = False
        self.speed = 3

    # --- Control/Routing Methods ---------------------------------------------

    def request_junction_branch(self):
        if isinstance(self.current_track, JunctionTrack):
            junction = self.current_track
            if not junction.is_branch_set_for(self.entry_ep, self.exit_ep):
                if {self.entry_ep, self.exit_ep} == {"A", "C"}:
                    self.stop()
                    junction.activate_branch()
                    self.start()
                elif {self.entry_ep, self.exit_ep} == {"A", "C"}:
                    self.stop()
                    junction.deactivate_branch()
                    self.start()

    # --- Segment Transition Methods ------------------------------------------

    def enter_segment(self, track_piece, entry_ep, exit_ep):
        """
        Called when train enters a new track segment.
        Initialises direction, curve position, pixel/grid position, and orientation.
        """
        self.current_track = track_piece
        self.entry_ep = entry_ep
        self.exit_ep = exit_ep

        grid_pos = track_piece.get_endpoint_grid(entry_ep)
        pixel_pos = track_piece.get_endpoint_coords(entry_ep)
        self.row, self.col = grid_pos
        self.x, self.y = pixel_pos

        if isinstance(track_piece, StraightTrack):
            self.angle = track_piece.get_angle(entry_ep, exit_ep)

        elif isinstance(track_piece, CurvedTrack):
            # Set curve position depending on direction
            if entry_ep == "A" and exit_ep == "B":
                self.s_on_curve = 0
            elif entry_ep == "B" and exit_ep == "A":
                self.s_on_curve = track_piece.curve_length
            else:
                raise ValueError("Invalid endpoint pair for CurvedTrack.")
            self.angle = track_piece.get_angle(entry_ep, exit_ep)

        elif isinstance(track_piece, JunctionTrack):
            # Set s_on_curve if entering on curve
            if {entry_ep, exit_ep} == {"A", "S"} or {entry_ep, exit_ep} == {"S", "A"}:
                self.angle = track_piece.get_angle(entry_ep, exit_ep)
            elif {entry_ep, exit_ep} == {"A", "C"}:
                self.s_on_curve = 0 if entry_ep == "A" else track_piece.curve_length
                self.angle = track_piece.get_angle(entry_ep, exit_ep)
            else:
                self.angle = track_piece.get_angle(entry_ep, exit_ep)

    # --- Movement Methods ----------------------------------------------------

    def move_along_segment(self):
        """
        Move the train along its current track segment (straight, curve, or junction).
        Uses entry_ep and exit_ep to determine direction.
        """
        track = self.current_track

        if isinstance(track, StraightTrack):
            target_grid = track.get_endpoint_grid(self.exit_ep)
            target_x, target_y = track.get_endpoint_coords(self.exit_ep)
            dx = target_x - self.x
            dy = target_y - self.y
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist > self.speed:
                self.x += dx / dist * self.speed
                self.y += dy / dist * self.speed
            else:
                self.x, self.y = target_x, target_y
                self.row, self.col = target_grid

        elif isinstance(track, CurvedTrack):
            direction = "A_to_B" if (self.entry_ep == "A" and self.exit_ep == "B") else "B_to_A"
            if direction == "A_to_B":
                self.s_on_curve = min(self.s_on_curve + self.speed, track.curve_length)
                t = track.arc_length_to_t(self.s_on_curve, direction="A_to_B")
            else:
                self.s_on_curve = max(self.s_on_curve - self.speed, 0)
                t = track.arc_length_to_t(self.s_on_curve, direction="B_to_A")
            (self.x, self.y), self.angle = track.get_point_and_angle(t, direction=direction)
            if direction == "A_to_B" and self.s_on_curve >= track.curve_length:
                self.row, self.col = track.get_endpoint_grid("B")
            elif direction == "B_to_A" and self.s_on_curve <= 0:
                self.row, self.col = track.get_endpoint_grid("A")

        elif isinstance(track, JunctionTrack): # Maybe move logic from junction to train
            track.move_along_segment(self, self.speed, self.entry_ep, self.exit_ep)

    # --- Rendering Methods ---------------------------------------------------

    def draw(self, surface):
        """Draws the train, rotated according to its current angle."""
        if self.image is None:
            raise RuntimeError("Train image not loaded.")
        self.rotated_image = pygame.transform.rotate(self.image, -self.angle)
        self.image_rect = self.rotated_image.get_rect(center=(self.x, self.y))
        surface.blit(self.rotated_image, self.image_rect)

    # --- Utility Methods -----------------------------------------------------

    def load_image(self):
        """Loads the train image for the specified colour."""
        self.image = pygame.image.load(
            f"assets/images/train_{self.colour}.png"
        ).convert_alpha()

    def at_cell_center(self):
        """Returns True if the train is at the center of its current grid cell."""
        expected_x, expected_y = self.grid.grid_to_screen(self.row, self.col)
        return abs(self.x - expected_x) < 1 and abs(self.y - expected_y) < 1
    