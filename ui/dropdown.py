import pygame
from ui.styles import TEXT_COLOUR

class Dropdown:
    def __init__(self, x, y, width, height, options, font, placeholder="Select..."):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_index = None
        self.selected_value = None
        self.expanded = False
        self.font = font
        self.placeholder = placeholder
        
        # Visual styling
        self.bg_color = (60, 60, 60)
        self.border_color = (100, 100, 100)
        self.hover_color = (80, 80, 80)
        self.selected_color = (50, 100, 150)
        
        # Calculate dropdown list height
        self.option_height = height
        self.max_visible = min(5, len(options))  # Show max 5 options at once
        self.dropdown_height = self.max_visible * self.option_height
        
        # Scroll offset for long lists
        self.scroll_offset = 0
        
    def draw(self, surface):
        # Draw main dropdown button
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=4)
        pygame.draw.rect(surface, self.border_color, self.rect, width=2, border_radius=4)
        
        # Draw current selection or placeholder
        display_text = self.placeholder
        if self.selected_value is not None:
            display_text = str(self.selected_value)
            
        text_surface = self.font.render(display_text, True, TEXT_COLOUR)
        text_rect = text_surface.get_rect()
        text_rect.centery = self.rect.centery
        text_rect.left = self.rect.left + 10
        surface.blit(text_surface, text_rect)
        
        # Draw dropdown arrow
        arrow_points = [
            (self.rect.right - 20, self.rect.centery - 5),
            (self.rect.right - 10, self.rect.centery - 5),
            (self.rect.right - 15, self.rect.centery + 5)
        ]
        pygame.draw.polygon(surface, TEXT_COLOUR, arrow_points)
        
        # Draw dropdown list if expanded
        if self.expanded and self.options:
            dropdown_rect = pygame.Rect(
                self.rect.x, 
                self.rect.bottom, 
                self.rect.width, 
                self.dropdown_height
            )
            
            # Background for dropdown list
            pygame.draw.rect(surface, self.bg_color, dropdown_rect, border_radius=4)
            pygame.draw.rect(surface, self.border_color, dropdown_rect, width=2, border_radius=4)
            
            # Draw visible options
            visible_options = self.options[self.scroll_offset:self.scroll_offset + self.max_visible]
            mouse_pos = pygame.mouse.get_pos()
            
            for i, option in enumerate(visible_options):
                option_index = i + self.scroll_offset
                option_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.bottom + i * self.option_height,
                    self.rect.width,
                    self.option_height
                )
                
                # Highlight hovered option
                if option_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(surface, self.hover_color, option_rect)
                
                # Highlight selected option
                if option_index == self.selected_index:
                    pygame.draw.rect(surface, self.selected_color, option_rect)
                
                # Draw option text
                option_text = self.font.render(str(option), True, TEXT_COLOUR)
                option_text_rect = option_text.get_rect()
                option_text_rect.centery = option_rect.centery
                option_text_rect.left = option_rect.left + 10
                surface.blit(option_text, option_text_rect)
                
            # Draw scroll indicators if needed
            if len(self.options) > self.max_visible:
                self._draw_scroll_indicators(surface, dropdown_rect)
    
    def _draw_scroll_indicators(self, surface, dropdown_rect):
        # Up arrow (if can scroll up)
        if self.scroll_offset > 0:
            up_arrow = [
                (dropdown_rect.right - 15, dropdown_rect.top + 10),
                (dropdown_rect.right - 10, dropdown_rect.top + 15),
                (dropdown_rect.right - 20, dropdown_rect.top + 15)
            ]
            pygame.draw.polygon(surface, TEXT_COLOUR, up_arrow)
        
        # Down arrow (if can scroll down)
        if self.scroll_offset + self.max_visible < len(self.options):
            down_arrow = [
                (dropdown_rect.right - 15, dropdown_rect.bottom - 10),
                (dropdown_rect.right - 10, dropdown_rect.bottom - 15),
                (dropdown_rect.right - 20, dropdown_rect.bottom - 15)
            ]
            pygame.draw.polygon(surface, TEXT_COLOUR, down_arrow)
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                
                # Click on main dropdown button
                if self.rect.collidepoint(pos):
                    self.expanded = not self.expanded
                    return {"action": "dropdown_toggled", "expanded": self.expanded}
                
                # Click on dropdown options
                elif self.expanded and self.options:
                    dropdown_rect = pygame.Rect(
                        self.rect.x, self.rect.bottom, 
                        self.rect.width, self.dropdown_height
                    )
                    
                    if dropdown_rect.collidepoint(pos):
                        # Calculate which option was clicked
                        relative_y = pos[1] - self.rect.bottom
                        option_index = relative_y // self.option_height + self.scroll_offset
                        
                        if 0 <= option_index < len(self.options):
                            self.selected_index = option_index
                            self.selected_value = self.options[option_index]
                            self.expanded = False
                            return {
                                "action": "option_selected", 
                                "index": option_index, 
                                "value": self.selected_value
                            }
                    else:
                        # Click outside dropdown - close it
                        self.expanded = False
                        return {"action": "dropdown_closed"}
                        
            elif event.type == pygame.MOUSEWHEEL and self.expanded:
                # Scroll through options
                dropdown_rect = pygame.Rect(
                    self.rect.x, self.rect.bottom, 
                    self.rect.width, self.dropdown_height
                )
                
                if dropdown_rect.collidepoint(pygame.mouse.get_pos()):
                    self.scroll_offset = max(0, min(
                        len(self.options) - self.max_visible,
                        self.scroll_offset - event.y
                    ))
        
        return None
    
    def set_options(self, new_options):
        """Update the dropdown options"""
        self.options = new_options
        self.scroll_offset = 0
        self.selected_index = None
        self.selected_value = None
        self.expanded = False
        
        # Recalculate dropdown height
        self.max_visible = min(5, len(new_options))
        self.dropdown_height = self.max_visible * self.option_height
    
    def get_selected(self):
        """Get the currently selected value"""
        return self.selected_value
    
    def set_selected(self, value):
        """Set the selected value programmatically"""
        try:
            self.selected_index = self.options.index(value)
            self.selected_value = value
        except ValueError:
            self.selected_index = None
            self.selected_value = None