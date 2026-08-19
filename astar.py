"""
A* Search implementation using the Manhattan-distance heuristic:

    h(n) = |x1 - x2| + |y1 - y2|

This module has zero Pygame dependency so it can be unit tested and
reused headlessly (see tests/test_astar.py).
"""

import heapq
import itertools
from dataclasses import dataclass
from typing import Callable, Optional


def manhattan(a, b):
    """Admissible + consistent heuristic for 4-directional unit-cost grids."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


@dataclass
class AStarResult:
    path: list
    cost: int
    nodes_expanded: int
    found: bool


def astar_search(grid, start, goal, on_expand: Optional[Callable] = None) -> AStarResult:
    """
    Runs A* from `start` to `goal` on `grid`.

    Parameters
    ----------
    grid : Grid
        Must provide .neighbors(cell) -> list of walkable neighbor cells.
    start, goal : (int, int)
    on_expand : callable(cell, g, h, f, nodes_expanded_so_far) -> None
        Optional callback fired every time a node is popped off the open
        set and expanded — used to stream live "decision log" lines.

    Returns
    -------
    AStarResult(path, cost, nodes_expanded, found)
    """
    counter = itertools.count()  # heap tie-breaker; avoids comparing tuples with equal f
    open_heap = []
    g_score = {start: 0}
    came_from = {}
    closed = set()

    heapq.heappush(open_heap, (manhattan(start, goal), next(counter), start))
    nodes_expanded = 0

    while open_heap:
        f, _, current = heapq.heappop(open_heap)

        if current in closed:
            continue
        closed.add(current)
        nodes_expanded += 1

        g_current = g_score[current]
        h_current = manhattan(current, goal)
        if on_expand:
            on_expand(current, g_current, h_current, f, nodes_expanded)

        if current == goal:
            return AStarResult(
                path=_reconstruct(came_from, start, goal),
                cost=g_score[goal],
                nodes_expanded=nodes_expanded,
                found=True,
            )

        for neighbor in grid.neighbors(current):
            tentative_g = g_current + 1  # uniform step cost of 1 per move
            if tentative_g < g_score.get(neighbor, float("inf")):
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current
                f_neighbor = tentative_g + manhattan(neighbor, goal)
                heapq.heappush(open_heap, (f_neighbor, next(counter), neighbor))

    return AStarResult(path=[], cost=0, nodes_expanded=nodes_expanded, found=False)


def _reconstruct(came_from, start, goal):
    path = [goal]
    while path[-1] != start:
        path.append(came_from[path[-1]])
    path.reverse()
    return path
