import pygame
import sys

from core.grid import Grid
from core.trains.train import Train
from core.trains.carriage import Carriage
from core.track.straight import StraightTrack
from core.track.curve import CurvedTrack
from core.track.junction import JunctionTrack
from core.track.double_curve_junction import DoubleCurveJunctionTrack
from core.track.station import StationTrack
from core.passenger import Passenger
from core.route import Route

from controller.simulation_manager import SimulationManager
from controller.track_loader import load_track_layout
from controller.route_loader import load_route

from ui.sidebar import Sidebar
from ui.button import Button

from utils.track_data import get_all_track_infos

def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0),pygame.RESIZABLE)
    pygame.display.set_caption("Train Simulation Prototype")
    clock = pygame.time.Clock()

    screen_width, screen_height = screen.get_size()
    rows, cols, cell_size = 50, 50, 40
    grid = Grid(rows, cols, cell_size=cell_size)
    
    sim_manager = SimulationManager(screen, grid)
    sim_manager.track_infos = get_all_track_infos()

    # json_track_path = "data/Tracks/Two_Rectangles_with_Two_Junctions_and_Three_Stations.JSON"
    # json_route_path_1 = "data/Routes/Two_Rectangles_with_Two_Junctions_and_Three_Stations/top_loop.JSON"
    # json_route_path_2 = "data/Routes/Two_Rectangles_with_Two_Junctions_and_Three_Stations/bottom_loop.JSON"

    # Load tracks and routes
    # track_objects, segment_objects = load_track_layout(json_track_path, grid)
    # track_route_1 = load_route(json_route_path_1, track_objects)
    # track_route_2 = load_route(json_route_path_2, track_objects)

    # Load station objects
    # station1 = track_objects["top_station"]
    # station2 = track_objects["middle_station"]
    # station3 = track_objects["bottom_station"]

    # Add 50 passengers at station1, destined for station2
    # for i in range(50):
    #     p = Passenger(origin_station=station1, destination_station=station2)
    #     station1.waiting_passengers.append(p)

    # Setup routes
    # route_1 = Route(track_route_1)
    # route_2 = Route(track_route_2)

    # track_pieces = list(track_objects.values())

    # --- TRAIN SETUP ---
    # first_step_1 = route_1.get_current_step()
    # first_track_1 = first_step_1["track_obj"]
    # first_entry_1 = first_step_1["entry"]
    # start_row_1, start_col_1 = first_track_1.get_endpoint_grid(first_entry_1)
    # first_step_2 = route_2.get_current_step()
    # first_track_2 = first_step_2["track_obj"]
    # first_entry_2 = first_step_2["entry"]
    # start_row_2, start_col_2 = first_track_2.get_endpoint_grid(first_entry_2)

    # train_1 = Train(start_row_1, start_col_1, grid, [], track_objects, colour="red")
    # train_2 = Train(start_row_2, start_col_2, grid, [], track_objects, colour="blue")
    # train_1.set_route(route_1)
    # train_2.set_route(route_2)
    # trains = [train_1, train_2]

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        sim_manager.handle_events(events)
        sim_manager.update()
        sim_manager.draw()

        # --- MAIN UPDATE: Update all active track pieces (junctions) ---
        # for piece in track_pieces:
        #     # Only call update if the piece defines it (junctions, double junctions)
        #     if hasattr(piece, "update"):
        #         piece.update()

        # --- Update all trains ---
        # for train in trains:
        #     train.update(screen)

        # --- Rendering ---
        # draw_track_selection_menu(screen, screen_width, screen_height, track_infos)

        # for piece in track_pieces:
        #     if isinstance(piece, JunctionTrack) or isinstance(piece, DoubleCurveJunctionTrack):
        #         piece.draw_track(screen, track_objects)
        #     else:
        #         piece.draw_track(screen)
        # for train in trains:
        #     train.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
