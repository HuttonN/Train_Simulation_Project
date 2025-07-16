import pygame

def draw_signal_indicator(surface, center, state_dictionary):
    """
    Draws a visual signal indicator (circle with an arrow) at the given position.

    Arguments:
        surface: Pygame surface to draw on.
        center (tuple): (x, y) center position for the signal.
        angle (float): Arrow direction in radians.
        is_allowed (bool): True if the signal should show "proceed" (green), else "stop" (red).
        is_active (bool): True if this is the currently active branch (can affect visual).
        in_progress (bool): True if switch is in progress (optional, can show yellow).

    Returns:
        None
    """
    if state_dictionary["allowed"]:
        circle_fill = (40, 220, 40) # green
    elif state_dictionary["in_progress"]:
        circle_fill = (255, 200, 40) # amber
    else:
        circle_fill = (230, 30, 30) # red
    pygame.draw.circle(surface, circle_fill, center, radius=12, width=0)
    
