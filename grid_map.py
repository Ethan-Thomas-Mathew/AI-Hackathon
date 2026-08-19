"""
Warehouse grid layout and a lightweight Grid helper class.

Legend
------
0 = open floor (forklift may drive here)
1 = static shelf (impassable — the "static shelf obstacles" from the
    problem statement)
"""

from config import GRID_COLS, GRID_ROWS


def _build_static_layout():
    """
    Hand-designed warehouse floor plan: shelf racks sit on rows 1, 3, 5, 7
    in three column blocks, leaving a perimeter aisle plus horizontal
    cross-aisles (rows 0, 2, 4, 6, 8, 9) so every cell stays reachable.
    This guarantees A* always has a valid path between any two open cells.
    """
    layout = [[0] * GRID_COLS for _ in range(GRID_ROWS)]
    shelf_rows = (1, 3, 5, 7)
    shelf_col_blocks = [(1, 3), (5, 7), (9, 11)]  # inclusive column ranges

    for row in shelf_rows:
        for start, end in shelf_col_blocks:
            for col in range(start, end + 1):
                layout[row][col] = 1
    return layout


STATIC_LAYOUT = _build_static_layout()


class Grid:
    """Represents the warehouse floor and exposes A*-friendly helpers."""

    def __init__(self):
        # Deep copy so runtime obstacle changes never mutate the template
        self.cells = [row[:] for row in STATIC_LAYOUT]
        self.cols = GRID_COLS
        self.rows = GRID_ROWS
        self.dynamic_obstacles = set()

    def in_bounds(self, cell):
        x, y = cell
        return 0 <= x < self.cols and 0 <= y < self.rows

    def is_static_wall(self, cell):
        x, y = cell
        return self.in_bounds(cell) and self.cells[y][x] == 1

    def is_walkable(self, cell):
        if not self.in_bounds(cell):
            return False
        if self.is_static_wall(cell):
            return False
        if cell in self.dynamic_obstacles:
            return False
        return True

    def neighbors(self, cell):
        x, y = cell
        candidates = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return [c for c in candidates if self.is_walkable(c)]

    def add_dynamic_obstacle(self, cell):
        self.dynamic_obstacles.add(cell)

    def remove_dynamic_obstacle(self, cell):
        self.dynamic_obstacles.discard(cell)

    def toggle_dynamic_obstacle(self, cell):
        """Adds an obstacle if `cell` is currently clear, or removes it if
        one is already there. Returns True if an obstacle was just added,
        False if one was just removed. Used by the click-to-place UI."""
        if cell in self.dynamic_obstacles:
            self.dynamic_obstacles.discard(cell)
            return False
        self.dynamic_obstacles.add(cell)
        return True
