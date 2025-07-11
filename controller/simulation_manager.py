import pygame
from ui.sidebar import Sidebar

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
        self.tracks = []
        self.trains = []
        self.passengers = []
        self.stations = []

        self.selected_track = None
        self.simulation_running = False

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
            # Optionally close menus when simulation starts/stops
        #     self.menu_state = None
        # elif clicked == "Controls":
        #     # You can toggle controls or make it modal
        #     if self.menu_state == "controls":
        #         self.menu_state = None
        #     else:
        #         self.menu_state = "controls"

        # Close menus when ESC key pressed
        for event in events: 
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.menu_state = None

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
        # TODO: Import and call your track_selection_menu logic here
        # For now, just render a stub panel
        import pygame
        pygame.draw.rect(self.screen, (50,50,50), (self.screen_width * 0.12, self.screen_height * 0.02, self.screen_width * 0.15, self.screen_height * 0.9))
        # You could also call: self.track_selection_menu.draw(self.screen) if you have a class/component

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