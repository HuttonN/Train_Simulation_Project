import pygame
from ui.styles import MENU_COLOUR, TEXT_COLOUR, get_track_button_size, get_button_font
from ui.button import Button
from utils.track_data import get_all_track_infos
from utils.ui import draw_fade_overlay
from ui.dropdown import Dropdown

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
        # Store the carriage number rectangles for click detection
        self.carriage_rects = []
        
        self.font = get_button_font(screen_width)
        self.menu_rect = pygame.Rect(
            screen_width * 0.38, screen_height * 0.02,
            screen_width * 0.24, screen_height * 0.80
        )

        self.route_dropdowns = []

        self.back_button = Button((0, 0), (0, 0), "Back", self.font, (70, 180, 120), TEXT_COLOUR)
        self.next_button = Button((0, 0), (0, 0), "Next", self.font, (70, 180, 120), TEXT_COLOUR)

        self.appeared = False
        self.active = False

        self.max_trains_allowed = 0
        self.add_train_button = None
        self.add_train_rects = []
        
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
        pygame.draw.rect(self.surface, (60, 60, 60), card_rect, border_radius=8)
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

        # Clear colour rects for this frame
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

        # Carriage selection label
        carriage_label = self.font.render("Carriages:", True, TEXT_COLOUR)
        carriage_label_rect = carriage_label.get_rect()
        carriage_label_rect.topleft = (card_rect.left + 15, colour_label_rect.bottom + 30)
        self.surface.blit(carriage_label, carriage_label_rect)

        # Clear carriage rects for this frame
        self.carriage_rects.clear()

        # Carriage controls [-] [number] [+]
        controls_start_x = carriage_label_rect.right + 20
        controls_y = carriage_label_rect.centery -15

        # Minus button
        minus_rect = pygame.Rect(controls_start_x, controls_y, 30, 30)
        minus_colour = (80, 80, 80)
        pygame.draw.rect(self.surface, minus_colour, minus_rect, border_radius= 4)
        minus_text = self.font.render("-", True, TEXT_COLOUR)
        minus_text_rect = minus_text.get_rect(center = minus_rect.center)
        self.surface.blit(minus_text, minus_text_rect)

        # Number display
        number_rect = pygame.Rect(controls_start_x+30, controls_y, 30, 30)
        pygame.draw.rect(self.surface, (40, 40, 40), number_rect, border_radius=4)
        number_text = self.font.render(str(card["carriages"]), True, TEXT_COLOUR)
        number_text_rect = number_text.get_rect(center=number_rect.center)
        self.surface.blit(number_text, number_text_rect)
                
        # Plus button
        plus_rect = pygame.Rect(controls_start_x + 60, controls_y, 30, 30)
        plus_colour = (80, 80, 80)
        pygame.draw.rect(self.surface, plus_colour, plus_rect, border_radius= 4)
        plus_text = self.font.render("+", True, TEXT_COLOUR)
        plus_text_rect = plus_text.get_rect(center = plus_rect.center)
        self.surface.blit(plus_text, plus_text_rect)

        # Store button rects for click detection
        self.carriage_rects.append(("minus", minus_rect, card_index))
        self.carriage_rects.append(("plus", plus_rect, card_index))

        # Route selection
        route_label = self.font.render("Route:", True, TEXT_COLOUR)
        route_label_rect = route_label.get_rect()
        route_label_rect.topleft = (card_rect.left + 15, carriage_label_rect.bottom + 25)
        self.surface.blit(route_label, route_label_rect)

        while len(self.route_dropdowns) <= card_index:
            self.route_dropdowns.append(None)

        if not self.route_dropdowns[card_index]:
            routes = getattr(self, "available_routes", ["No routes available"])
            self.route_dropdowns[card_index] = Dropdown(
                route_label_rect.right + 20,
                route_label_rect.y - 5,
                250, 30,
                routes,
                self.font,
                "Select Route"
            )
        
        self.route_dropdowns[card_index].draw(self.surface)

    def is_back_button_clicked(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                if self.back_button.button.get_rect(topleft=self.back_button.position).collidepoint(pos):
                    return True
        return False

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                
                # Check color selection clicks
                for rect, colour, card_index in self.color_rects:
                    if rect.collidepoint(pos):
                        self.train_cards[card_index]["colour"] = colour
                        return {"action": "color_selected", "card": card_index, "color": colour}
                    
                # Check carriage [-][+] clicks
                for button_type, rect, card_index in self.carriage_rects:
                    if rect.collidepoint(pos):
                        card = self.train_cards[card_index]
                        if button_type == "minus" and card["carriages"] > 0:
                            card["carriages"] -= 1
                            return {"action": "carriage_changed", "card": card_index, "carriages": card["carriages"]}
                        elif button_type == "plus" and card["carriages"] < 5:
                            card["carriages"] += 1
                            return {"action": "carriage_changed", "card": card_index, "carriages": card["carriages"]}
                        
        for card_index, dropdown in enumerate(self.route_dropdowns):
            if dropdown:
                dropdown_result = dropdown.handle_events(events)
                if dropdown_result and dropdown_result["action"] == "option_selected":
                    card = self.train_cards[card_index]
                    card["route"] = dropdown_result["value"]
                    return {"action": "route_selected", "card": card_index, "route": dropdown_result["value"]}
        return None
    
    def get_available_routes(self):
        if not self.wizard_data["selected_track"]:
            return []
        
    def set_available_routes(self, routes):
        self.available_routes = routes
        for dropdown in self.route_dropdowns:
            if dropdown:
                dropdown.set_options(routes)

    def set_train_limits(self, max_trains):
        self.max_trains_allowed = max_trains

    def is_train_card_complete(self, card_index):
        if card_index >= len(self.train_cards):
            return False
        card = self.train_cards[card_index]
        return (card["colour"] is not None and 
                card["route"] is not None and
                card["carriages"] >= 0)
    
    def can_add_more_trains(self):
        return (len(self.train_cards) < self.max_trains_allowed and
                all(self.is_train_card_complete(i) for i in range(len(self.train_cards))))