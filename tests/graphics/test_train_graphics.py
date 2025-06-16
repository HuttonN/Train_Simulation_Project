import pygame
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from core.trains.train import Train

# Constants
WINDOW_SIZE = (800, 600)
DURATION = 3  # seconds to display each test

def display_text(screen, text):
    font = pygame.font.SysFont(None, 32)
    surface = font.render(text, True, (255, 255, 255))
    screen.blit(surface, (20, 20))

def test_static_train(screen):
    train = Train(400, 300)
    train.generate_image("red")
    screen.fill((30, 30, 30))
    train.draw(screen, angle=0)
    display_text(screen, "Static Train: A red train should appear at the center.")
    pygame.display.flip()

def run_graphics_tests():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Train Graphics Tests")

    # 1. Static
    start = time.time()
    while time.time() - start < DURATION:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        test_static_train(screen)
        pygame.time.wait(10)  # slight delay to allow window events

    # Done
    screen.fill((30, 30, 30))
    display_text(screen, "All graphics tests complete! Close the window.")
    pygame.display.flip()
    # Wait until quit
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
        pygame.time.wait(50)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_graphics_tests()
