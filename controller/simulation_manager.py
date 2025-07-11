import pygame
from ui.sidebar import Sidebar
from ui.track_selection_menu import draw_track_selection_menu

class SimulationManager:
    """
    Manages simulation state, steps and main components (classes)
    Acts as coordinator between the core logic and the UI
    """

    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.sidebar = Sidebar(self.screen_width, self.screen_height)

        # Core state
        self.track_infos = []
        self.selected_track = None
        self.track_buttons = []
        self.track_selection_button = []
        self.simulation_running = False

        self.trains = []
        self.passengers = []
        self.stations = []

        # Main menu state
        self.menu_state = None

    def handle_events(self, events):
        clicked = self.sidebar.handle_events(events)
        if clicked == "Spawn Train":
            self.menu_state = "spawn"
        elif clicked == "Track":
            self.menu_state = "track"
        elif clicked == "Train Status":
            self.menu_state = "status"
        elif clicked == "Player Train":
            self.menu_state = "player"
        elif clicked == "Start Sim":
            self.simulation_running = not self.simulation_running

        # Close menus when ESC key pressed
        for event in events: 
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.menu_state = None

         # --- NEW: Handle clicks on track menu buttons ---
        if self.menu_state == "track" and hasattr(self, "track_buttons") and self.track_buttons:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    # Track option buttons
                    for btn, info in self.track_buttons:
                        if btn.rect.collidepoint(mouse_pos):
                            self.selected_track = info["filename"]
                            # Optionally, update visuals or print feedback
                            print(f"Selected track: {info['display_name']}")
                            break
                    # Select button
                    if self.track_selection_button and self.track_selection_button.rect.collidepoint(mouse_pos):
                        if self.selected_track:
                            # Here you trigger your track loading logic!
                            print(f"Confirmed selection: {self.selected_track}")
                            # You might want to close the menu after this:
                            self.menu_state = None
                            # You would call your track loading logic here!

    def update(self):
        # To fill in
        pass

    def draw(self):
        """
        Draws the main screen, sidebar, and the currently active menu/panel.
        """
        self.sidebar.draw(self.screen)

        # Draw the active menu/panel, if any
        if self.menu_state == "track":
            self.draw_track_menu()
        elif self.menu_state == "spawn":
            self.draw_spawn_menu()
        elif self.menu_state == "status":
            self.draw_status_menu()
        elif self.menu_state == "player":
            self.draw_player_menu()
        # elif self.menu_state == "controls":
        #     self.draw_controls_menu()

    # --- MENU DRAWING METHODS ---
    def draw_track_menu(self):
        self.track_buttons, self.track_selection_button = draw_track_selection_menu(
        self.screen,
        self.screen_width,
        self.screen_height,
        self.track_infos,
        self.selected_track
        )

    def draw_spawn_menu(self):
        # TODO: Implement spawn train/station selection menu here
        pass

    def draw_status_menu(self):
        # TODO: Implement train status/monitoring panel here
        pass

    def draw_player_menu(self):
        # TODO: Implement player train options here
        pass

    def draw_controls_menu(self):
        # TODO: Implement controls/help overlay here
        pass