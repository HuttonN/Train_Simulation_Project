import pygame
from ui.styles import MENU_COLOUR, TEXT_COLOUR, get_track_button_size, get_button_font
from ui.button import Button
from utils.track_data import get_all_track_infos


class TrackSelectionMenu:
    def __init__(self, surface, screen_width, screen_height):
        self.surface = surface
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.track_infos = get_all_track_infos()
        self.selected_track = None
        self.scroll_offset = 0
        self.max_display = 2

        self.font = get_button_font(screen_width)
        self.option_size = get_track_button_size(screen_width, screen_height)
        self.menu_rect = pygame.Rect(
            screen_width * 0.12, screen_height * 0.02,
            screen_width * 0.24, screen_height * 0.80
        )

        self.select_button = Button((0, 0), (0, 0), "Select", self.font, (70, 180, 120), TEXT_COLOUR)
        # Load images ONCE
        self.images = self.load_images()

        # Button objects (for click detection)
        self.track_buttons = []
        
    def load_images(self):
        images = {}
        thumb_size = (int(self.option_size[0]*0.85), int(self.option_size[1]*0.7))
        for info in self.track_infos:
            try:
                img = pygame.image.load(info["preview_image"]).convert_alpha()
                img = pygame.transform.smoothscale(img, thumb_size)
            except Exception as e:
                print(f"Error loading {info['preview_image']}: {e}")
                img = None
            images[info["filename"]] = img
        return images

    def draw(self):
        images = self.images
        pygame.draw.rect(
            self.surface,
            MENU_COLOUR,
            self.menu_rect,
            border_radius=14
        )
        # Title
        title = self.font.render("Track Selection", True, TEXT_COLOUR)
        title_rect = title.get_rect(center=(self.menu_rect.centerx, self.menu_rect.top + 30))
        self.surface.blit(title, title_rect)

        self.track_buttons.clear()
        button_gap = 20
        visible_tracks = self.track_infos[self.scroll_offset:self.scroll_offset+self.max_display]

        # y-coordinate for the first button, set with reference to bottom of title rectangle
        y = title_rect.bottom + 30
        last_option_rect = None

        for idx, info in enumerate(visible_tracks):
            option_rect = pygame.Rect(
                self.menu_rect.left + 10,
                y,
                self.option_size[0],
                self.option_size[1]
            )
            is_selected = (self.selected_track == info["filename"])
            button_colour = (80, 120, 200) if is_selected else (80, 80, 80)
            btn = Button(
                (option_rect.left, option_rect.top),
                (option_rect.width, option_rect.height),
                "",  # No text in base button, we'll render below image
                self.font,
                button_colour,
                TEXT_COLOUR
            )
            btn.render(self.surface)
            # Draw the image
            img = images[info["filename"]]
            if img:
                img_rect = img.get_rect(center=(option_rect.centerx, option_rect.top + img.get_height()//2 + 30))
                self.surface.blit(img, img_rect)
            # Draw the text below image
            text_surface = self.font.render(info["display_name"], True, TEXT_COLOUR)
            text_rect = text_surface.get_rect(center=(option_rect.centerx, img_rect.bottom + 30))
            self.surface.blit(text_surface, text_rect)
            # Highlight if selected
            if is_selected:
                pygame.draw.rect(self.surface, (0,200,255), option_rect, width=4)
            self.track_buttons.append((btn, info))
            y = option_rect.bottom + button_gap
            last_option_rect = option_rect

            if last_option_rect is not None:
                select_button_top = last_option_rect.bottom + 30
            else: 
                select_button_top = title_rect.bottom + 120

        # Draw the select button
        select_button_width = self.menu_rect.width * 0.7
        select_button_rect = pygame.Rect(
            self.menu_rect.left + (self.menu_rect.width - select_button_width) // 2,
            select_button_top,
            select_button_width, 45
        )
        self.select_button = Button(
            (select_button_rect.left, select_button_rect.top),
            (select_button_rect.width, select_button_rect.height),
            "Select", self.font, (70, 180, 120), TEXT_COLOUR
        )
        self.select_button.render(self.surface)

    def get_selected(self):
        return self.selected_track

    def is_select_button_clicked(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                if self.select_button.button.get_rect(topleft=self.select_button.position).collidepoint(pos):
                    return True
        return False
    
    def handle_events(self, events):
        for btn, info in self.track_buttons:
            if btn.clicked(events):
                self.selected_track = info["filename"]
                return {"action": "select_track", "track": info["filename"]}
        # Check select button
        if self.select_button.clicked(events):
            if self.selected_track:
                return {"action": "confirm_selection", "track": self.selected_track}
        return None
