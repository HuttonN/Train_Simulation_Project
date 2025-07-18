import pygame
from ui.styles import MENU_COLOUR, TEXT_COLOUR, get_track_button_size, get_button_font
from ui.button import Button
from utils.track_data import get_all_track_infos
from utils.ui import draw_fade_overlay

class TrainSelectionMenu:
    def __init__(self, surface, screen_width, screen_height):
        self.surface = surface
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.train_cards = [
            {
                "colour": None,
                "carriages": 0,
                "carriage_colours": [],
                "route": None,
                "confirmed": False
            }
        ]
        self.available_colours = ["blue", "green", "purple", "yellow"]
        # self.track_infos = get_all_track_infos()
        # self.selected_track = None
        # self.scroll_offset = 0
        # self.max_display = 2

        self.font = get_button_font(screen_width)
        self.option_size = get_track_button_size(screen_width, screen_height)
        self.menu_rect = pygame.Rect(
            screen_width * 0.38, screen_height * 0.02,
            screen_width * 0.24, screen_height * 0.80
        )

        # self.select_button = Button((0, 0), (0, 0), "Select", self.font, (70, 180, 120), TEXT_COLOUR)
        # Load images ONCE
        # self.images = self.load_images()

        # Button objects (for click detection)
        # self.track_buttons = []

        self.appeared = False
        self.active = False
        
    # def load_images(self):
    #     images = {}
    #     thumb_size = (int(self.option_size[0]*0.85), int(self.option_size[1]*0.7))
    #     for info in self.track_infos:
    #         try:
    #             img = pygame.image.load(info["preview_image"]).convert_alpha()
    #             img = pygame.transform.smoothscale(img, thumb_size)
    #         except Exception as e:
    #             print(f"Error loading {info['preview_image']}: {e}")
    #             img = None
    #         images[info["filename"]] = img
    #     return images

    def draw(self):
        if not self.appeared:
            return

        # images = self.images
        pygame.draw.rect(
            self.surface,
            MENU_COLOUR,
            self.menu_rect,
            border_radius=14
        )
        # Title
        title = self.font.render("Train Selection", True, TEXT_COLOUR)
        title_rect = title.get_rect(center=(self.menu_rect.centerx, self.menu_rect.top + 30))
        self.surface.blit(title, title_rect)

        # Draw first train card
        self.draw_train_card(0, title_rect.bottom + 20)
 
        # Add faded overlay if not active
        if not self.active:
            draw_fade_overlay(self.surface, self.menu_rect)

    def draw_train_card(self, card_index, y_start):
        card = self.train_cards[card_index]

        # Card dimensions
        card_width = self.menu_rect.width - 20
        card_height = 200
        card_rect = pygame.Rect(
            self.menu_rect.left + 10,
            y_start,
            card_width,
            card_height
        )

        # Card background
        pygame.draw.rect(self.surface, (60,60,60), card_rect, border_radius=8)
        pygame.draw.rect(self.surface, (100, 100, 100), card_rect, width=2, border_radius=8)

        # Card title
        card_title = self.font.render(f"Train {card_index + 1}", True, TEXT_COLOUR)
        card_title_rect = card_title.get_rect(center=(card_rect.centerx, card_rect.top + 20))
        self.surface.blit(card_title, card_title_rect)     



