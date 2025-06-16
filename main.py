import pygame
import sys

def main():
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("Train Simulation Game")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill screen with background color
        screen.fill((30, 30, 30))  # Dark grey background

        # --- DRAW/UPDATE GOES HERE ---

        pygame.display.flip()
        clock.tick(60)  # Limit to 60 frames per second

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()