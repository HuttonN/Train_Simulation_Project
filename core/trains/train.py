import pygame

class Train(pygame.sprite.Sprite):
    """
    Represents a train in the simulation. Supports smooth animation,
    keeps track of grid position and current track piece, and draws itself
    at the center of its current cell.
    """

    def __init__(self, row, col, grid, colour="red", player_controlled=False):
        """
        Initialise the train at a grid position, snapped to the cell center.

        Arguments:
            row, col: Initial grid position.
            grid: Reference to the grid object (for coordinate conversion).
            colour: Train color (for image loading).
            player_controlled (bool): Whether train is controlled by player.
        """
        super().__init__()
        self.row = row
        self.col = col
        self.grid = grid
        self.x, self.y = self.grid_cell_center(row, col)
        self.colour = colour
        self.player_controlled = player_controlled
        self.current_track = None
        self.next_track = None
        self.image = None
        self.rotated_image = None
        self.image_rect = None
        self.angle = 0
        self.load_image()

    def grid_cell_center(self, row, col):
        """Get pixel coords for center of cell (row, col)."""
        x, y = self.grid.grid_to_screen(row, col)
        x += self.grid.cell_size // 2
        y += self.grid.cell_size // 2
        return float(x), float(y)

    def set_position(self, x, y):
        """Set pixel position (floats for smooth animation)."""
        self.x = float(x)
        self.y = float(y)

    def set_grid_position(self, row, col, snap_to_center=True):
        """
        Update logical grid position, and optionally snap to pixel center.
        """
        self.row = row
        self.col = col
        if snap_to_center:
            self.x, self.y = self.grid_cell_center(row, col)

    def set_current_track(self, track_piece):
        """Set the train's current track piece (object reference)."""
        self.current_track = track_piece

    def set_next_track(self, track_piece):
        """Set the train's next track piece (object reference)."""
        self.next_track = track_piece

    def load_image(self):
        """Load train sprite image based on color."""
        self.image = pygame.image.load(
            f"assets/images/train_{self.colour}.png"
        ).convert_alpha()

    def draw(self, surface, angle=None):
        """
        Draw the train at its pixel position (centered in cell by default).
        Args:
            surface: Pygame surface to draw on.
            angle: Rotation angle in degrees (None uses self.angle).
        """
        if self.image is None:
            raise RuntimeError("Train image not loaded.")
        use_angle = self.angle if angle is None else angle
        self.rotated_image = pygame.transform.rotate(self.image, use_angle)
        self.image_rect = self.rotated_image.get_rect(center=(self.x, self.y))
        surface.blit(self.rotated_image, self.image_rect)

    def move_towards(self, target_row, target_col, speed=2):
        """
        Move smoothly toward the center of the given grid cell.
        """
        target_x, target_y = self.grid_cell_center(target_row, target_col)
        dx = target_x - self.x
        dy = target_y - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist > speed:
            self.x += dx / dist * speed
            self.y += dy / dist * speed
        else:
            self.x, self.y = target_x, target_y
            self.row, self.col = target_row, target_col

    def get_grid_position(self):
        """Return (row, col)."""
        return self.row, self.col

    def at_cell_center(self):
        """Return True if train is exactly centered in its current cell."""
        expected_x, expected_y = self.grid_cell_center(self.row, self.col)
        return abs(self.x - expected_x) < 1 and abs(self.y - expected_y) < 1
