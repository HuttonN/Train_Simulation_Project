import pygame
import sys

from core.grid import Grid
from core.trains.train import Train
from core.track.straight import StraightTrack
from core.track.junction import JunctionTrack

def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 600))
    pygame.display.set_caption("Junction Test")
    clock = pygame.time.Clock()

    # --- GRID SETUP ---
    rows = 15
    cols = 25
    cell_size = 40
    grid = Grid(rows, cols, cell_size=cell_size)

    # --- TRACK SETUP ---
    track_pieces = []

    # 1. Approach: Straight from (5, 5) to (5, 10)
    approach = StraightTrack(grid, 5, 5, 5, 10)
    track_pieces.append(approach)

    # 2. Junction at (5,10)
    junction_piece = JunctionTrack(
        grid,
        start_row=5, start_col=10,            # Junction entrance
        straight_end_row=5, straight_end_col=15,  # Straight exit
        curve_control_row=8, curve_control_col=12,  # Curve control
        curve_end_row=8, curve_end_col=15,        # Curve exit
        track_id="J1",
        branch_activated=False  # Toggle to False to test straight vs curve as active
    )
    track_pieces.append(junction_piece)

    # --- TRAIN SETUP ---
    train = Train(approach.start_row, approach.start_col, grid, colour="red")
    train.set_current_track(approach)
    curr_idx = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Move train ---
        current_track = track_pieces[curr_idx]
        from utils.track_utils import get_segment_length
        segment_length = get_segment_length(current_track)
        train_speed = segment_length / 60  # 1 second per segment

        train.move_along_segment(current_track, train_speed)

        # --- Advance to next piece if arrived ---
        # For demonstration, we only let the train move from the approach to the junction once.
        if (train.at_cell_center() and (train.row, train.col) == (current_track.end_row, current_track.end_col)):
            if curr_idx + 1 < len(track_pieces):
                curr_idx += 1
                next_track = track_pieces[curr_idx]
                train.set_current_track(next_track)
                train.row, train.col = next_track.start_row, next_track.start_col
                train.x, train.y = grid.grid_to_screen(train.row, train.col)
                # If it's a curve or junction, reset curve progress
                if hasattr(next_track, 'is_curve') and next_track.is_curve:
                    train.s_on_curve = 0.0

        # --- Draw everything ---
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
