import pygame
from core.track.straight import StraightTrack
from core.track.curve import CurvedTrack
from core.track.junction import JunctionTrack
from core.track.station import StationTrack
from core.track.double_curve_junction import DoubleCurveJunctionTrack
from core.route import Route
from core.trains.carriage import Carriage

class Train(pygame.sprite.Sprite):
    """
    Represents a train that can traverse any track piece, in any direction.
    Uses entry/exit endpoints to abstract direction.
    """

    MAX_CARRIAGES = 5

    def __init__(self, row, col, grid, carriages, track_objects, colour="red", player_controlled=False, current_segment = None):
        super().__init__()
        self.row = row
        self.col = col
        self.grid = grid
        self.x, self.y = self.grid.grid_to_screen(row, col)
        self.colour = colour
        self.track_objects = track_objects
        self.player_controlled = player_controlled
        self.position_history = []

        self.route = None
        self.current_track = None
        self.entry_ep = None
        self.exit_ep = None
        self.current_segment = current_segment

        self.speed = 3
        self.angle = 0
        self.s_on_curve = 0      # For curves
        self.curve_speed = 3
        self.reverse = False     # Whether traversing in reverse direction

        self.stopped = False          # Used for station (timed) stops
        self.stop_start_time = 0
        self.stop_duration = 0

        self.waiting_for_junction = False  # Used for event-driven junction wait

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

    #------------------ Route and Movement -----------------------

    def set_route(self, route):
        """Assign a new route and reset route progress."""
        self.route = route
        step = self.route.get_current_step()
        if step:
            self.enter_track_piece(step["track_obj"], step["entry"], step["exit"])
            if step["track_obj"].segment:
                self.current_segment = step["track_obj"].segment
                self.current_segment.request_entry(self)

    def travel_route(self):
        """Handle movement along the route, pausing for junctions or stations if needed."""
        if self.stopped or self.waiting_for_junction or self.route is None or self.route.is_finished():
            return

        # ---- Non-blocking Junction Wait ----
        if isinstance(self.current_track, (JunctionTrack, DoubleCurveJunctionTrack)):
            if not self.current_track.can_proceed(self.entry_ep, self.exit_ep):
                self.waiting_for_junction = True
                self.speed = 0
                return  # Wait for junction
            else:
                self.waiting_for_junction = False
                self.speed = 3  # or your default

        self.move_along_track_piece()

        if self.at_track_piece_end():
            # Timed stop at station
            if isinstance(self.current_track, StationTrack):
                self.stop(1000)  # Milliseconds at station
                self.alight_passengers_at_station(self.current_track)
                self.board_passengers_from_station(self.current_track)
            
            next_index = self.route.current_index + 1
            if next_index < len(self.route.steps):
                next_step = self.route.steps[next_index]
                next_track = next_step["track_obj"]

                # ----- JUNCTION INTERLOCK LOGIC -----
                # If next track is a junction, attempt to atomically reserve the junction and the segment *after* it
                if isinstance(next_track, (JunctionTrack, DoubleCurveJunctionTrack)):
                    exit_index = next_index + 1
                    if exit_index < len(self.route.steps):
                        exit_step = self.route.steps[exit_index]
                        exit_segment = exit_step["track_obj"].segment
                        if not next_track.can_reserve_junction(self, exit_segment):
                            print(f"Train {id(self)} blocked: cannot reserve junction {getattr(next_track, 'track_id', '')} and exit segment {getattr(exit_segment, 'name', '')}")
                            return  # Wait until both are free
                    else:
                        # At end of route; just check junction
                        if next_track.occupied_by is not None and next_track.occupied_by != self:
                            print(f"Train {id(self)} blocked: junction {getattr(next_track, 'track_id', '')} is occupied")
                            return

                # --- Attempt normal segment transition if not a junction ---
                if not self.handle_segment_transition(next_track):
                    print(f"Train {id(self)} waiting: cannot advance, next segment is occupied.")
                    return  # Blocked—do NOT advance or move

                # If we are LEAVING a junction, release its lock now
                if isinstance(self.current_track, (JunctionTrack, DoubleCurveJunctionTrack)):
                    self.current_track.release_junction(self)

                self.route.advance()
                print(f"Train {id(self)} advancing to next route step.")
                self.enter_track_piece(next_track, next_step["entry"], next_step["exit"])
            else:
                self.stop()


    def enter_track_piece(self, track_piece, entry_ep, exit_ep):
        """Called when entering a new track_piece; resets curve/angle state."""
        print(f"Train {id(self)} entering track {track_piece.track_id} (segment: {getattr(track_piece.segment, 'name', None)})")
        self.current_track = track_piece
        self.entry_ep = entry_ep
        self.exit_ep = exit_ep

        grid_pos = track_piece.get_endpoint_grid(entry_ep)
        pixel_pos = track_piece.get_endpoint_coords(entry_ep)
        self.row, self.col = grid_pos
        self.x, self.y = pixel_pos

        if isinstance(self.current_track, DoubleCurveJunctionTrack):
            if {self.entry_ep, self.exit_ep} == {"A", "L"}:
                self.s_on_curve = 0 if self.entry_ep == "A" else getattr(track_piece, "left_curve_length", 0)
            else:
                self.s_on_curve = 0 if self.entry_ep == "A" else getattr(track_piece, "right_curve_length", 0)
        else: 
            self.s_on_curve = 0 if self.entry_ep == "A" else getattr(track_piece, "curve_length", 0)
        self.angle = track_piece.get_angle(entry_ep, exit_ep)

    #------------------- Station Stops ---------------------------

    def stop_at_station(self):
        """Handle stops at station tracks (uses timer)."""
        step = self.route.get_current_step()
        if (
            isinstance(self.current_track, StationTrack)
            and step is not None
            and step.get("stop?", False)
            and self.at_track_piece_end()
        ):
            print(f"Train stopping at station: {self.current_track.name}")
            self.stop(2000)
            self.current_track.board_passengers_onto_train(self)
            self.start()  # Remove if you want to wait at the station for the full duration

    def stop(self, duration=None):
        """Halts the train for a timed stop (e.g. station)."""
        self.stopped = True
        self.stop_start_time = pygame.time.get_ticks()
        self.stop_duration = duration
        self.speed = 0

    def start(self):
        """Resume train movement after timed stop."""
        self.stopped = False
        self.speed = 3

    #------------------ Core Movement ---------------------------

    def move_along_track_piece(self):
        self.current_track.move_along_track_piece(self, self.speed, self.entry_ep, self.exit_ep)

    def at_track_piece_end(self):
        return self.current_track.has_reached_endpoint(self, self.exit_ep)

    #------------------ Pygame Update Loop ----------------------

    def update(self, surface):
        """
        Called every frame. Handles all pause logic, movement, and drawing.
        """
        # Handle station stops (timer)
        if self.stopped:
            if self.stop_duration is not None:
                now = pygame.time.get_ticks()
                if now - self.stop_start_time >= self.stop_duration:
                    self.start()
                else:
                    self.draw(surface)
                    return

        # Handle junction waits (event-driven, no timer)
        if self.waiting_for_junction:
            # Check if allowed to proceed now
            if isinstance(self.current_track, (JunctionTrack, DoubleCurveJunctionTrack)) and self.current_track.can_proceed(self.entry_ep, self.exit_ep):
                self.waiting_for_junction = False
                self.speed = 3
            else:
                self.draw(surface)
                return

        # Main movement logic
        self.travel_route()
        self.stop_at_station()
        self.record_position_history()
        self.update_carriages(surface)
        # self.prune_position_history()
        self.draw(surface)

    #----------------- Rendering Methods ------------------------

    def draw(self, surface):
        """Draws the train, rotated according to its current angle."""
        if self.image is None:
            raise RuntimeError("Train image not loaded.")
        self.rotated_image = pygame.transform.rotate(self.image, -self.angle)
        self.image_rect = self.rotated_image.get_rect(center=(self.x, self.y))
        surface.blit(self.rotated_image, self.image_rect)

    #----------------- Utility & Carriage Methods --------------

    def at_cell_center(self):
        expected_x, expected_y = self.grid.grid_to_screen(self.row, self.col)
        return abs(self.x - expected_x) < 1 and abs(self.y - expected_y) < 1

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
        CARRIAGE_LENGTH = 53  # px per carriage (update if needed)
        target_distance = (carriage_index + 1) * CARRIAGE_LENGTH

        # Try to get position from position history
        total_distance = 0
        last_pos = (self.x, self.y)
        for pos in self.position_history:
            dist = ((pos[0] - last_pos[0]) ** 2 + (pos[1] - last_pos[1]) ** 2) ** 0.5
            total_distance += dist
            if total_distance >= target_distance:
                return pos
            last_pos = pos

        # If not enough history, walk back through track network
        distance_left = target_distance - total_distance
        current_track = self.current_track
        entry_ep = self.entry_ep

        while distance_left > 0:
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

            seg_length = prev_track.get_length(prev_entry_ep, entry_ep)
            if distance_left <= seg_length:
                s = seg_length - distance_left
                x, y, angle = prev_track.get_position_at_distance(prev_entry_ep, entry_ep, s)
                return (x, y, angle)
            else:
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
        return len(self.carriages) < self.MAX_CARRIAGES

    #----------------- Passenger Methods -----------------------

    def board_passengers_from_station(self, station):
        waiting = station.get_waiting_passengers()
        eligible = [p for p in waiting if self.route.stops_at_station(p.destination_station.track_id)]
        boarded = []
        for p in eligible:
            for carriage in self.carriages:
                if carriage.has_space():
                    carriage.assign_seat(p)
                    p.board(self, carriage)
                    boarded.append(p)
                    break
        station.remove_passengers(boarded)

    def alight_passengers_at_station(self, station):
        for carriage in self.carriages:
            alighting = carriage.unload_passengers_to_station(station.track_id)
            for passenger in alighting:
                print(f"Passenger {passenger.id} alighting at station {station.track_id}")
                passenger.alight(station)

    def handle_segment_transition(self, next_track):
        next_segment = next_track.segment
        if next_segment != self.current_segment:
            if next_segment:  # Entering a new (non-junction) segment
                print(f"Train {id(self)} attempting to enter segment {next_segment.name} from {getattr(self.current_segment, 'name', None)}")
                if not next_segment.request_entry(self):
                    print(f"Train {id(self)} BLOCKED from entering segment {next_segment.name} (occupied by {getattr(next_segment.occupied_by, 'colour', None)})")
                    self.stopped = True
                    self.speed = 0
                    return False
                if self.current_segment:
                    print(f"Train {id(self)} leaving segment {self.current_segment.name}")
                    self.current_segment.leave(self)
                self.current_segment = next_segment
            elif self.current_segment:  # Leaving a segment for a junction
                print(f"Train {id(self)} leaving segment {self.current_segment.name} for a junction")
                self.current_segment.leave(self)
                self.current_segment = None
        return True
