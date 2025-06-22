import pygame

class Train(pygame.sprite.Sprite):
    """
    Represents a train in the simulation. Snaps to grid centers,
    and uses track's compass for orientation.
    """

    def __init__(self, row, col, grid, colour="red", player_controlled=False):
        super().__init__()
        self.row = row
        self.col = col
        self.grid = grid
        self.x, self.y = self.grid.grid_to_screen(row, col)
        self.colour = colour
        self.player_controlled = player_controlled
        self.current_track = None
        self.next_track = None
        self.image = None
        self.rotated_image = None
        self.image_rect = None
        self.angle = 0
        self.load_image()
        self.s_on_curve = 0 # Distance along current curve
        self.curve_speed = 3 

    def set_current_track(self, track_piece):
        self.current_track = track_piece
        self.angle = track_piece.get_angle() if track_piece else 0

    def move_towards(self, target_row, target_col, speed=3):
        target_x, target_y = self.grid.grid_to_screen(target_row, target_col)
        dx = target_x - self.x
        dy = target_y - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist > speed:
            self.x += dx / dist * speed
            self.y += dy / dist * speed
        else:
            self.x, self.y = target_x, target_y
            self.row, self.col = target_row, target_col

    def draw(self, surface):
        if self.image is None:
            raise RuntimeError("Train image not loaded.")
        self.rotated_image = pygame.transform.rotate(self.image, -self.angle)
        self.image_rect = self.rotated_image.get_rect(center=(self.x, self.y))
        surface.blit(self.rotated_image, self.image_rect)

    # def print_status(self):
    #     """Print grid coordinates, current track, and angle."""
    #     track_info = (
    #         f"Track[{self.current_track.row},{self.current_track.col},{getattr(self.current_track, 'compass', '?')}]"
    #         if self.current_track else "None"
    #     )
    #     print(f"Train: (row={self.row}, col={self.col}), on {track_info}, angle={self.angle:.1f}")


    def load_image(self):
        self.image = pygame.image.load(
            f"assets/images/train_{self.colour}.png"
        ).convert_alpha()

    def at_cell_center(self):
        expected_x, expected_y = self.grid.grid_to_screen(self.row, self.col)
        return abs(self.x - expected_x) < 1 and abs(self.y - expected_y) < 1
    
    def move_along_curve(self, curved_track):
        self.s_on_curve = min(self.s_on_curve + self.curve_speed, curved_track.curve_length)
        t = curved_track.arc_length_to_t(self.s_on_curve)
        (self.x, self.y), self.angle = curved_track.get_point_and_angle(t)
        if self.s_on_curve >= curved_track.curve_length:
            self.row, self.col = curved_track.end_row, curved_track.end_col
