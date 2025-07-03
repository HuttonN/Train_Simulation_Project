import pygame
import math

class Carriage(pygame.sprite.Sprite):

    def __init__(self, grid, colour = "blue", passengers=[], max_capacity=10):
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
        DOT_RADIUS = 2
        DOT_DIAM = DOT_RADIUS * 2
        DOT_GAP = 1
        GRID_CELL = DOT_DIAM + DOT_GAP

        dots_per_row = int(16 // GRID_CELL)
        dots_per_col = int(53 // GRID_CELL)

        max_dots = dots_per_row * dots_per_col
        n_passengers = min(len(self.passengers), max_dots)

        dot_positions = []
        for idx in range(n_passengers):
            row = idx // dots_per_row
            col = idx % dots_per_row
            # Grid position, origin at center of platform
            x = -53/2 + GRID_CELL/2 + row * GRID_CELL
            y = -16/2 + GRID_CELL/2 + col * GRID_CELL

            # Rotate to platform orientation
            s = math.sin(math.radians(angle))
            c = math.cos(math.radians(angle))
            rot_x = c * x - s * y
            rot_y = s * x + c * y
            screen_x = int(base_x + rot_x)
            screen_y = int(base_y + rot_y)
            dot_positions.append((screen_x, screen_y))

        for idx, pos in enumerate(dot_positions):
            passenger = self.passengers[idx]
            pygame.draw.circle(surface, passenger.colour, pos, DOT_RADIUS)

    def draw(self, surface):
        if self.image is None:
            raise RuntimeError("Carriage image not loaded.")
        x, y = self.position
        print(f"Drawing carriage at {x}, {y}, angle={self.angle}")
        self.rotated_image = pygame.transform.rotate(self.image, -self.angle)
        self.image_rect = self.rotated_image.get_rect(center=(x, y))
        surface.blit(self.rotated_image, self.image_rect)
        if len(self.passengers)>0:
            self.draw_passengers_in_carriage(
                surface, x, y, self.angle
            )
