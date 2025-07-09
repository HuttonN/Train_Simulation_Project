class SimulationManager:
    """
    Manages simulation state, steps and main components (classes)
    Acts as coordinator between the core logic and the UI
    """

    def __init__(self, screen):
        self.screen = screen

    # Core state
        self.tracks = []
        self.trains = []
        self.passengers = []
        self.stations = []
        self.selected_track = None
        self.simulation_running = False

    def handle_events(self, events):
        # To fill in
        pass

    def update(self):
        # To fill in
        pass

    def draw(self):
        # Just draws blank screen for now
        self.screen.fill((30,30,30))