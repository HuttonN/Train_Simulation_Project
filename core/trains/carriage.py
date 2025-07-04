import pygame
import math

class Carriage(pygame.sprite.Sprite):

    def __init__(self, grid, colour = "blue", passengers=[], max_capacity=30):
        self.grid = grid
        self.position = (223,220)
        self.passengers = passengers
        self.train = None
        self.index_in_train = None
        self.angle = 0
        self.colour = colour
        self.coupled = False
        self.max_capacity = max_capacity

        self.image = None
        self.rotated_image = None
        self.image_rect = None
        self.load_image()

        self.seat_grid = self.compute_seat_grid()

    def compute_seat_grid(self):
        DOT_RADIUS = 2
        DOT_DIAM = DOT_RADIUS * 2
        DOT_GAP = 1
        GRID_CELL = DOT_DIAM + DOT_GAP

        carriage_width = 16
        carriage_length = 53

        dots_per_row = int(carriage_width // GRID_CELL)
        dots_per_col = int(carriage_length // GRID_CELL)

        max_seats = dots_per_row * dots_per_col
        seat_positions = []
        for idx in range(min(self.max_capacity, max_seats)):
            row = idx // dots_per_row
            col = idx % dots_per_row
            # Grid position, origin at center of platform
            x = -carriage_length/2 + GRID_CELL/2 + row * GRID_CELL
            y = -carriage_width/2 + GRID_CELL/2 + col * GRID_CELL
            seat_positions.append((x,y))
        return seat_positions


    def load_image(self):
        """Loads the carriage image for the specified colour."""
        self.image = pygame.image.load(
            f"assets/images/carriage_blue.png"
        ).convert_alpha()

    def couple(self, train, index=None):
        self.train = train
        self.index_in_train = index
        self.coupled = True

    def uncouple(self):
        self.train = None
        self.index_in_train = None
        self.coupled = False

    def load(self, passenger_list):
        available = self.max_capacity - len(self.passengers)
        to_board = passenger_list[:available]
        self.passengers.extend(to_board)
        return passenger_list[available:]

    def empty(self):
        self.passengers = []

    def draw_passengers_in_carriage(self, surface, base_x, base_y, angle):
        """
        Draws passengers as coloured dots in the carriage.
        - base_x, base_y: center of the unrotated carriage
        - angle: rotation in degrees
        """

        for idx, passenger in enumerate(self.passengers):
            if idx >= len(self.seat_grid):
                break
            local_x, local_y = self.seat_grid[idx]
            s = math.sin(math.radians(angle))
            c = math.cos(math.radians(angle))
            rot_x = c * local_x - s * local_y
            rot_y = s * local_x + c * local_y
            screen_x = int(base_x + rot_x)
            screen_y = int(base_y + rot_y)
            pygame.draw.circle(surface, passenger.colour, (screen_x, screen_y), 2)

    def draw(self, surface):
        if self.image is None:
            raise RuntimeError("Carriage image not loaded.")
        x, y = self.position
        # print(f"Drawing carriage at {x}, {y}, angle={self.angle}")
        self.rotated_image = pygame.transform.rotate(self.image, -self.angle)
        self.image_rect = self.rotated_image.get_rect(center=(x, y))
        surface.blit(self.rotated_image, self.image_rect)
        if len(self.passengers)>0:
            self.draw_passengers_in_carriage(
                surface, x, y, self.angle
            )

    def has_space(self):
        return len(self.passengers) < self.max_capacity

    def assign_seat(self, passenger):
        """Assign passenger to lowest available seat, return seat index or None if full."""
        used_seats = set(getattr(p, "seat_index_in_carriage", None) for p in self.passengers)
        for idx in range(len(self.seat_grid)):
            if idx not in used_seats:
                passenger.seat_index_in_carriage = idx
                self.passengers.append(passenger)
                return idx
        return None  # No seat available

    def remove_passenger(self, passenger):
        """Remove a passenger from this carriage."""
        try:
            self.passengers.remove(passenger)
        except ValueError:
            pass  # Already removed