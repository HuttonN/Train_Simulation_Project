from ui.button import Button
from ui.styles import get_button_font, get_button_size, get_track_button_size, BUTTON_COLOUR, TEXT_COLOUR

class Sidebar:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        font = get_button_font(screen_width)
        button_size = get_button_size(screen_width, screen_height)

        y_positions = [
            0.02, # Spawn Train
            0.11, # Start Sim
            0.20, # Track
            0.29, # Train Status
            0.38, # Player Train
        ]
        labels = [
            "Spawn Train", "Start Sim", "Track", "Train Status", "Player Train"
        ]

        self.buttons = []
        for i, label in enumerate(labels):
            btn = Button(
                (screen_width * 0.01, screen_height * y_positions[i]),
                button_size,
                label,
                font,
                BUTTON_COLOUR,
                TEXT_COLOUR
            )
            self.buttons.append(btn)

    def draw(self, surface):
        for button in self.buttons:
            button.render(surface)

    