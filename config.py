"""
Configuration constants for the Warehouse Logistics Agent simulation.
Tweak these values to change grid size, colors, animation speed, or the
mission list without touching any simulation logic.
"""

# ---------------------------------------------------------------------------
# Grid dimensions (columns x rows)
# ---------------------------------------------------------------------------
GRID_COLS = 14
GRID_ROWS = 10
CELL_SIZE = 50          # pixels per grid cell

# ---------------------------------------------------------------------------
# Window layout — grid area on the left, a live decision-log panel on the
# right, and an interactive control bar along the bottom, all inside ONE
# application window (no separate terminal needed).
# ---------------------------------------------------------------------------
HUD_HEIGHT = 70                              # top status bar, spans full width
GRID_AREA_WIDTH = GRID_COLS * CELL_SIZE      # 700
GRID_AREA_HEIGHT = GRID_ROWS * CELL_SIZE     # 500
LOG_PANEL_WIDTH = 430
LOG_HEADER_HEIGHT = 28
CONTROL_BAR_HEIGHT = 58

WINDOW_WIDTH = GRID_AREA_WIDTH + LOG_PANEL_WIDTH
WINDOW_HEIGHT = HUD_HEIGHT + GRID_AREA_HEIGHT + CONTROL_BAR_HEIGHT
FPS = 60

# ---------------------------------------------------------------------------
# Animation timing
# ---------------------------------------------------------------------------
# BASE_CELL_MOVE_MS is the glide time per cell at 1.0x speed (slider default).
# Tuned so a full run at 1.0x (all 3 deliveries) takes roughly 50 seconds —
# sized to fill the 45-60s "live demonstration" segment of the required
# 60-90s video in one take. The in-app speed slider scales this live.
BASE_CELL_MOVE_MS = 950
PICKUP_PAUSE_MS = 800
DELIVER_PAUSE_MS = 800
REPLAN_PAUSE_MS = 1100
START_PAUSE_MS = 1500

SPEED_MIN = 0.5
SPEED_MAX = 3.0
SPEED_DEFAULT = 1.0

# ---------------------------------------------------------------------------
# Colors (R, G, B)
# ---------------------------------------------------------------------------
COLOR_BG            = (235, 236, 240)
COLOR_FLOOR         = (250, 250, 252)
COLOR_FLOOR_ALT     = (241, 242, 246)
COLOR_SHELF         = (120, 84, 54)
COLOR_SHELF_EDGE    = (89, 61, 38)
COLOR_GRID_LINE     = (216, 218, 224)
COLOR_HUD_BG        = (30, 33, 41)
COLOR_HUD_TEXT      = (240, 240, 245)
COLOR_HUD_ACCENT    = (255, 176, 59)
COLOR_FORKLIFT      = (255, 176, 32)
COLOR_FORKLIFT_EDGE = (168, 110, 10)
COLOR_PACKAGE       = (176, 122, 68)
COLOR_PACKAGE_EDGE  = (94, 62, 30)
COLOR_BAY           = (77, 175, 124)
COLOR_BAY_EDGE      = (43, 122, 84)
COLOR_PATH          = (117, 178, 255)
COLOR_VISITED       = (206, 222, 245)
COLOR_OBSTACLE_NEW  = (222, 70, 70)
COLOR_TEXT_DARK     = (35, 37, 43)
COLOR_TEXT_LIGHT    = (255, 255, 255)

# Live decision-log panel
COLOR_LOG_BG        = (24, 26, 32)
COLOR_LOG_HEADER_BG = (40, 44, 54)
COLOR_LOG_TEXT      = (210, 213, 220)
COLOR_LOG_DIM        = (120, 124, 135)
COLOR_LOG_SUCCESS    = (108, 209, 150)
COLOR_LOG_WARNING    = (240, 120, 110)
COLOR_LOG_SECTION    = (255, 176, 59)

# Interactive control bar (bottom): restart button + speed slider
COLOR_CONTROL_BG     = (30, 33, 41)
COLOR_BUTTON         = (61, 110, 150)
COLOR_BUTTON_HOVER   = (77, 133, 178)
COLOR_BUTTON_EDGE    = (168, 110, 10)
COLOR_SLIDER_TRACK   = (70, 74, 85)
COLOR_HINT_TEXT      = (150, 154, 165)

# ---------------------------------------------------------------------------
# Mission definition: each package must be picked up, then carried to its
# assigned loading bay. Cells are (col, row), (0,0) = top-left.
# ---------------------------------------------------------------------------
FORKLIFT_START = (0, 0)

MISSIONS = [
    {"package_id": "A", "package_cell": (2, 2),  "bay_id": "1", "bay_cell": (3, 9)},
    {"package_id": "B", "package_cell": (6, 4),  "bay_id": "2", "bay_cell": (7, 9)},
    {"package_id": "C", "package_cell": (10, 6), "bay_id": "3", "bay_cell": (11, 9)},
]

# ---------------------------------------------------------------------------
# Interactive obstacles: the player clicks any open floor cell during the
# run to drop or remove a shelf-like obstacle. If it blocks the path the
# forklift is currently driving, the agent replans live with A* — this
# replaces what used to be a scripted, one-shot obstacle event.
# ---------------------------------------------------------------------------
