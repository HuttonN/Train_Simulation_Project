import pygame

# https://stackoverflow.com/a/63763175
class Button:
    def __init__(self, position, size, text, font, colour, text_colour=(0,0,0), image=None):
        self.position = position
        self.size = (int(size[0]), int(size[1]))
        self.text = text
        self.font = font
        self.colour = colour
        self.text_colour = text_colour
        self.image = image

        self.button = pygame.Surface((self.size[0], self.size[1])).convert()
        self.button.fill(colour)

    def getPosition(self):
        return self.position

    def getText(self):
        return self.text

    def setText(self, text):
        self.text = text

    def render(self, window):
        window.blit(self.button, (self.position[0], self.position[1]))

        if self.image:
            img_rect = self.image.get_rect()
            img_rect.centerx = self.position[0] + self.size[0] // 2
            img_rect.y = self.position[1] + 8
            window.blit(self.image, img_rect)
            text_y = img_rect.bottom + 8
        else:
            text_y = self.position[1] + self.size[1] // 2
        
        text_surface = self.font.render(f"{self.text}", True, self.text_colour)
        text_rect = text_surface.get_rect(center=(self.position[0] + self.size[0]//2, text_y))
        window.blit(text_surface, text_surface.get_rect(
            center=(self.position[0] + self.size[0] // 2, self.position[1] + self.size[1] // 2)))

    def clicked(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # get the mouse position
                mousePos = event.pos

                if self.button.get_rect(topleft=self.position).collidepoint(mousePos[0], mousePos[1]):
                    return True

        return False

    def hovered(self):
        mousePos = pygame.mouse.get_pos()

        if self.button.get_rect(topleft=self.position).collidepoint(mousePos[0], mousePos[1]):
            return True

        return False