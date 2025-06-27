class Route:
    def __init__(self, segments):
        self.segments = segments
        self.current_index = 0

    def get_current_segment(self):
        if self.current_index < len(self.segments):
            return self.segments[self.current_index]
        return None
    
    def advance(self):
        self.current_index += 1

    def is_finished(self):
        return self.current_index >= len(self.segments)