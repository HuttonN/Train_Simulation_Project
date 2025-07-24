import pygame
import os
from ui.sidebar import Sidebar
from ui.track_selection_menu import TrackSelectionMenu
from ui.train_selection_menu import TrainSelectionMenu
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
        self.train_menu = TrainSelectionMenu(self.screen, self.screen_width, self.screen_height)

        self.trains = []
        self.passengers = []
        self.stations = []

        # Main menu state
        self.menu_state = None
        self.wizard_state = None
        self.wizard_data = {
            "selected_track": None,
            "trains": [],
            "current_train": None
        }

        # Create manual simulation

    def handle_events(self, events):
        clicked = self.sidebar.handle_events(events)
        if clicked == "Create Simulation":
            if self.wizard_state is None:
                self.start_wizard()
            else:
                pass
        if self.wizard_state == "track_selection":
            result = self.track_menu.handle_events(events)
            if result and result["action"] == "confirm_selection":
                self.wizard_data["selected_track"] = result["track"]
                json_path = os.path.join("data/Tracks", self.wizard_data["selected_track"])
                self.track_objects, self.segment_objects, available_routes = load_track_layout(json_path, self.grid)
                self.wizard_data["available_routes"] = available_routes
                self.advance_wizard_to("train_selection")
        elif self.wizard_state == "train_selection":
            result = self.train_menu.handle_events(events)
            if result:
                if result["action"] == "route_selected":
                    route_name = result["route"]
                    route_file_path = self.get_route_file_path(route_name)

                    # Store name and file path in train card data
                    card_index = result["card"]
                    train_card = self.train_menu.train_cards[card_index]
                    train_card["route"] = route_name
                    train_card["route_file_path"] = route_file_path

                    print(f"Route selected: {route_name} -> {route_file_path}")

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

        if self.wizard_state == "track_selection":
            self.track_menu.draw()
        elif self.wizard_state in ["train_selection", "route_selection", "carriage_selection"]:
            self.track_menu.draw()
            self.train_menu.draw()

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
            return
        for piece in self.track_objects.values():
            if isinstance(piece, JunctionTrack) or isinstance(piece, DoubleCurveJunctionTrack):
                piece.draw_track(self.screen, self.track_objects)
            else:
                piece.draw_track(self.screen)

    def start_wizard(self):
        self.wizard_state = "track_selection"
        self.wizard_data = {"selected_track": None, "trains": [], "current_train": None}
        self.track_menu.active = True
        self.track_menu.appeared = True
        self.train_menu.active = False
        self.train_menu.appeared = False

    def advance_wizard_to(self, next_state):
        self.wizard_state = next_state

        if next_state == "train_selection":
            self.track_menu.active = False
            self.train_menu.active = True
            self.train_menu.appeared = True

            available_routes = self.get_available_routes()
            self.train_menu.set_available_routes(available_routes)

    def get_available_routes(self):
        routes = self.wizard_data.get("available_routes", [])
        return [route["name"] for route in routes]
    
    def get_route_file_path(self, route_name):
        routes = self.wizard_data.get("available_routes", [])
        for route in routes:
            if route["name"] == route_name:
                return route["file_path"]
        return None
    
    def get_segment_count(self):
        if not hasattr(self, 'segment_objects'):
            return 0
        return len(self.segment_objects)
    
    def get_max_trains_allowed(self):
        return max(0, self.get_segment_count() - 1)
    
    def get_current_train_count(self):
        return len(self.track_menu.train_cards)