import pygame
from core.track.straight import StraightTrack
from core.track.curve import CurvedTrack
from core.track.junction import JunctionTrack
from core.route import Route

from core.trains.carriage import Carriage

class Train(pygame.sprite.Sprite):
    """
    Represents a train that can traverse any track segment, in any direction.
    Uses entry/exit endpoints to abstract direction.
    """

    #region --- Constructor ---------------------------------------------------------

    def __init__(self, row, col, grid, carriages, colour="red", player_controlled=False):
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

        self.carriages = carriages

        self.image = None
        self.rotated_image = None
        self.image_rect = None
        self.load_image()

    def load_image(self):
        """Loads the train image for the specified colour."""
        self.image = pygame.image.load(
            f"assets/images/train_{self.colour}.png"
        ).convert_alpha()

    #endregion

    #region --- Control/Routing Methods ---------------------------------------------

    def set_route(self, route):
        """
        Assigns a new route to the train and resets its route progress.

        Arguments:
            route: The sequence of track segments the train should follow.
        """
        self.route = route
        segment = self.route.get_current_segment()
        if segment:
            track, entry_ep, exit_ep = segment
            self.enter_segment(track, entry_ep, exit_ep)

    def travel_route(self):
        """
        Advances the train along its current route.

        Moves the train along its current segment, and transitions to the next one when complete.
        If the route is finished, the train stops.
        """
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

        self.s_on_curve = 0 if self.entry_ep == "A" else getattr(track_piece, "curve_length", 0)
        self.angle = track_piece.get_angle(entry_ep, exit_ep)

        self.request_junction_branch()


    def request_junction_branch(self):
        """
        Requests the correct branch configuration on a junction.

        If the train is on a junction and the desired entry/exit path is not active,
        it stops the train, activates the appropriate branch, and then resumes movement.
        """
        if isinstance(self.current_track, JunctionTrack):
            junction = self.current_track
            if not junction.is_branch_set_for(self.entry_ep, self.exit_ep):
                if {self.entry_ep, self.exit_ep} == {"A", "C"}:
                    self.stop()
                    junction.activate_branch()
                    self.start()
                elif {self.entry_ep, self.exit_ep} == {"A", "S"}:
                    self.stop()
                    junction.deactivate_branch()
                    self.start()

    def stop(self):
        """
        Halts the train by setting speed to zero and marking it as stopped.
        """
        self.stopped = True
        self.speed = 0

    def start(self):
        """
        Resumes the train's movement by restoring its default speed and clearing the stopped flag.
        """
        self.stopped = False
        self.speed = 3

    #endregion

    #region --- Movement Methods ----------------------------------------------------

    def move_along_segment(self):
        """
        Move the train along its current track segment (straight, curve, or junction).
        Uses entry_ep and exit_ep to determine direction.
        """
        self.current_track.move_along_segment(self, self.speed, self.entry_ep, self.exit_ep)

    def at_segment_end(self):
        """
        Checks whether the train has reached the end of its current segment.

        Returns:
            bool: True if the train has arrived at its exit endpoint, False otherwise.
        """
        return self.current_track.has_reached_endpoint(self,self.exit_ep)
    
    #endregion

    #region --- Rendering Methods ---------------------------------------------------

    def draw(self, surface):
        """Draws the train, rotated according to its current angle."""
        if self.image is None:
            raise RuntimeError("Train image not loaded.")
        self.rotated_image = pygame.transform.rotate(self.image, -self.angle)
        self.image_rect = self.rotated_image.get_rect(center=(self.x, self.y))
        surface.blit(self.rotated_image, self.image_rect)

    #endregion

    #region --- Utility Methods -----------------------------------------------------

    def at_cell_center(self):
        """Returns True if the train is at the center of its current grid cell."""
        expected_x, expected_y = self.grid.grid_to_screen(self.row, self.col)
        return abs(self.x - expected_x) < 1 and abs(self.y - expected_y) < 1
    
    #endregion

    def board_passengers(self, passenger_list):
        still_to_board = passenger_list
        for carriage in self.carriages:
            still_to_board = carriage.load(still_to_board)
            if not still_to_board:
                break
        return still_to_board