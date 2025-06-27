import pygame

_next_id = 1

class Passenger(pygame.sprite.Sprite):

    def __init__(self, origin_station, destination_station, group_size = 1, colour=None):
        self.id = Passenger._next_id
        _next_id += 1
        

        self.origin_station = origin_station
        self.destination_station = destination_station
        self.group_size = group_size
        self.status = "waiting"
        self.current_location = origin_station
        self.colour = colour or (120, 255, 255)

    def board(self, train, carriage):
        self.status = "onboard"
        self.current_location = (train, carriage)

    def alight(self, station):
        self.status = "waiting"
        self.current_location = station

    def has_arrived(self):
        return self.status == "waiting" and self.current_location == self.destination_station
    
    def draw(self, surface, position):
        pygame.draw.circle(surface, self.colour, position, 3)