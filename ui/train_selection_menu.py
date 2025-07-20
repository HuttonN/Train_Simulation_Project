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
        self.available_colours = ["blue", "green", "purple", "red", "yellow"]
        
        # Store color button rectangles for click detection
        self.color_rects = []
        
        self.font = get_button_font(screen_width)
        self.menu_rect = pygame.Rect(
            screen_width * 0.38, screen_height * 0.02,
            screen_width * 0.24, screen_height * 0.80
        )

        self.back_button = Button((0, 0), (0, 0), "Back", self.font, (70, 180, 120), TEXT_COLOUR)
        self.next_button = Button((0, 0), (0, 0), "Next", self.font, (70, 180, 120), TEXT_COLOUR)

        self.appeared = False
        self.active = False
        
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

        # Draw the back button
        back_button_top = self.menu_rect.bottom - 87
        back_button_width = self.menu_rect.width * 0.35
        back_button_rect = pygame.Rect(
            self.menu_rect.left + (self.menu_rect.width //2 - back_button_width) // 2,
            back_button_top,
            back_button_width, 45
        )
        self.back_button = Button(
            (back_button_rect.left, back_button_rect.top),
            (back_button_rect.width, back_button_rect.height),
            "Back", self.font, (70, 180, 120), TEXT_COLOUR
        )
        self.back_button.render(self.surface)


        # Draw the next button
        next_button_top = self.menu_rect.bottom - 87
        next_button_width = self.menu_rect.width * 0.35
        next_button_rect = pygame.Rect(
            self.menu_rect.left + (self.menu_rect.width *(6/4) - next_button_width) // 2,
            next_button_top,
            next_button_width, 45
        )
        self.next_button = Button(
            (next_button_rect.left, next_button_rect.top),
            (next_button_rect.width, next_button_rect.height),
            "Next", self.font, (70, 180, 120), TEXT_COLOUR
        )
        self.next_button.render(self.surface)
 
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

        # Colour selection label
        colour_label = self.font.render("Train Colour:", True, TEXT_COLOUR)
        colour_label_rect = colour_label.get_rect()
        colour_label_rect.topleft = (card_rect.left + 15, card_rect.top + 45)
        self.surface.blit(colour_label, colour_label_rect)

        # Clear color rects for this frame
        self.color_rects.clear()

        # Colour options
        colour_start_x = colour_label_rect.right + 20
        colour_y = colour_label_rect.centery - 15
        for i, colour in enumerate(self.available_colours):
            colour_rect = pygame.Rect(
                colour_start_x + (i*45),
                colour_y,
                30, 30
            )
            
            # Store rect for click detection
            self.color_rects.append((colour_rect, colour, card_index))
            
            colour_map = {
                "blue": (63,72,204),
                "green": (14,209,69),
                "purple": (184,61,186),
                "red": (236,28,36),
                "yellow": (255,202,24)
            }
            pygame.draw.rect(self.surface, colour_map[colour], colour_rect, border_radius=4)

            if card["colour"] == colour:
                pygame.draw.rect(self.surface, (255, 255, 255), colour_rect, width=3, border_radius=4)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                
                # Check color selection clicks
                for rect, colour, card_index in self.color_rects:
                    if rect.collidepoint(pos):
                        self.train_cards[card_index]["colour"] = colour
                        return {"action": "color_selected", "card": card_index, "color": colour}
        
        return None