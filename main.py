"""
Warehouse Logistics Agent — entry point.

Run normally to open the live, interactive Pygame app:
    python main.py

Run a fast headless correctness check (no window, exits automatically —
useful for verifying the install or for CI):
    python main.py --test

Interactivity
-------------
- Click any open grid cell to drop or remove an obstacle. If it blocks the
  path the forklift is currently driving, A* replans live.
- Restart button: resets the whole simulation.
- Speed slider: scales movement/pause speed live, from 0.5x to 3x.
"""

import argparse
import os
import sys

import config
from logger import get_logger, get_log_buffer, clear_log_buffer

log = get_logger()


# ---------------------------------------------------------------------------
# Pure click-to-obstacle logic — deliberately free of any Pygame/display
# dependency so it can be unit tested directly (see tests/test_interactive.py).
# ---------------------------------------------------------------------------
def pixel_to_cell(pos):
    """Converts a mouse (x, y) pixel position to a grid (col, row), or
    None if the click landed outside the grid area (e.g. on the log panel
    or the control bar)."""
    x, y = pos
    if x < 0 or x >= config.GRID_AREA_WIDTH:
        return None
    if y < config.HUD_HEIGHT or y >= config.HUD_HEIGHT + config.GRID_AREA_HEIGHT:
        return None
    return (x // config.CELL_SIZE, (y - config.HUD_HEIGHT) // config.CELL_SIZE)


def try_toggle_obstacle(grid, agent, cell):
    """Validates and applies a click-to-obstacle request. Refuses to block
    shelf cells or any cell the agent still needs (its own position, or an
    unfinished pickup/bay). Returns (success: bool, message: str)."""
    if cell is None or not grid.in_bounds(cell):
        return False, "Click was outside the grid."
    if grid.is_static_wall(cell):
        msg = f"Cannot place an obstacle on the shelf at {cell}."
        log.info(msg)
        return False, msg
    if cell in agent.protected_cells():
        msg = (f"Cannot block {cell} — it's the forklift's current cell or "
               f"still needed for an active pickup/bay.")
        log.info(msg)
        return False, msg

    added = grid.toggle_dynamic_obstacle(cell)
    if added:
        log.info(f"User placed an obstacle at {cell}.")
        agent.notify_obstacle_added(cell)
        return True, f"Obstacle added at {cell}."
    else:
        log.info(f"User removed the obstacle at {cell}.")
        agent.notify_obstacle_removed(cell)
        return True, f"Obstacle removed at {cell}."


def run(headless=False):
    if headless:
        # Dummy video/audio drivers let Pygame run with no real display,
        # e.g. inside SSH sessions, CI, or this project's sandbox.
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

    import pygame  # imported after driver env vars are set

    # Only initialize the display + font subsystems (not audio) — this
    # avoids the common "ALSA / no audio device" error some Linux/WSL
    # setups hit on a full pygame.init().
    pygame.display.init()
    pygame.font.init()

    from grid_map import Grid
    from agent import Agent
    from visualizer import Renderer
    from controls import Button, Slider

    log_buffer = get_log_buffer()

    try:
        screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    except pygame.error as e:
        print(f"\nCould not open a display window ({e}).")
        print("If you're on WSL2, enable WSLg (Windows 11) or run an X server,")
        print("or run 'python main.py --test' for a headless correctness check.")
        sys.exit(1)

    pygame.display.set_caption("Warehouse Logistics Agent — A* (Manhattan Heuristic)")
    clock = pygame.time.Clock()

    grid = Grid()
    agent = Agent(grid)
    renderer = Renderer(screen, grid)

    control_font = pygame.font.SysFont("consolas,menlo,monospace", 14, bold=True)
    bar_top = config.HUD_HEIGHT + config.GRID_AREA_HEIGHT
    restart_button = Button((14, bar_top + 14, 110, 30), "Restart", control_font)
    speed_slider = Slider((150, bar_top + 28, 230, 8),
                           config.SPEED_MIN, config.SPEED_MAX, config.SPEED_DEFAULT,
                           "Speed", control_font)
    hint_pos = (410, bar_top + 20)
    hint_text = "Click any open cell to add/remove an obstacle — the agent replans live."

    running = True
    frame_count = 0
    frame_cap = config.FPS * 60 * 3  # 3 min safety cap so --test can't hang forever

    while running:
        dt = clock.tick(config.FPS) / 1000.0
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                restart_button.handle_mousemove(event.pos)
                speed_slider.handle_event(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.is_clicked(event.pos):
                    grid = Grid()
                    agent = Agent(grid)
                    renderer.grid = grid
                    clear_log_buffer()
                else:
                    speed_slider.handle_event(event)
                    if not speed_slider.dragging:
                        cell = pixel_to_cell(event.pos)
                        if cell is not None:
                            try_toggle_obstacle(grid, agent, cell)
            elif event.type == pygame.MOUSEBUTTONUP:
                speed_slider.handle_event(event)

        agent.speed_multiplier = speed_slider.value
        agent.update(dt)

        screen.fill(config.COLOR_BG)
        renderer.draw_grid()
        renderer.draw_bays(config.MISSIONS, agent.delivered_ids)
        renderer.draw_packages(config.MISSIONS, agent.delivered_ids, agent.carrying_package)
        if agent.state == Agent.STATE_MOVE:
            renderer.draw_path_preview(agent.current_path, agent.path_step)
        fx, fy = agent.render_position()
        renderer.draw_forklift(fx, fy, agent.carrying_package)
        renderer.draw_hud(agent)
        renderer.draw_log_panel(log_buffer)

        renderer.draw_control_bar_background()
        restart_button.draw(screen)
        speed_slider.draw(screen)
        renderer.draw_hint_text(hint_text, hint_pos)

        if agent.state == Agent.STATE_START_PAUSE:
            renderer.draw_state_banner("Warehouse Logistics Agent starting...")
        elif agent.state == Agent.STATE_BLOCKED:
            renderer.draw_state_banner("No path available — remove an obstacle to continue")
        elif agent.state == Agent.STATE_DONE:
            renderer.draw_state_banner("All deliveries complete! Press ESC to close.")

        pygame.display.flip()

        if headless:
            if agent.state == Agent.STATE_DONE:
                running = False
            if frame_count > frame_cap:
                log.info("!!! TEST TIMEOUT: simulation did not finish in time.")
                pygame.quit()
                sys.exit(1)

    pygame.quit()
    if headless:
        print("\n--test PASSED: simulation completed without errors.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Warehouse Logistics Agent (A*)")
    parser.add_argument("--test", action="store_true",
                         help="Run headless to completion and exit (no window) — sanity check")
    args = parser.parse_args()
    run(headless=args.test)
