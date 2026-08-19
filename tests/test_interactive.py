"""
Tests for the interactive features: click-to-obstacle, live replanning,
protected cells, and BLOCKED-state recovery. None of this touches Pygame
or a display — main.py only imports pygame inside run(), so these pure
helper functions (and the Agent/Grid classes they call) are safe to test
directly.

Run with:
    python tests/test_interactive.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grid_map import Grid
from agent import Agent
from main import try_toggle_obstacle, pixel_to_cell
import config


def _advance_to_move(agent, max_steps=10000):
    """Fast-forwards the agent's state machine (using large dt) until it
    is actively MOVE-ing along a path, or gives up after max_steps."""
    for _ in range(max_steps):
        agent.update(0.05)
        if agent.state == Agent.STATE_MOVE and agent.current_path:
            return
    raise AssertionError("Agent never reached STATE_MOVE")


def test_pixel_to_cell_bounds():
    assert pixel_to_cell((10, config.HUD_HEIGHT + 10)) == (0, 0)
    assert pixel_to_cell((-5, 100)) is None                      # left of grid
    assert pixel_to_cell((5, 5)) is None                          # inside HUD, above grid
    assert pixel_to_cell((config.GRID_AREA_WIDTH + 5, 100)) is None  # right of grid (log panel)
    print("test_pixel_to_cell_bounds PASSED")


def test_click_toggles_obstacle_on_open_floor():
    grid = Grid()
    agent = Agent(grid)
    cell = (5, 0)  # open floor, far from forklift and all missions
    assert grid.is_walkable(cell)

    ok, _ = try_toggle_obstacle(grid, agent, cell)
    assert ok and cell in grid.dynamic_obstacles

    ok, _ = try_toggle_obstacle(grid, agent, cell)  # click again -> removes it
    assert ok and cell not in grid.dynamic_obstacles
    print("test_click_toggles_obstacle_on_open_floor PASSED")


def test_cannot_block_shelf_or_protected_cells():
    grid = Grid()
    agent = Agent(grid)

    shelf_cell = (1, 1)
    assert grid.is_static_wall(shelf_cell)
    ok, _ = try_toggle_obstacle(grid, agent, shelf_cell)
    assert not ok and shelf_cell not in grid.dynamic_obstacles

    ok, _ = try_toggle_obstacle(grid, agent, agent.position)  # forklift's own cell
    assert not ok

    pkg_cell = config.MISSIONS[0]["package_cell"]
    ok, _ = try_toggle_obstacle(grid, agent, pkg_cell)
    assert not ok and pkg_cell not in grid.dynamic_obstacles
    print("test_cannot_block_shelf_or_protected_cells PASSED")


def test_obstacle_on_active_path_triggers_live_replan():
    grid = Grid()
    agent = Agent(grid)
    _advance_to_move(agent)

    assert agent.leg_index == 0  # dock -> Package A
    original_path = list(agent.current_path)
    remaining = original_path[agent.path_step + 1:]
    assert len(remaining) >= 2, "leg 1's path is too short for this test"

    block_cell = remaining[len(remaining) // 2]
    ok, _ = try_toggle_obstacle(grid, agent, block_cell)
    assert ok
    assert agent.state == Agent.STATE_REPLAN_PAUSE, "agent should replan immediately"
    assert block_cell not in agent.current_path, "new path must avoid the new obstacle"

    for cell in agent.current_path:
        assert grid.is_walkable(cell)
    print("test_obstacle_on_active_path_triggers_live_replan PASSED "
          f"(old path len={len(original_path)}, new path len={len(agent.current_path)})")


def test_obstacle_off_path_does_not_trigger_replan():
    grid = Grid()
    agent = Agent(grid)
    _advance_to_move(agent)

    far_cell = (13, 9)  # nowhere near leg 1's path (dock -> package A, top-left area)
    if far_cell in agent.current_path:
        far_cell = (13, 0)
    path_before = list(agent.current_path)

    ok, _ = try_toggle_obstacle(grid, agent, far_cell)
    assert ok
    assert agent.state == Agent.STATE_MOVE, "should keep driving, no replan needed"
    assert agent.current_path == path_before
    print("test_obstacle_off_path_does_not_trigger_replan PASSED")


def test_blocked_state_recovers_when_obstacle_removed():
    grid = Grid()
    agent = Agent(grid)
    _advance_to_move(agent)

    # Seal the forklift in completely on its current leg by blocking every
    # neighboring open cell it hasn't already passed through.
    fx, fy = agent.position
    ring = [(fx + 1, fy), (fx - 1, fy), (fx, fy + 1), (fx, fy - 1)]
    placed = []
    for cell in ring:
        if grid.is_walkable(cell) and cell not in agent.protected_cells():
            ok, _ = try_toggle_obstacle(grid, agent, cell)
            if ok:
                placed.append(cell)

    assert agent.state in (Agent.STATE_BLOCKED, Agent.STATE_REPLAN_PAUSE, Agent.STATE_MOVE)

    # Drain any pending replan pause so we land on the real outcome.
    for _ in range(200):
        if agent.state != Agent.STATE_REPLAN_PAUSE:
            break
        agent.update(0.05)

    if agent.state == Agent.STATE_BLOCKED:
        # Free one of the cells we placed and confirm recovery.
        assert placed, "expected at least one obstacle to have been placed"
        ok, _ = try_toggle_obstacle(grid, agent, placed[0])
        assert ok
        assert agent.state in (Agent.STATE_MOVE, Agent.STATE_REPLAN_PAUSE, Agent.STATE_PLAN)
        print("test_blocked_state_recovers_when_obstacle_removed PASSED (recovered from BLOCKED)")
    else:
        # The layout had another route around the ring — also a valid,
        # correct outcome (A* found an alternate path).
        print("test_blocked_state_recovers_when_obstacle_removed PASSED "
              "(alternate route existed, agent was never blocked)")


if __name__ == "__main__":
    test_pixel_to_cell_bounds()
    test_click_toggles_obstacle_on_open_floor()
    test_cannot_block_shelf_or_protected_cells()
    test_obstacle_on_active_path_triggers_live_replan()
    test_obstacle_off_path_does_not_trigger_replan()
    test_blocked_state_recovers_when_obstacle_removed()
    print("\nAll interactive-feature tests passed.")
