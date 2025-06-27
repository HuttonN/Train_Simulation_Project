import pygame

class Carriage(pygame.sprite.Sprite):

    def __init__(self, max_capacity=10):
        self.passengers = []
        self.train = None
        self.index_in_train = None
        self.position = (0,0)
        self.angle = 0

    def couple(self, train, index=None):
        self.train = train
        self.index_in_train = index

    def uncouple(self):
        self.train = None
        self.index_in_train = None

    def load(self, passenger_list):
        available = self.max_capacity - len(self.passengers)
        to_board = passenger_list[:available]
        self.passengers.extend(to_board)
        return passenger_list[available:]

    def empty(self):
        self.passengers = []