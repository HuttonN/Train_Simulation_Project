import pygame
import sys
import os

# Go up three levels from tests/scenarios/JunctionTrack to project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.grid import Grid
from core.track.junction import JunctionTrack
from core.trains.train import Train
from core.route import Route
from controller.track_loader import load_track_layout
from controller.route_loader import load_route

def test_show_junction_track_layout():
    pygame.init()
    screen = pygame.display.set_mode((0, 0),pygame.RESIZABLE)
    grid = Grid(50,50,40)

    # Load layout
    json_path = "data/Tracks/Test_Layouts/Test_JunctionTrack.JSON"
    print("File exists:", os.path.exists(json_path))
    track_objects, _, _ = load_track_layout(json_path, grid)

    # Preview loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((30, 30, 30))
        grid.draw_grid(screen)
        for piece in track_objects.values():
            if isinstance(piece, JunctionTrack):
                piece.draw_track(screen, track_objects)
            else:
                piece.draw_track(screen)
        pygame.display.flip()
        pygame.time.delay(100)

    pygame.quit()

def make_train(start_row, start_col, route_file, grid, track_objects, colour="red"):
    route = Route(load_route(route_file, track_objects))
    train = Train(row=start_row, col=start_col, grid=grid, carriages=[], track_objects=track_objects, colour=colour)
    train.set_route(route)
    return train

def test_junction_conflict_A_vs_C_vs_S():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
    grid = Grid(50, 50, 40)
    json_path = "data/Tracks/Test_Layouts/Test_JunctionTrack.JSON"
    track_objects, _, _ = load_track_layout(json_path, grid)

    # Trains from A, C and S, both aiming to traverse the junction
    train_A = make_train(5, 10, "data/Routes/Test_Routes/Test_JunctionTrack/A_to_S.JSON", grid, track_objects, "red")
    train_S = make_train(5, 24, "data/Routes/Test_Routes/Test_JunctionTrack/S_to_A.JSON", grid, track_objects, "blue")
    train_C = make_train(10, 24, "data/Routes/Test_Routes/Test_JunctionTrack/C_to_A.JSON", grid, track_objects, "green")
    trains = [train_A, train_S, train_C]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((30, 30, 30))
        grid.draw_grid(screen)
        for piece in track_objects.values():
            if isinstance(piece, JunctionTrack):
                piece.draw_track(screen, track_objects)
            else:
                piece.draw_track(screen)

        for train in trains:
            train.update(screen)

        pygame.display.flip()
        pygame.time.delay(60)
    pygame.quit()

test_junction_conflict_A_vs_C_vs_S()