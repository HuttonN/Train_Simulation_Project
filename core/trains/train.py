import pygame

class Train(pygame.sprite.Sprite):
    """
    Represents a train object in the simulation.
    Handles position, drawing, movement logic, and control status.
    """

    def __init__(self, x, y, player_controlled=False):
        """
        Intialise the train object.

        Arguments:
            x: initial x position.
            y: initial y position.
            player_controlled: Initially False, but can be set to True for player controlled
        """

        self.x = x
        self.y = y
        self.player_controlled = player_controlled
        self.current_track = None
        self.next_track = None
        self.image = None
        self.rotated_image = None
        self.image_rect = None
        self.angle = 0

    def set_position(self, x, y):
        """Set the train's position"""
        self.x = x
        self.y = y

    def set_current_track(self, track_id):
        """Set the train's current track"""
        self.current_track = track_id
        
    def set_next_track(self, track_id):
        """Set the train's next track"""
        self.next_track = track_id

    def generate_image(self, colour):
        """
        Load the train's image based on its colour
        """
        self.image = pygame.image.load(
            f"assets/images/train_{colour}.png"
        ).convert_alpha()
        return self.image
    
    def draw(self, surface, angle=0):
        """
        Draw the train at its current position and rotation.

        Arguments:
            surface: Pygame surface to draw on
            angle: Angle to rotate the train image
        """
        if self.image is None:
            raise RuntimeError("Train image not loaded. generate_image() need called first.")
        self.rotated_image = pygame.transform.rotate(self.image, angle)
        self.image_rect = self.rotated_image.get_rect(center=(self.x, self.y))
        surface.blit(self.rotated_image, self.image_rect)