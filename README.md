# Train Simulation Prototype

A Python/Pygame prototype for experimenting with railway operations on a discrete 2D grid. Track layouts are described in JSON and loaded into an in-memory network of track pieces, routes, stations, junctions, passengers, and trains. The project includes a work-in-progress UI, several scripted simulation scenarios, visual assets, and supporting utilities for geometry, signalling, and routing.

---

## Features

- **Grid-based infrastructure** (`core/grid.py`, `core/track/*`) providing straight track, Bézier curves, stations, single and double junctions.
- **Operational model** (`core/trains/train.py`, `core/segment.py`, `core/passenger.py`) for train motion, carriage following, timed station stops, junction interlocking, and passenger boarding.
- **Scenario runner** (`main.py`) with ready-made demos:
  - `run_with_ui` — sidebar + wizard prototype (minimal drawing).
  - `run_two_trains_demo` — two independent services with passenger loading.
  - `run_single_train_minimal` — smoke test with one train.
  - `run_layout_viewer` — static visualisation of a layout.
  - `run_deadlock_demo` — conflicting routes on a junction-rich layout.
- **JSON-driven content** under `data/Tracks` and `data/Routes`, including functional layouts and focused test cases.
- **Reusable UI widgets** (`ui/*`) for buttons, menus, dropdowns, and styling.
- **Assets** (`assets/`) containing sprites, preview images, and the bundled font.
- **Automatable scenario harness** (`tests/scenarios`) and classic unit tests (`tests/unit`) for selected components.

---

## Project layout

```
Train_Simulation_Project/
├─ assets/                 # Fonts and sprite/preview images
├─ controller/             # Simulation manager + loaders for tracks and routes
├─ core/                   # Grid, segments, passengers, trains, and track pieces
├─ data/                   # JSON definitions for layouts and routes
├─ tests/                  # Unit tests and interactive scenario harnesses
├─ ui/                     # Sidebar, menus, buttons, and shared styles
├─ utils/                  # Geometry, numerics, signalling, and data helpers
└─ main.py                 # Entry point with selectable simulation scenarios
```

---

## Requirements

- Python **3.10+** (Pygame is fully supported from 3.8+, code targets 3.10 syntax).
- `pip` for dependency management.
- SDL libraries (installed automatically with the official `pygame` wheels on Windows/macOS; see Linux notes on the Pygame wiki).

### Python dependencies

| Package  | Purpose                        |
|----------|--------------------------------|
| `pygame` | Rendering, timing, event loop  |

Optional (for tests/tooling):

| Package  | Purpose                                |
|----------|----------------------------------------|
| `pytest` | Running the unit test suite (optional) |

---

## Quick start

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-account>/Train_Simulation_Project.git
   cd Train_Simulation_Project
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install pygame
   # Optional:
   # pip install pytest
   ```

4. **Choose a scenario**

   Open `main.py`, scroll to the bottom, and make sure **exactly one** of the scenario
   functions is uncommented inside the `if __name__ == "__main__":` block.
   The repo ships with `run_two_trains_demo()` enabled by default.

5. **Run the simulation**
   ```bash
   python main.py
   ```
   A Pygame window opens. Close it or press `ESC` (where implemented) to exit.

---

## Scenario reference

| Function                  | Description                                                                              | Notes                                                                                 |
|--------------------------|------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| `run_with_ui()`          | Boots the Sidebar + wizard prototype without drawing tracks (UI-only smoke test).        | Useful for validating `SimulationManager` interactions.                                |
| `run_two_trains_demo()`  | Two trains on independent loops with stations and passengers.                            | Demonstrates boarding/alighting and carriage following.                                |
| `run_single_train_minimal()` | One train, no passengers – fastest way to verify route traversal and rendering.     | Good hardware sanity check.                                                            |
| `run_layout_viewer()`    | Renders the active layout without trains.                                                | Ideal when tuning JSON track geometry.                                                |
| `run_deadlock_demo()`    | Competing routes on a junction-rich layout highlighting interlocking/deadlock behaviour. | Uses `JSON_SEG3_TO_SEG1` / `JSON_SEG1_TO_SEG3` route definitions.                     |

---

## Data files

- **Layouts** (`data/Tracks/*.json`): supply tracks (with geometry, connections, optional segment membership) and metadata (`display_name`, `preview_image`, `complete` flag). Use existing files as templates.
- **Routes** (`data/Routes/**.json`): ordered route steps referencing track IDs plus entry/exit endpoints and optional metadata (e.g. `"stop?": true` to enforce station halts).

The loaders (`controller/track_loader.load_track_layout` and `controller/route_loader.load_route`) raise explicit errors if a referenced track or endpoint is missing.

---

## Running tests

**Standard library unittest**
```bash
python -m unittest tests.unit.test_segment
```

**Pytest (optional)**
```bash
pytest tests/unit
```

> ⚠️ Scenario tests under `tests/scenarios` intentionally open Pygame windows and are best driven manually (they double as reproducible demos).

---

## Troubleshooting

- **Pygame fails to initialise video**  
  On Linux, ensure SDL dependencies (`libsdl2-dev`, `libsdl2-image-dev`, etc.) are installed before `pip install pygame`.

- **Blank window**  
  Verify that **one** scenario is uncommented and the others remain commented; having zero or multiple scenarios active will cause immediate exit or conflicts.

- **Assets missing**  
  Run from the repository root so relative paths to `assets/` and `data/` resolve correctly.

---

## Contributing

1. Fork or branch locally.
2. Follow the virtual environment + dependency instructions above.
3. Add or update tests where possible (unit tests for logic; scenario harnesses for behaviour).
4. Ensure the simulation runs without runtime errors.
5. Open a pull request summarising the change (reference relevant scenarios or tests).

---

## License

Copyright (c) 2025 Neil Hutton. All rights reserved.

Permission is granted to prospective employers, recruiters, and interviewers to
view, clone, and run this code for evaluation purposes only. No permission is
granted to modify, redistribute, sublicense, or use this code in production or
derivative works without prior written consent from the copyright holder.
