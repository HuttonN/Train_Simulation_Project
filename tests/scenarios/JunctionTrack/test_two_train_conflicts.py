# test_two_train_conflicts.py
import os
import sys
import pygame

# ------------------------------------------------------------
# Project path
# ------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ------------------------------------------------------------
# Engine imports
# ------------------------------------------------------------
from core.grid import Grid
from core.track.junction import JunctionTrack
from core.trains.train import Train
from core.route import Route
from controller.track_loader import load_track_layout
from controller.route_loader import load_route

# ------------------------------------------------------------
# Paths & constants
# ------------------------------------------------------------
# Layouts
LAYOUT_MIN   = "data/Tracks/Test_Layouts/Test_JunctionTrack.JSON"                 # minimal: no onward segment after A
LAYOUT_TAIL  = "data/Tracks/Test_Layouts/Test_JunctionTrack_with_tail.JSON"       # same, but with a short egress after A (optional file)

# Routes
ROUTES = {
    "AS": "data/Routes/Test_Routes/Test_JunctionTrack/A_to_S.JSON",
    "AC": "data/Routes/Test_Routes/Test_JunctionTrack/A_to_C.JSON",
    "SA": "data/Routes/Test_Routes/Test_JunctionTrack/S_to_A.JSON",
    "CA": "data/Routes/Test_Routes/Test_JunctionTrack/C_to_A.JSON",
}

ROUTES_TAIL = {
    "SA": "data/Routes/Test_Routes/Test_JunctionTrack_with_tail/S_to_A_tail.JSON",
    "CA": "data/Routes/Test_Routes/Test_JunctionTrack_with_tail/C_to_A_tail.JSON",
}

# Spawn (row, col) at each approach, matching your layout JSON
SPAWN_AT = {
    "A": (5, 10),   # entry_A.start
    "S": (5, 24),   # entry_S.start
    "C": (12, 18),  # entry_C.start
}

# Where screenshots are saved when you press "S"
SCREENSHOT_DIR = os.path.join(PROJECT_ROOT, "Figures", "Appendicies", "JunctionTrack_Scenarios")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

BG = (30, 30, 30)

# ------------------------------------------------------------
# Utilities
# ------------------------------------------------------------
def make_train(row, col, route_file, grid, track_objects, colour="red"):
    """Create a Train on (row, col) with a Route loaded from route_file."""
    route = Route(load_route(route_file, track_objects))
    train = Train(row=row, col=col, grid=grid, carriages=[], track_objects=track_objects, colour=colour)
    train.set_route(route)
    return train

def create_train_from_move(move_code, grid, track_objects, colour, *, use_tail=False):
    origin = move_code[0]  # 'A' | 'S' | 'C'
    (r, c) = SPAWN_AT[origin]
    route_file = (ROUTES_TAIL.get(move_code) if use_tail else None) or ROUTES[move_code]
    # Optional debug:
    # print(f"[route] {move_code} -> {os.path.basename(route_file)} (tail={use_tail})")
    return make_train(r, c, route_file, grid, track_objects, colour)

def draw_world(screen, grid, track_objects):
    """Draw grid + tracks (JunctionTrack needs track_objects for draw)."""
    grid.draw_grid(screen)
    for piece in track_objects.values():
        if hasattr(piece, "update"):
            piece.update()
        if isinstance(piece, JunctionTrack):
            piece.draw_track(screen, track_objects)
        else:
            piece.draw_track(screen)

def save_screenshot(screen, scenario_code, step_hint=None):
    base = f"{scenario_code}"
    if step_hint:
        base += f"_{step_hint}"
    fname = os.path.join(SCREENSHOT_DIR, f"{base}.png")
    pygame.image.save(screen, fname)
    print(f"[saved] {fname}")

# ------------------------------------------------------------
# Core runner
# ------------------------------------------------------------
def run_pair(first_code, second_code, *, layout_path=LAYOUT_MIN, headstart_ms=0, fps=10, window_caption=None):
    """
    Deterministically run a two-train pairing.
    - first_code, second_code: 'AS'/'AC'/'SA'/'CA'
    - headstart_ms: delay before spawning the second train (0 = simultaneous)
    - layout_path: LAYOUT_MIN (default) or LAYOUT_TAIL to allow clearing A
    - Keys: ESC to quit, S to screenshot
    """
    scenario = f"JT2-{first_code}-{second_code}"

    pygame.init()
    try:
        screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
        caption = window_caption or f"{scenario}  |  layout={os.path.basename(layout_path)}"
        pygame.display.set_caption(caption)

        grid = Grid(50, 50, 40)
        track_objects, _, _ = load_track_layout(layout_path, grid)

        trains = []

        use_tail = os.path.normpath(layout_path) == os.path.normpath(LAYOUT_TAIL)

        # Spawn first train immediately (red), second after headstart (blue)
        train_first = create_train_from_move(first_code, grid, track_objects, colour="red",  use_tail=use_tail)
        trains.append(train_first)

        second_spawned = False
        start_ticks = pygame.time.get_ticks()
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_s:
                        # simple screenshot (no step counter); press whenever you want a frame
                        save_screenshot(screen, scenario)

            # Spawn second after headstart
            if not second_spawned and (pygame.time.get_ticks() - start_ticks) >= headstart_ms:
                train_second = create_train_from_move(second_code, grid, track_objects, colour="blue", use_tail=use_tail)
                trains.append(train_second)
                second_spawned = True

            screen.fill(BG)
            draw_world(screen, grid, track_objects)
            for t in trains:
                t.update(screen)

            pygame.display.flip()
            clock.tick(fps)
    finally:
        pygame.quit()

# ------------------------------------------------------------
# Convenience wrappers: JT2-<first>-<second>
# (Use these names in your matrix/results; each enforces creation order)
# ------------------------------------------------------------
def test_JT2_AS_SA():  # E1 conflict (order-independent)
    """A→S first, then S→A"""
    run_pair("AS", "SA")

def test_JT2_SA_AS():  # E1 conflict (order-independent)
    """S→A first, then A→S"""
    run_pair("SA", "AS")

def test_JT2_AC_CA():  # E1 conflict (order-independent)
    """A→C first, then C→A"""
    run_pair("AC", "CA")

def test_JT2_CA_AC():  # E1 conflict (order-independent) - complement
    """C→A first, then A→C"""
    run_pair("CA", "AC")

def test_JT2_AC_SA():  # E2 interlocking (order-independent)
    """A→C first, then S→A"""
    run_pair("AC", "SA")

def test_JT2_SA_AC():  # E2 interlocking (order-independent) - complement
    """S→A first, then A→C"""
    run_pair("SA", "AC")

def test_JT2_AS_CA():  # E2 interlocking (order-independent)
    """A→S first, then C→A"""
    run_pair("AS", "CA")

def test_JT2_CA_AS():  # E2 interlocking (order-independent) - complement
    """C→A first, then A→S"""
    run_pair("CA", "AS")

def test_JT2_CA_SA():  # E3 merge into A (order-sensitive) — C first
    """
    C→A first, then S→A.
    On the MIN layout, the first train will occupy segment_A (no egress),
    so the second remains held indefinitely — this is expected.
    Use LAYOUT_TAIL to show the second proceeding after C clears A.
    """
    run_pair("CA", "SA", layout_path=LAYOUT_MIN)

def test_JT2_SA_CA():  # E3 merge into A (order-sensitive) — S first
    """S→A first, then C→A. Same layout caveat as above."""
    run_pair("SA", "CA", layout_path=LAYOUT_MIN)

# Optional “tail” proof runs for SA↔CA (if you add the with_tail layout file)
def test_JT2_CA_SA_tail():
    """C→A first, then S→A on tail layout so the first can clear A."""
    run_pair("CA", "SA", layout_path=LAYOUT_TAIL)

def test_JT2_SA_CA_tail():
    """S→A first, then C→A on tail layout so the first can clear A."""
    run_pair("SA", "CA", layout_path=LAYOUT_TAIL)

# test_JT2_AS_SA()
# test_JT2_SA_AS()
# test_JT2_AC_CA()
# test_JT2_CA_AC()
# test_JT2_AC_SA()
# test_JT2_SA_AC()
# test_JT2_AS_CA()
# test_JT2_CA_AS()
# test_JT2_CA_SA()
# test_JT2_SA_CA()
# test_JT2_CA_SA_tail()
test_JT2_SA_CA_tail()