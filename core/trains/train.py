import pygame
from core.track.straight import StraightTrack
from core.track.curve import CurvedTrack
from core.track.junction import JunctionTrack
from core.track.station import StationTrack
from core.route import Route

from core.trains.carriage import Carriage

class Train(pygame.sprite.Sprite):
    """
    Represents a train that can traverse any track segment, in any direction.
    Uses entry/exit endpoints to abstract direction.
    """

    MAX_CARRIAGES = 5

    #region --- Constructor ---------------------------------------------------------

    def __init__(self, row, col, grid, carriages, track_objects, colour="red", player_controlled=False):
        super().__init__()
        self.row = row
        self.col = col
        self.grid = grid
        self.x, self.y = self.grid.grid_to_screen(row, col)
        self.colour = colour
        self.track_objects = track_objects
        self.player_controlled = player_controlled
        self.position_history =[]

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

        # Enforce max carriages
        if len(carriages) > self.MAX_CARRIAGES:
            raise ValueError(
                f"Cannot initialise train with {len(carriages)} carriages (max allowed is {self.MAX_CARRIAGES})"
            )
        self.carriages = list(carriages)

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
        step = self.route.get_current_step()
        if step:
            self.enter_segment(step["track_obj"], step["entry"], step["exit"])

    def travel_route(self):
        if self.stopped or self.route is None or self.route.is_finished():
            return

        self.move_along_segment()

        if self.at_segment_end():
            # Stop and board passengers if we're at a station
            if isinstance(self.current_track, StationTrack):
                print(f"Train stopping at station: {self.current_track.name}")
                self.stop()
                self.current_track.board_passengers_onto_train(self)
                self.start()
            # Now move on to the next segment
            self.route.advance()
            next_step = self.route.get_current_step()
            if next_step:
                self.enter_segment(next_step["track_obj"], next_step["entry"], next_step["exit"])
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

    def stop_at_station(self):
        """
        If train is at a station (with stop?=True at this segment and at segment end), 
        stop, board all eligible passengers, then resume.
        """
        # Check: Are we at a station, with stop? True, and at the end of the segment?
        step = self.route.get_current_step()
        if (
            isinstance(self.current_track, StationTrack)
            and step is not None
            and step.get("stop?", False)
            and self.at_segment_end()
        ):
            print(f"Train stopping at station: {self.current_track.name}")
            self.stop()
            # Board passengers from station onto this train
            self.current_track.board_passengers_onto_train(self)
            # (Optional: add a delay before starting, for realism. For now, resume instantly:)
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
    
    def update(self, surface):
        self.travel_route()
        self.stop_at_station()
        self.record_position_history()
        self.update_carriages(surface)
        # self.prune_position_history()

    def record_position_history(self):
        if not hasattr(self, "position_history"):
            self.position_history = []
        self.position_history.insert(0, (self.x, self.y, self.angle))

    def update_carriages(self, surface):
        for idx, carriage in enumerate(self.carriages):
            pos = self.get_carriage_position(idx)
            carriage.position = pos[:2]
            carriage.angle = pos[2]
            carriage.draw(surface)

    def get_carriage_position(self, carriage_index):
        """
        Returns (x, y, angle) for a carriage at a given index behind the train,
        stepping back through position history, then track network if needed.

        Assumes:
        - Each track object implements .get_length(entry_ep, exit_ep) and
        .get_position_at_distance(entry_ep, exit_ep, s)
        - Each track has a .connections dict for endpoint traversal
        - self.track_objects is a dict of all track objects by ID
        """
        CARRIAGE_LENGTH = 53  # px per carriage (update if needed)
        target_distance = (carriage_index + 1) * CARRIAGE_LENGTH

        # --- 1. Try to get position from position history ---
        total_distance = 0
        last_pos = (self.x, self.y)
        for pos in self.position_history:
            dist = ((pos[0] - last_pos[0]) ** 2 + (pos[1] - last_pos[1]) ** 2) ** 0.5
            total_distance += dist
            if total_distance >= target_distance:
                return pos
            last_pos = pos

        # --- 2. If not enough history, walk back through track network ---
        distance_left = target_distance - total_distance
        current_track = self.current_track
        entry_ep = self.entry_ep
        s_on_segment = 0  # Default: right at entry_ep

        # Optionally, if you store s_on_curve or equivalent, you might start at that value.
        # (But if at the start of simulation, just use 0.)

        while distance_left > 0:
            # Defensive: need connections data
            if not hasattr(current_track, "connections") or entry_ep not in current_track.connections:
                # Fallback: return oldest available position
                if self.position_history:
                    last_hist = self.position_history[-1]
                    return (last_hist[0], last_hist[1], last_hist[2])
                return (self.x, self.y, self.angle)
            # Step to previous track
            conn = current_track.connections[entry_ep]
            prev_track_id = conn["track"]
            prev_entry_ep = conn["endpoint"]
            prev_track = self.track_objects[prev_track_id]

            # Get the length of the previous segment (from prev_entry_ep to entry_ep)
            seg_length = prev_track.get_length(prev_entry_ep, entry_ep)
            if distance_left <= seg_length:
                s = seg_length - distance_left  # Position along the previous segment
                x, y, angle = prev_track.get_position_at_distance(prev_entry_ep, entry_ep, s)
                return (x, y, angle)
            else:
                # Move through the whole segment, step further back
                distance_left -= seg_length
                current_track = prev_track
                entry_ep = prev_entry_ep

        # Fallback (should not happen, but for safety)
        return (self.x, self.y, self.angle)


    def couple_carriage(self, carriage):
        if len(self.carriages) >= self.MAX_CARRIAGES:
            raise ValueError(
                f"Cannot couple carriage: already at maximum ({self.MAX_CARRIAGES})"
            )
        carriage.index_in_train = len(self.carriages)
        carriage.train = self
        carriage.coupled = True
        self.carriages.append(carriage)
        pos = self.get_carriage_position(carriage.index_in_train)
        carriage.x, carriage.y = pos[:2]
        carriage.angle = pos[2]

    def can_couple(self):
        """Return True if another carriage can be coupled to this train."""
        return len(self.carriages) < self.MAX_CARRIAGES