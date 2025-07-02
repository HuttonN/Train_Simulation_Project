import pygame
import math
from core.track.straight import StraightTrack

class StationTrack(StraightTrack):
    """
    Represents a straight track section with an associated station platform.

    Extends StraightTrack to add rendering of station platforms and display
    of passenger count, and stores station-specific attributes such as name 
    and passenger count.

    Designed for use only on straight track sections.
    """
    STATION_COLOUR = (220, 170, 50)
    TEXT_COLOUR = (30, 30, 30)
    STATION_WIDTH = 44
    STATION_LENGTH = 100
    PLATFORM_WIDTH = 20
    PLATFORM_COLOUR = (220, 100, 5) 

    GAP_SIZE = 8
    MIN_PLATFORM_LENGTH = 190  # pixels. Ensures that maximum number of passengers that can board a train (max 5 carriages and 30 per carriage) can fit on platform.

    #region --- Constructor ---------------------------------------------------------

    def __init__(self, grid, start_row, start_col, end_row, end_col, name, passenger_count=0, track_id=None, position=True):
        """
        Initialises a StationTrack object representing a station platform on a straight track.

        Arguments:
            grid: The grid object for coordinate conversion.
            start_row, start_col: Grid coordinates of one endpoint.
            end_row, end_col: Grid coordinates of the other endpoint.
            name (str): Station name.
            passenger_count (int): Number of passengers currently waiting at the station.
            track_id (str, optional): Identifier for the station track.
            position (bool, optional): Platform side; True = one side, False = the other.
        """
        super().__init__(grid, start_row, start_col, end_row, end_col, track_id=track_id or f"STN:{name}")
        self.name = name
        self.passenger_count = passenger_count
        self.position = bool(position)  # True=one side, False=other

        segment_length = math.hypot(self.xB - self.xA)
        if segment_length < self.MIN_PLATFORM_LENGTH:
            raise ValueError(
                f"StationTrack '{self.name}' is too short: {segment_length:.1f}px (minimum {self.MIN_PLATFORM_LENGTH}px needed)."
            )
        self.PLATFORM_LENGTH = segment_length # ensures it matches the length of the track piece
    #endregion

    #region --- Methods -------------------------------------------------------------

    def draw_track(self, surface):
        """
        Draws the straight track and overlays the station platform and name label.

        Arguments:
            surface: Pygame surface to render onto.
        """
        super().draw_track(surface)

        # Direction vectors
        dx = self.xB - self.xA
        dy = self.yB - self.yA
        length = math.hypot(dx, dy)
        if length == 0:
            return

        # Unit vectors
        ux, uy = dx / length, dy / length
        side = 1 if self.position else -1
        perp_x, perp_y = -uy * side, ux * side

        # Track midpoint
        mx, my = (self.xA + self.xB) / 2, (self.yA + self.yB) / 2

        # Move perpendicularly from midpoint by GAP_SIZE + half platform width (to ensure GAP is from track to edge)
        station_offset = self.GAP_SIZE + self.STATION_WIDTH / 2 + self.PLATFORM_WIDTH
        station_px = mx + perp_x * station_offset
        station_py = my + perp_y * station_offset
        platform_offset = self.GAP_SIZE + self.PLATFORM_WIDTH / 2
        platform_px = mx + perp_x * platform_offset
        platform_py = my + perp_y * platform_offset

        # 4. Create the platform surface (unrotated)
        station_surface = pygame.Surface((self.STATION_LENGTH, self.STATION_WIDTH), pygame.SRCALPHA)
        pygame.draw.rect(station_surface, self.STATION_COLOUR, (0, 0, self.STATION_LENGTH, self.STATION_WIDTH))
        platform_surface = pygame.Surface((self.PLATFORM_LENGTH, self.PLATFORM_WIDTH), pygame.SRCALPHA)
        pygame.draw.rect(platform_surface, self.PLATFORM_COLOUR, (0, 0, self.PLATFORM_LENGTH, self.PLATFORM_WIDTH))

        # 5. Draw label in center
        label = f"{self.name} ({self.passenger_count})"
        font = pygame.font.SysFont(None, 16)
        text = font.render(label, True, self.TEXT_COLOUR)
        text_rect = text.get_rect(center=(self.STATION_LENGTH / 2, self.STATION_WIDTH / 2))
        station_surface.blit(text, text_rect)

        # 6. Rotate platform surface to match track angle (note: negative for pygame)
        angle = math.degrees(math.atan2(dy, dx))
        rotated_surface = pygame.transform.rotate(station_surface, -angle)
        rotated_platform = pygame.transform.rotate(platform_surface, -angle)

        # 7. Place rotated surface centered at (px, py)
        rotated_station_rect = rotated_surface.get_rect(center=(station_px, station_py))
        rotated_platform_rect = rotated_platform.get_rect(center=(platform_px, platform_py))
        surface.blit(rotated_surface, rotated_station_rect.topleft)
        surface.blit(rotated_platform, rotated_platform_rect.topleft)

        #endregion