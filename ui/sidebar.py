from ui.button import Button
from ui.styles import get_button_font, get_button_size, get_track_button_size, BUTTON_COLOUR, TEXT_COLOUR

class Sidebar:
    def __init__(self, screen_width, screen_height):

        font = get_button_font(screen_width)
        button_size = get_button_size(screen_width, screen_height)

        self.buttons = [
            Button(
                (screen_width * 0.01, screen_height * 0.02),
                button_size,
                "Create Simulation",
                font,
                BUTTON_COLOUR,
                TEXT_COLOUR
            )
        ]

    def draw(self, surface):
        for button in self.buttons:
            button.render(surface)

    