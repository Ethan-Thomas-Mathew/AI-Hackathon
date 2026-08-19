"""
Lightweight sanity tests for the A* implementation (no Pygame needed).

Run with:
    python tests/test_astar.py
or, if pytest is installed:
    pytest tests/test_astar.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astar import astar_search, manhattan
from grid_map import Grid


def test_manhattan_heuristic():
    assert manhattan((0, 0), (3, 4)) == 7
    assert manhattan((5, 5), (5, 5)) == 0
    print("test_manhattan_heuristic PASSED")


def test_open_grid_optimality():
    grid = Grid()
    grid.cells = [[0] * grid.cols for _ in range(grid.rows)]  # clear all shelves
    result = astar_search(grid, (0, 0), (5, 4))
    assert result.found
    assert result.cost == manhattan((0, 0), (5, 4)), "A* must find the optimal cost on an open grid"
    assert len(result.path) == result.cost + 1
    print(f"test_open_grid_optimality PASSED (cost={result.cost}, nodes={result.nodes_expanded})")


def test_obstacle_avoidance():
    grid = Grid()  # default warehouse layout with shelves
    result = astar_search(grid, (0, 0), (2, 2))
    assert result.found
    for cell in result.path:
        assert grid.is_walkable(cell), f"Path must never cross a shelf, got {cell}"
    print(f"test_obstacle_avoidance PASSED (cost={result.cost}, nodes={result.nodes_expanded})")


def test_no_path_when_fully_boxed_in():
    grid = Grid()
    grid.cells = [[1] * grid.cols for _ in range(grid.rows)]
    grid.cells[0][0] = 0
    grid.cells[5][5] = 0
    result = astar_search(grid, (0, 0), (5, 5))
    assert not result.found
    print("test_no_path_when_fully_boxed_in PASSED")


def test_all_missions_reachable():
    from config import MISSIONS, FORKLIFT_START
    grid = Grid()
    cursor = FORKLIFT_START
    for mission in MISSIONS:
        r1 = astar_search(grid, cursor, mission["package_cell"])
        assert r1.found, f"Package {mission['package_id']} unreachable from {cursor}"
        r2 = astar_search(grid, mission["package_cell"], mission["bay_cell"])
        assert r2.found, f"Bay {mission['bay_id']} unreachable from package {mission['package_id']}"
        cursor = mission["bay_cell"]
    print("test_all_missions_reachable PASSED")


def test_path_cost_matches_step_count():
    grid = Grid()
    result = astar_search(grid, (0, 0), (11, 9))
    assert result.found
    assert result.cost == len(result.path) - 1, "cost must equal number of moves (unit step cost)"
    print(f"test_path_cost_matches_step_count PASSED (cost={result.cost})")


if __name__ == "__main__":
    test_manhattan_heuristic()
    test_open_grid_optimality()
    test_obstacle_avoidance()
    test_no_path_when_fully_boxed_in()
    test_all_missions_reachable()
    test_path_cost_matches_step_count()
    print("\nAll A* tests passed.")
