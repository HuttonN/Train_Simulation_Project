"""
Main launcher with multiple scenarios.

How to use:
- Scroll to the bottom and UNCOMMENT exactly ONE of the `run_*()` calls.
- Leave the others commented.

Scenarios:
  1) run_with_ui() → Loads the partially complete UI (SimulationManager + Sidebar) if available
  2) run_two_trains_demo() → Your current two-loop layout with two trains + passengers (manual drawing path)
  3) run_single_train_minimal() → Minimal smoke test: one train, no passengers
  4) run_layout_viewer() → Draw track + junction animations only, no trains

"""
import os
import sys
import pygame
from typing import Dict, Tuple, List, Any

# --- Core / Model ---
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

# --- Controller ---
from controller.simulation_manager import SimulationManager
from controller.track_loader import load_track_layout
from controller.route_loader import load_route

# --- Utils ---
from utils.track_data import get_all_track_infos

# =========================================================
# Configuration (adjust as needed)
# =========================================================
TITLE = "Train Simulation Prototype"
GRID_ROWS, GRID_COLS, CELL_SIZE = 50, 50, 40
JSON_TRACK = "data/Tracks/Two_Rectangles_with_Two_Junctions_and_Three_Stations.JSON"
JSON_ROUTE_TOP = "data/Routes/Two_Rectangles_with_Two_Junctions_and_Three_Stations/top_loop.JSON"
JSON_ROUTE_BOTTOM = "data/Routes/Two_Rectangles_with_Two_Junctions_and_Three_Stations/bottom_loop.JSON"
JSON_DEADLOCK_TRACK = "data/Tracks/Rectangle_with_Two_Junctions.JSON"
JSON_SEG3_TO_SEG1 = "data/Routes/Rectangle_with_Two_Junctions/seg3_to_seg1_and_back.JSON"
JSON_SEG1_TO_SEG3 = "data/Routes/Rectangle_with_Two_Junctions/seg1_to_seg3_and_back.JSON"
FPS = 10

# =========================================================
# Helpers
# =========================================================

def init_pygame(resizable: bool = True) -> Tuple[pygame.Surface, pygame.time.Clock]:
    pygame.init()
    flags = pygame.RESIZABLE if resizable else 0
    screen = pygame.display.set_mode((0, 0), flags)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    return screen, clock


def build_grid() -> Grid:
    return Grid(GRID_ROWS, GRID_COLS, cell_size=CELL_SIZE)


def load_world(json_track_path: str, grid: Grid):
    """Load tracks + segments + available routes from JSON."""
    track_objects, segment_objects, available_routes = load_track_layout(json_track_path, grid)
    return track_objects, segment_objects, available_routes


def attach_world_to_sim(sim_manager: SimulationManager,
                        grid: Grid,
                        track_objects: Dict[str, Any],
                        segment_objects: Dict[str, Any],
                        available_routes: Dict[str, Any]) -> None:
    if hasattr(sim_manager, "set_world"):
        sim_manager.set_world(grid=grid,
                              track_objects=track_objects,
                              segment_objects=segment_objects,
                              available_routes=available_routes)
    else:
        # Fallback
        sim_manager.grid = grid
        sim_manager.track_objects = track_objects
        sim_manager.segment_objects = segment_objects
        sim_manager.available_routes = available_routes


def draw_all_tracks(screen: pygame.Surface,
                    track_pieces: List[Any],
                    track_objects: Dict[str, Any]) -> None:
    for piece in track_pieces:
        if isinstance(piece, (JunctionTrack, DoubleCurveJunctionTrack)):
            piece.draw_track(screen, track_objects)
        else:
            piece.draw_track(screen)


def update_junction_like_pieces(track_pieces: List[Any]) -> None:
    for piece in track_pieces:
        if hasattr(piece, "update"):
            piece.update()


def start_position_for_route(route: Route) -> Tuple[int, int]:
    first_step = route.get_current_step()
    first_track = first_step["track_obj"]
    entry = first_step["entry"]
    return first_track.get_endpoint_grid(entry)

# =========================================================
# Scenario 1: PARTIAL UI (SimulationManager + Sidebar)
# =========================================================

def run_with_ui() -> None:
    """
    UI-focused scenario: do NOT render the track layout.
    - Uses SimulationManager's own Sidebar and menus.
    - We avoid calling any method that would draw tracks (e.g., sim_manager.draw() / draw_track_layout()).
    - Shows a small HUD note to make it obvious that tracks are intentionally hidden.
    """
    screen, clock = init_pygame(resizable=True)
    grid = build_grid()

    sim_manager = SimulationManager(screen, grid)

    if hasattr(sim_manager, "track_infos"):
        sim_manager.track_infos = get_all_track_infos()

    # Attach world so menus that query tracks/routes can function.
    track_objects, segment_objects, available_routes = load_world(JSON_TRACK, grid)
    attach_world_to_sim(sim_manager, grid, track_objects, segment_objects, available_routes)

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        # Let the SimulationManager process sidebar/menu input
        if hasattr(sim_manager, "handle_events"):
            sim_manager.handle_events(events)
        if hasattr(sim_manager, "update"):
            sim_manager.update()

        # Clear screen + draw grid for context
        screen.fill((30, 30, 30))
        if hasattr(sim_manager, "grid") and hasattr(sim_manager.grid, "draw_grid"):
            sim_manager.grid.draw_grid(screen)

        # --- UI-ONLY DRAWING ---
        # Draw the sidebar owned by the SimulationManager
        if hasattr(sim_manager, "sidebar") and hasattr(sim_manager.sidebar, "draw"):
            try:
                sim_manager.sidebar.draw(screen)
            except Exception:
                pass

        # Draw active wizard/menu panels without drawing the track layout
        # Wizard states
        wiz = getattr(sim_manager, "wizard_state", None)
        if wiz == "track_selection" and hasattr(sim_manager, "track_menu"):
            sim_manager.track_menu.draw()
        elif wiz in ("train_selection", "route_selection", "carriage_selection"):
            if hasattr(sim_manager, "track_menu"):
                sim_manager.track_menu.draw()
            if hasattr(sim_manager, "train_menu"):
                sim_manager.train_menu.draw()

        # Non-wizard menu panels
        menu_state = getattr(sim_manager, "menu_state", None)
        if menu_state == "track" and hasattr(sim_manager, "track_menu"):
            sim_manager.track_menu.draw()
        elif menu_state == "spawn" and hasattr(sim_manager, "draw_spawn_menu"):
            sim_manager.draw_spawn_menu()
        elif menu_state == "status" and hasattr(sim_manager, "draw_status_menu"):
            sim_manager.draw_status_menu()
        elif menu_state == "player" and hasattr(sim_manager, "draw_player_menu"):
            sim_manager.draw_player_menu()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

# =========================================================
# Scenario 2: TWO-TRAINS DEMO (manual draw path)
# =========================================================

def run_two_trains_demo() -> None:
    screen, clock = init_pygame(resizable=True)
    grid = build_grid()

    sim_manager = SimulationManager(screen, grid)
    if hasattr(sim_manager, "track_infos"):
        sim_manager.track_infos = get_all_track_infos()

    # Load tracks and routes
    track_objects, segment_objects, available_routes = load_world(JSON_TRACK, grid)
    track_route_1 = load_route(JSON_ROUTE_TOP, track_objects)
    track_route_2 = load_route(JSON_ROUTE_BOTTOM, track_objects)

    # Stations
    station1 = track_objects["top_station"]
    station2 = track_objects["middle_station"]
    station3 = track_objects["bottom_station"]

    # Seed passengers at station1 destined for station2
    for _ in range(50):
        p = Passenger(origin_station=station1, destination_station=station2)
        station1.waiting_passengers.append(p)

    # Routes (model wrapper)
    route_1 = Route(track_route_1)
    route_2 = Route(track_route_2)

    # Train start grid positions
    start_row_1, start_col_1 = start_position_for_route(route_1)
    start_row_2, start_col_2 = start_position_for_route(route_2)

    # Trains
    red_carriages = [Carriage(grid, passengers=[]) for _ in range(5)]
    train_1 = Train(start_row_1, start_col_1, grid, red_carriages, track_objects, colour="red")
    train_2 = Train(start_row_2, start_col_2, grid, [], track_objects, colour="blue")
    train_1.set_route(route_1)
    train_2.set_route(route_2)
    trains = [train_1, train_2]

    # Track list
    track_pieces = list(track_objects.values())

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        screen.fill((30, 30, 30))

        # Grid
        grid.draw_grid(screen)

        # Update junction-like pieces
        update_junction_like_pieces(track_pieces)

        # Draw all tracks
        draw_all_tracks(screen, track_pieces, track_objects)

        # Update + draw trains
        for train in trains:
            train.update(screen)
        for train in trains:
            train.draw(screen)
        for train in trains:
            if train.stopped or getattr(train, "waiting_for_junction", False):
                for idx, carriage in enumerate(train.carriages):
                    pos = train.get_carriage_position(idx)
                    carriage.position = pos[:2]
                    carriage.angle = pos[2]
                    carriage.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

# =========================================================
# Scenario 3: SINGLE TRAIN MINIMAL (no passengers)
# =========================================================

def run_single_train_minimal() -> None:
    screen, clock = init_pygame(resizable=True)
    grid = build_grid()

    # World + one route
    track_objects, segment_objects, available_routes = load_world(JSON_TRACK, grid)
    track_route = load_route(JSON_ROUTE_TOP, track_objects)
    route = Route(track_route)

    # Single train, no carriages for simplicity
    start_row, start_col = start_position_for_route(route)
    train = Train(start_row, start_col, grid, [], track_objects, colour="red")
    train.set_route(route)

    track_pieces = list(track_objects.values())

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((25, 25, 25))
        grid.draw_grid(screen)

        update_junction_like_pieces(track_pieces)
        draw_all_tracks(screen, track_pieces, track_objects)

        train.update(screen)
        train.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

# =========================================================
# Scenario 4: LAYOUT VIEWER (no trains)
# =========================================================

def run_layout_viewer() -> None:
    screen, clock = init_pygame(resizable=True)
    grid = build_grid()

    track_objects, segment_objects, available_routes = load_world(JSON_TRACK, grid)
    track_pieces = list(track_objects.values())

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((20, 20, 20))
        grid.draw_grid(screen)

        update_junction_like_pieces(track_pieces)
        draw_all_tracks(screen, track_pieces, track_objects)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

# =========================================================
# Scenario 5: DEADLOCK DEMO on Rectangle_with_Two_Junctions
# =========================================================

def run_deadlock_demo() -> None:
    """
    Scenario 5: Two trains contend around the shortcut (segment3) and segment1.
    - Train A: starts on the shortcut (segment3) → segment1 → back to segment3
    - Train B: starts on segment1 → shortcut (segment3) → back to segment3

    Uses the Rectangle_with_Two_Junctions layout and the two route JSONs you created.
    """
    screen, clock = init_pygame(resizable=True)
    grid = build_grid()

    # Load the rectangle layout; fall back to the default layout if missing
    try:
        track_objects, segment_objects, available_routes = load_world(JSON_DEADLOCK_TRACK, grid)
    except Exception:
        track_objects, segment_objects, available_routes = load_world(JSON_TRACK, grid)

    # Load the two routes from JSON
    try:
        track_route_a = load_route(JSON_SEG3_TO_SEG1, track_objects)   # starts on shortcut (segment3)
        track_route_b = load_route(JSON_SEG1_TO_SEG3, track_objects)   # starts on segment1
    except Exception as e:
        # Show a clear on-screen error if the route files are missing/misnamed
        screen.fill((10, 10, 10))
        pygame.font.init()
        font = pygame.font.Font(None, 28)
        msg = font.render(f"Route load error: {e}", True, (230, 80, 80))
        screen.blit(msg, (20, 20))
        sub = font.render("Check JSON_SEG3_TO_SEG1 / JSON_SEG1_TO_SEG3 paths.", True, (200, 200, 200))
        screen.blit(sub, (20, 54))
        pygame.display.flip()
        pygame.time.wait(2500)
        pygame.quit()
        sys.exit(1)

    route_a = Route(track_route_a)
    route_b = Route(track_route_b)

    # Start positions from the first step of each route
    start_row_a, start_col_a = start_position_for_route(route_a)
    start_row_b, start_col_b = start_position_for_route(route_b)

    # Create trains
    train_a = Train(start_row_a, start_col_a, grid, [], track_objects, colour="red")
    train_b = Train(start_row_b, start_col_b, grid, [], track_objects, colour="blue")
    train_a.set_route(route_a)
    train_b.set_route(route_b)
    trains = [train_a, train_b]

    # Track pieces for updates (junctions etc.)
    track_pieces = list(track_objects.values())

    sync_frames = 30  # ~0.5s at 60 fps
    frame = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((18, 18, 18))
        grid.draw_grid(screen)

        update_junction_like_pieces(track_pieces)
        draw_all_tracks(screen, track_pieces, track_objects)

        frame += 1
        if frame > sync_frames:
            for t in trains:
                t.update(screen)
        for t in trains:
            t.draw(screen)

        # HUD
        try:
            pygame.font.init()
            font = pygame.font.Font(None, 24)
            hud1 = font.render("Scenario 5: seg3↔seg1 routes (A starts on shortcut, B on segment1)", True, (230, 230, 230))
            screen.blit(hud1, (12, 12))
        except Exception:
            pass

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

# =========================================================
# Pick ONE scenario by uncommenting below
# =========================================================
if __name__ == "__main__":
    # --- Uncomment exactly ONE of these ---

    # 1) Partially complete UI (SimulationManager + Sidebar)
    # run_with_ui()

    # 2) Your current two-trains demo (manual drawing path)
    run_two_trains_demo()

    # 3) Minimal: single train, no passengers
    # run_single_train_minimal()

    # 4) Layout viewer only (no trains)
    # run_layout_viewer()

    # 5) Deadlock demo on Rectangle_with_Two_Junctions
    # run_deadlock_demo()