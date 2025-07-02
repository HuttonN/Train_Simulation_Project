import pygame

class Carriage(pygame.sprite.Sprite):

    def __init__(self, grid, colour = "blue", max_capacity=10):
        self.grid = grid
        self.position = (223,220)
        self.passengers = []
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

    def draw(self, surface):
        if self.image is None:
            raise RuntimeError("Carriage image not loaded.")
        x, y = self.position
        print(f"Drawing carriage at {x}, {y}, angle={self.angle}")
        self.rotated_image = pygame.transform.rotate(self.image, -self.angle)
        self.image_rect = self.rotated_image.get_rect(center=(x, y))
        surface.blit(self.rotated_image, self.image_rect)
