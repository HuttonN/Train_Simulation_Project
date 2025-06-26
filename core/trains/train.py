import pygame
from core.track.straight import StraightTrack
from core.track.curve import CurvedTrack
from core.track.junction import JunctionTrack  # For future use!
from core.route import Route

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

        self.route = None
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

    # --- Start/Stop Methods (not currently used)--------------------------------------------------

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
        self.current_track.move_along_segment(self, self.speed, self.entry_ep, self.exit_ep)

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
    
    def set_route(self, route: Route):
        self.route = route
        self.route.current_index = 0

    def travel_route(self):
        if self.stopped or self.route is None or self.route.is_finished():
            return
        
        self.move_along_segment()

        if self.at_segment_end():
            self.route.advance()
            next_segment = self.route.get_current_segment()
            if next_segment:
                self.enter_segment(*next_segment)
            else:
                self.stop()

    def at_segment_end(self):
        if isinstance(self.current_track, StraightTrack):
            tx, ty = self.current_track.get_endpoint_coords(self.exit_ep)
            return abs(self.x - tx) < 1 and abs(self.y - ty) < 1
        
        elif isinstance(self.current_track, CurvedTrack):
            if self.entry_ep == "A":
                return self.s_on_curve >= self.current_track.curve_length
            else:
                return self.s_on_curve <= 0
            
        elif isinstance(self.current_track, JunctionTrack):
            return self.current_track.has_reached_endpoint(self,self.exit_ep)
        
        return False
    