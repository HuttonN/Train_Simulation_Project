class Route:
    def __init__(self, steps):
        self.steps = steps          # List of dicts, one per track piece
        self.current_index = 0

    def get_current_step(self):
        if self.current_index < len(self.steps):
            return self.steps[self.current_index]
        return None
    
    def advance(self):
        self.current_index += 1

    def is_finished(self):
        return self.current_index >= len(self.steps)

    def stops_at_station(self, station_id):
        return any(
            step["track_id"] == station_id and step.get("stop?", False)
            for step in self.steps
        )
    
    def reset(self):
        self.current_index = 0
