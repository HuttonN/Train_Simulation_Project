import pygame
import sys

from core.grid import Grid
from core.trains.train import Train
from core.track.straight import StraightTrack
from core.track.curve import CurvedTrack
from core.track.junction import JunctionTrack

def main():
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Rectangle with Two Junctions and a Shortcut")
    clock = pygame.time.Clock()

    rows = 20
    cols = 30
    cell_size = 40
    grid = Grid(rows, cols, cell_size=cell_size)

    # --- Corner and key points ---
    TL = (5, 5)
    TR = (5, 25)
    BR = (15, 25)
    BL = (15, 5)

    # Junctions placed near top/bottom center
    TOP_J = (5, 15)
    BOT_J = (15, 15)
    # Top junction exits
    TOP_J_S = (5, 19)     # straight exit
    TOP_J_C = (7, 18)     # branch exit (down)
    TOP_J_CTRL = (5, 18)  # control for curve (gentle downward arc)

    # Bottom junction exits
    BOT_J_S = (15, 15)    # straight exit
    BOT_J_C = (13, 18)    # branch exit (up)
    BOT_J_CTRL = (15, 18) # control for curve (gentle upward arc)

    # --- TRACK SETUP ---
    top_straight1  = StraightTrack(grid, TL[0], TL[1], TOP_J[0], TOP_J[1])
    top_junction   = JunctionTrack(
        grid,
        TOP_J[0], TOP_J[1],      # center (A)
        TOP_J_S[0], TOP_J_S[1],  # straight exit (S)
        TOP_J_CTRL[0], TOP_J_CTRL[1],  # control
        TOP_J_C[0], TOP_J_C[1],  # branch exit (C)
        track_id="J_TOP"
    )
    top_straight2  = StraightTrack(grid, TOP_J_S[0], TOP_J_S[1], TR[0], TR[1])
    tr_curve       = CurvedTrack(grid, TR[0], TR[1], TR[0]+5, TR[1], BR[0], BR[1])  # right-down corner

    right_straight = StraightTrack(grid, BR[0], BR[1], BOT_J_S[0], BOT_J_S[1])
    bottom_junction = JunctionTrack(
        grid,
        BOT_J[0], BOT_J[1],     # center (A)
        BOT_J_S[0], BOT_J_S[1], # straight exit (S)
        BOT_J_CTRL[0], BOT_J_CTRL[1], # control
        BOT_J_C[0], BOT_J_C[1], # branch exit (C)
        track_id="J_BOT"
    )
    bottom_straight2 = StraightTrack(grid, BOT_J_S[0], BOT_J_S[1], BL[0], BL[1])
    bl_curve = CurvedTrack(grid, BL[0], BL[1], BL[0]-5, BL[1], TL[0], TL[1])  # left-up corner

    # The shortcut straight between branches
    shortcut = StraightTrack(grid, TOP_J_C[0], TOP_J_C[1], BOT_J_C[0], BOT_J_C[1])

    track_pieces = [
        top_straight1, top_junction, top_straight2, tr_curve,
        right_straight, bottom_junction, bottom_straight2, bl_curve,
        shortcut
    ]

    # --- ROUTE: Outer loop, then inside shortcut ---
    track_route = [
        # Outer rectangle (clockwise)
        (top_straight1, "A", "B"),
        (top_junction,  "A", "S"),
        (top_straight2, "A", "B"),
        (tr_curve,      "A", "B"),
        (right_straight,"A", "B"),
        (bottom_junction,"A", "S"),
        (bottom_straight2, "A", "B"),
        (bl_curve,      "A", "B"),

        # Shortcut: through both junction branches and the inside vertical
        (top_straight1, "A", "B"),
        (top_junction,  "A", "C"),        # take branch down
        (shortcut,      "A", "B"),        # descend shortcut
        (bottom_junction,"C", "A"),       # up from branch to center
        (bottom_straight2, "A", "B"),
        (bl_curve,      "A", "B"),
    ]

    # --- TRAIN SETUP ---
    first_track, first_entry, first_exit = track_route[0]
    train = Train(*first_track.get_endpoint_grid(first_entry), grid, colour="red")
    train.enter_segment(first_track, first_entry, first_exit)

    curr_idx = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_track, entry_ep, exit_ep = track_route[curr_idx]
        from utils.track_utils import get_segment_length
        if isinstance(current_track, JunctionTrack):
            segment_length = get_segment_length(current_track, entry_ep, exit_ep)
        else:
            segment_length = get_segment_length(current_track)

        train.move_along_segment()

        target_row, target_col = current_track.get_endpoint_grid(exit_ep)
        if train.at_cell_center() and (train.row, train.col) == (target_row, target_col):
            curr_idx = (curr_idx + 1) % len(track_route)
            next_track, next_entry, next_exit = track_route[curr_idx]
            if next_track is top_junction:
                # About to traverse top junction
                if next_entry == "A" and next_exit == "C":
                    top_junction.branch_activated = True
                else:
                    top_junction.branch_activated = False
            if next_track is bottom_junction:
                if next_entry == "C" and next_exit == "A":
                    bottom_junction.branch_activated = True
                else:
                    bottom_junction.branch_activated = False
            train.enter_segment(next_track, next_entry, next_exit)

        screen.fill((30, 30, 30))
        grid.draw_grid(screen, color=(80, 80, 80))
        for piece in track_pieces:
            piece.draw_track(screen)
        train.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
