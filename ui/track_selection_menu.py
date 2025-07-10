import pygame
from ui.styles import MENU_COLOUR, TEXT_COLOUR, get_track_button_size, get_button_font

def draw_track_selection_menu(surface, screen_width, screen_height, track_infos):
    """
    Draw a skeleton of the track selection menu.
    (Adapted directly from showTrackSelection() in old main.py, see notes inline)
    track_infos: list of dicts, each with keys:
        - display_name (str)
        - preview_image (str, path to image)
        - filename (str, original JSON filename)
    """
    # --- Menu Rectangle (from old main.py: menu background area, e.g. #draw_button(screen, menuColour, ...) )
    menu_x = screen_width * 0.12      # old: xPosition = screenWidth * 0.12
    menu_y = screen_height * 0.02     # old: yPosition = screenHeight * 0.02
    menu_w = screen_width * 0.24      # (was 550px wide for 1920x1080, so ~28% of width)
    menu_h = screen_height * 0.75     # matches how buttons stack vertically in old code

    # Draw menu background
    # Old: #draw_button(screen, menuColour, 130, 115, 550, 480)
    # (We're just using pygame.draw.rect for now.)
    pygame.draw.rect(
        surface,
        MENU_COLOUR,
        pygame.Rect(menu_x, menu_y, menu_w, menu_h)
    )

    # Draw placeholder title
    font = get_button_font(screen_width) # essesntially buttonFont = pygame.font.Font('calibri.ttf', int(screenWidth*0.013)) from old main.py
    title = font.render("Track Selection", True, TEXT_COLOUR) # not in old code but think it would be useful
    title_rect = title.get_rect(center=(menu_x + menu_w // 2, menu_y + 30))
    surface.blit(title, title_rect)
     # [No explicit title in old main.py, but good for context.]

     # --- Dummy Track Buttons (UI-only for now) ---
    option_size = get_track_button_size(screen_width, screen_height)
    runningY = 0
    changeInY = screen_height * 0.09  # from: changeInY = screenHeight * 0.09
    max_display = 7
    
    for i, info in enumerate(track_infos[:max_display]):  # Display 5 dummy tracks for layout (later: use real list)
        option_rect = pygame.Rect(
            menu_x + 10,
            menu_y + 60 + runningY,
            option_size[0],
            option_size[1]
        )
        pygame.draw.rect(surface, (80,80,80), option_rect, border_radius=8)
        
        try:
            img = pygame.image.load(info["preview_image"])
            img = pygame.transform.smoothscale(
                img, 
                (int(option_size[1] * 0.8), int(option_size[1] * 0.8))
            )
            img_rect = img.get_rect(left=option_rect.left + 6, centery=option_rect.centery)
            surface.blit(img, img_rect)
        except Exception:
            # If the image fails to load
            pass

        text = font.render(info["display_name"], True, TEXT_COLOUR)
        text_rect = text.get_rect(
            left=option_rect.left + int(option_size[1] * 0.8) + 14,
            centery=option_rect.centery
        )
        surface.blit(text, text_rect)
        runningY += changeInY
        # Old: see for-loop for f in trackFiles, for-loop for f in range(startScroll, startScroll+7)...
        # Old: trackOptions.append(Button(...)), then trackButton.render(screen)
        # Here, just render dummy rectangles for now.
