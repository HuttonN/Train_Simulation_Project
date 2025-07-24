from ui.button import Button
from ui.styles import get_button_font, get_button_size, get_track_button_size, BUTTON_COLOUR, TEXT_COLOUR

class Sidebar:
    def __init__(self, screen_width, screen_height):

        font = get_button_font(screen_width)
        button_size = get_button_size(screen_width, screen_height)

        self.button_titles = [
            "Create Simulation", "Train Status", "Player Train"
        ]

        self.buttons = []
        for i, title in enumerate(self.button_titles):
            y_pos = screen_height * 0.02 + i * (button_size[1] + screen_height * 0.01)
            button = Button(
                (screen_width * 0.01, y_pos),
                button_size,
                title,
                font,
                BUTTON_COLOUR,
                TEXT_COLOUR
            )
            self.buttons.append(button)

    def draw(self, surface):
        for button in self.buttons:
            button.render(surface)

    def handle_events(self, events):
        """Returns the index or title of the button clicked, or None"""
        for i, button in enumerate(self.buttons):
            if button.clicked(events):
                return self.button_titles[i]
        return None

    