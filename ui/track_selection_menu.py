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
        images = self.load_images()
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
                pygame.draw.rect(self.surface, (0,200,255), option_rect, width=4, border_radius=8)
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


# def load_track_images

# def draw_track_selection_menu(surface, screen_width, screen_height, track_infos, selected_track=None):
#     """
#     Draw a skeleton of the track selection menu.
#     (Adapted directly from showTrackSelection() in old main.py, see notes inline)
#     track_infos: list of dicts, each with keys:
#         - display_name (str)
#         - preview_image (str, path to image)
#         - filename (str, original JSON filename)
#     """
#     # --- Menu Rectangle (from old main.py: menu background area, e.g. #draw_button(screen, menuColour, ...) )
#     menu_x = screen_width * 0.12      # old: xPosition = screenWidth * 0.12
#     menu_y = screen_height * 0.02     # old: yPosition = screenHeight * 0.02
#     menu_w = screen_width * 0.24      # (was 550px wide for 1920x1080, so ~28% of width)
#     menu_h = screen_height * 0.75     # matches how buttons stack vertically in old code

#     # Draw menu background
#     # Old: #draw_button(screen, menuColour, 130, 115, 550, 480)
#     # (We're just using pygame.draw.rect for now.)
#     pygame.draw.rect(
#         surface,
#         MENU_COLOUR,
#         pygame.Rect(menu_x, menu_y, menu_w, menu_h),
#         border_radius = 14
#     )

#     # Draw placeholder title
#     font = get_button_font(screen_width) # essesntially buttonFont = pygame.font.Font('calibri.ttf', int(screenWidth*0.013)) from old main.py
#     title = font.render("Track Selection", True, TEXT_COLOUR) # not in old code but think it would be useful
#     title_rect = title.get_rect(center=(menu_x + menu_w // 2, menu_y + 30))
#     surface.blit(title, title_rect)
#      # [No explicit title in old main.py, but good for context.]

#      # --- Dummy Track Buttons (UI-only for now) ---
#     option_size = get_track_button_size(screen_width, screen_height)
#     runningY = 0
#     changeInY = screen_height * 0.11  # from: changeInY = screenHeight * 0.09
#     max_display = 7
    
#     track_buttons = []
#     for i, info in enumerate(track_infos[:max_display]):  # Display 5 dummy tracks for layout (later: use real list)
#         option_rect = pygame.Rect(
#             menu_x + 10,
#             menu_y + 60 + runningY,
#             option_size[0],
#             option_size[1]
#         )

#         is_selected = (selected_track == info["filename"])
#         button_colour = (80, 120, 200) if is_selected else (80, 80, 80)
#         track_button = Button(
#             (option_rect.left, option_rect.top),
#             (option_rect.width, option_rect.height),
#             info["display_name"],
#             font,
#             button_colour,
#             TEXT_COLOUR
#         )
#         track_button.render(surface)
#         # Optional: highlight if selected
#         if is_selected:
#             pygame.draw.rect(surface, (0,200,255), option_rect, width=4, border_radius=8)
#         track_buttons.append((track_button, info))
#         runningY += changeInY
#         # try:
#         #     img = pygame.image.load(info["preview_image"])
#         #     img = pygame.transform.smoothscale(
#         #         img, 
#         #         (int(option_size[1] * 0.8), int(option_size[1] * 0.8))
#         #     )
#         #     img_rect = img.get_rect(left=option_rect.left + 6, centery=option_rect.centery)
#         #     surface.blit(img, img_rect)
#         # except Exception:
#         #     # If the image fails to load
#         #     pass

#         # text = font.render(info["display_name"], True, TEXT_COLOUR)
#         # text_rect = text.get_rect(
#         #     left=option_rect.left + int(option_size[1] * 0.8) + 14,
#         #     centery=option_rect.centery
#         # )
#         # surface.blit(text, text_rect)
        
#     # --- "Select" Button ---
#     select_button_width = menu_w * 0.7
#     select_button_rect = pygame.Rect(
#         menu_x + (menu_w - select_button_width) // 2,
#         menu_y + menu_h - 60,
#         select_button_width,
#         45
#     )
#     select_button = Button(
#         (select_button_rect.left, select_button_rect.top),
#         (select_button_rect.width, select_button_rect.height),
#         "Select",
#         font,
#         (70, 180, 120),
#         TEXT_COLOUR
#     )
#     select_button.render(surface)

#     # --- Return buttons for event handling ---
#     return track_buttons, select_button

#         # button.render(surface)
#         # track_buttons.append((button, info))
#         # runningY += changeInY
#         # Old: see for-loop for f in trackFiles, for-loop for f in range(startScroll, startScroll+7)...
#         # Old: trackOptions.append(Button(...)), then trackButton.render(screen)
#         # Here, just render dummy rectangles for now.
