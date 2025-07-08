class Segment:
    def __init__(self, name):
        self.name = name
        self.occupied_by = None

    def request_entry(self, train):
        if self.occupied_by is None or self.occupied_by == train:
            self.occupied_by = train
            return True
        return False
    
    def leave(self, train):
        if self.occupied_by == train:
            self.occupied_by = None