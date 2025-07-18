import pygame

def draw_fade_overlay(surface, rect, alpha = 180, colour = (50, 50, 50)):
    overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    overlay.fill((*colour, alpha))
    surface.blit(overlay, (rect.left, rect.top))