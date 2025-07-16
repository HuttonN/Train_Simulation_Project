import pygame
import os
from ui.sidebar import Sidebar
from ui.track_selection_menu import TrackSelectionMenu
from ui.button import Button
from controller.track_loader import load_track_layout
from core.track.double_curve_junction import DoubleCurveJunctionTrack
from core.track.junction import JunctionTrack

class SimulationManager:
    """
    Manages simulation state, steps and main components (classes)
    Acts as coordinator between the core logic and the UI
    """

    def __init__(self, screen, grid):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.grid = grid
        self.sidebar = Sidebar(self.screen_width, self.screen_height)

        # Core state
        self.selected_track = None
        self.track_buttons = []
        self.track_selection_button = []
        self.simulation_running = False
        self.track_menu = TrackSelectionMenu(self.screen, self.screen_width, self.screen_height)
        self.track_menu_active = False

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
        if self.menu_state == "track":
            result = self.track_menu.handle_events(events)
            if result:
                if result["action"] == "select_track":
                    pass
                elif result["action"] == "confirm_selection":
                    # Load the selected track, close menu, etc.
                    selected_filename = result["track"]
                    print(f"Loading track: {selected_filename}")
                    json_path = os.path.join("data/Tracks", selected_filename)
                    self.track_objects, self.segment_objects = load_track_layout(json_path, self.grid)

    def update(self):
        # To fill in
        pass

    def draw(self):
        """
        Draws the main screen, sidebar, and the currently active menu/panel.
        """
        self.screen.fill((30,30,30))
        self.grid.draw_grid(self.screen)
        self.sidebar.draw(self.screen)
        self.draw_track_layout()

        # Draw the active menu/panel, if any
        if self.menu_state == "track":
            self.track_menu.draw()
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
        pass

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

    def draw_track_layout(self):
        if not hasattr(self, 'track_objects'):
            print("no objects")
            return
        for piece in self.track_objects.values():
            print(piece)
            if isinstance(piece, JunctionTrack) or isinstance(piece, DoubleCurveJunctionTrack):
                piece.draw_track(self.screen, self.track_objects)
            else:
                piece.draw_track(self.screen)