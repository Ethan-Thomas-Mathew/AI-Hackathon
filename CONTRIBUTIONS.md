# Team Contributions

This maps every file in the repo to the member responsible for it, so the
GitHub commit history clearly shows three separate, meaningful
contributions rather than one person pushing everything.

| Member | Role | Owns (files) | Commit message |
|---|---|---|---|
| **1** | A\* Algorithm | `astar.py`, `grid_map.py`, `config.py` | `Implement A* warehouse pathfinding` |
| **2** | Visualization | `visualizer.py`, `controls.py`, `assets/` | `Add warehouse grid visualization and forklift animation` |
| **3** | Integration & Documentation | `agent.py`, `logger.py`, `main.py`, `tests/`, `README.md`, `SUMMARY.pdf`, `build_summary_pdf.py`, `requirements.txt`, `.gitignore`, `CONTRIBUTIONS.md` | `Add logging, metrics, documentation and final integration` |

## What each member actually built

**Member 1 — A\* Algorithm**
- Grid representation (`grid_map.py`): warehouse layout, walkability
  checks, static shelves, and the click-to-obstacle toggle used by the
  interactive UI.
- A\* implementation (`astar.py`): the search itself, Manhattan heuristic,
  path reconstruction, expanded-node counting, path-cost calculation.
  Zero UI dependency — fully unit-testable on its own.

**Member 2 — Visualization**
- Pygame interface: the warehouse grid, forklift animation, packages,
  loading bays, obstacle rendering, and the live path-preview trail
  (`visualizer.py`).
- Interactive controls: the Restart button and speed Slider widgets, plus
  their hover/drag behavior (`controls.py`).
- The `assets/demo_screenshot.png` used in the README.

**Member 3 — Integration & Documentation**
- Console + in-app logging and performance metrics (`logger.py`): the
  timestamped decision log, the in-memory buffer the log panel reads
  from.
- Package pickup/delivery state machine, live replanning, and the
  BLOCKED-state recovery logic (`agent.py`).
- Wiring it all together — the Pygame event loop, mouse-click routing,
  and the `--test` headless mode (`main.py`).
- All tests (`tests/`), `README.md`, `SUMMARY.pdf` (+ its generator
  script), and this file.

## Suggested git workflow

See `scripts/GIT_WORKFLOW.md` for exact, ready-to-run commands for each
member, in the recommended sequential order (simplest way to avoid merge
conflicts in a 90-minute window).
