import pygame
import math

class Junction(pygame.sprite.Sprite):
    """
    Represents a simple junction with a main (straight) branch and a diverging (left or right) branch.
    """

    def __init__(self, track_id, prev_id, next_id, diverge_id, branch, junction_type="right", curve_radius = 75, angle=90):
        """
        Arguments:
            track_id: Unique identifier for this junction.
            prev_id: ID of the previous track piece.
            next_id: ID for the main/straight branch.
            diverge_id: ID for the diverging branch.
            branch: Branch/group information.
            junction_type: 'right' or 'left' (determines diverging direction).
            curve_radius: Radius for diverging curve (pixels).
            angle: Sweep angle of diverging branch (degrees).
        """
        super().__init__()
        self.track_id = track_id
        self.prev_id = prev_id
        self.next_id = next_id
        self.branch = branch
        self.junction_type = junction_type
        self.curve_radius = curve_radius
        self.angle = angle
        self.x = None
        self.y = None
        self.occupied = False

    def set_occupied(self, occupied = True):
        self.occupied = occupied

    def is_occupied(self):
        return self.occupied
    
    def get_id(self):
        return self.track_id

    def get_prev_id(self):
        return self.prev_id

    def get_next_id(self):
        return self.next_id

    def get_diverge_id(self):
        return self.diverge_id

    def get_coordinates(self):
        return self.x, self.y
    
    def set_coordinates(self, x, y):
        self.x = x
        self.y = y

    def get_branch(self):
        return self.branch
    
    def adjust_compass(self, compass, branch = 0):
        """
        Adjust compass after passing through junction.
        branch: 0 for main/street, 1 for diverge
        Currently accomodates 45 or 90 degreess
        """
    
        compass_order_cw = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        idx = compass_order_cw.index(compass)
        if branch == 0: # stay on main straight (no change)
            return compass
        if self.junction_type == 'right':
            return compass_order_cw[(idx + 2) % 8] if self.angle == 90 else compass_order_cw[(idx + 1) % 8]
        elif self.junction_type == 'left':
            return compass_order_cw[(idx - 2) % 8] if self.angle == 90 else compass_order_cw[(idx - 1) % 8]
        else:
            return compass # More options to implement here?



