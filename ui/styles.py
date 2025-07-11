import pygame
import os

# Colours
TRACK_COLOUR = (169, 169, 169)
BUTTON_COLOUR = (60,60,60)
MENU_COLOUR = (50,50,50,255)
TEXT_COLOUR = (240,240,240)

def get_button_font(screen_width):
    font_path = os.path.join("assets", "calibri.ttf")
    return pygame.font.Font(font_path, int(screen_width * 0.010))

# button sizes
def get_button_size(screen_width, screen_height):
    return (screen_width * 0.08, screen_height * 0.08)

def get_track_button_size(screen_width, screen_height):
    return (screen_width*0.13, screen_height*0.08)