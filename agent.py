"""
Forklift agent: turns config.MISSIONS into an ordered sequence of A* legs
and drives a small state machine that the Pygame main loop steps forward
every frame via update(dt).

This version is interactive: the person watching can click grid cells to
drop or remove obstacles while the forklift is mid-route. If a new
obstacle blocks the path currently being driven, the agent replans live
with A* (notify_obstacle_added). If the person accidentally seals off
every route to the goal, the agent parks safely in STATE_BLOCKED and
automatically retries as soon as an obstacle is cleared
(notify_obstacle_removed) — it never crashes or gets stuck silently.

State machine
-------------
START_PAUSE -> PLAN -> MOVE -> (PICKUP_PAUSE | DELIVER_PAUSE) -> PLAN -> ...
                          |                                        ^
                          +-> (user obstacle blocks path)          |
                                  -> REPLAN_PAUSE -> MOVE           |
                          +-> (no path exists) -> BLOCKED -----------+
                                  (waits; retries when an obstacle is
                                   removed)
... -> DONE
"""

from astar import astar_search
from logger import get_logger
import config

log = get_logger()


class Agent:
    STATE_START_PAUSE = "START_PAUSE"
    STATE_PLAN = "PLAN"
    STATE_MOVE = "MOVE"
    STATE_PICKUP_PAUSE = "PICKUP_PAUSE"
    STATE_DELIVER_PAUSE = "DELIVER_PAUSE"
    STATE_REPLAN_PAUSE = "REPLAN_PAUSE"
    STATE_BLOCKED = "BLOCKED"
    STATE_DONE = "DONE"

    def __init__(self, grid):
        self.grid = grid
        self.legs = self._build_legs()
        self.leg_index = 0
        self.position = config.FORKLIFT_START      # current CELL (int coords)
        self.state = Agent.STATE_START_PAUSE
        self.state_timer = 0.0

        self.current_path = []
        self.path_step = 0
        self.move_progress = 0.0                   # 0..1 between path_step and +1

        self.total_cost = 0
        self.total_nodes_expanded = 0
        self.leg_cost = 0
        self.leg_nodes_expanded = 0

        self.carrying_package = None
        self.delivered_ids = set()

        # Live speed multiplier, driven by the UI slider (1.0 = normal).
        self.speed_multiplier = config.SPEED_DEFAULT

        log.info("=" * 64)
        log.info("WAREHOUSE LOGISTICS AGENT — A* Search (Manhattan heuristic)")
        log.info(f"Start dock: {config.FORKLIFT_START} | Missions: "
                 f"{len(config.MISSIONS)} package(s) -> {len(self.legs)} planning legs")
        log.info("Click any open cell to drop/remove an obstacle at any time.")
        log.info("=" * 64)

    # ------------------------------------------------------------------
    @staticmethod
    def _build_legs():
        legs = []
        cursor = config.FORKLIFT_START
        for mission in config.MISSIONS:
            legs.append({
                "kind": "pickup",
                "label": f"{cursor} -> Package {mission['package_id']}",
                "start": cursor,
                "goal": mission["package_cell"],
                "mission": mission,
            })
            legs.append({
                "kind": "deliver",
                "label": f"Package {mission['package_id']} -> Bay {mission['bay_id']}",
                "start": mission["package_cell"],
                "goal": mission["bay_cell"],
                "mission": mission,
            })
            cursor = mission["bay_cell"]
        return legs

    # ------------------------------------------------------------------
    # Cells the click-to-obstacle UI must refuse to block
    # ------------------------------------------------------------------
    def protected_cells(self):
        """The forklift's own cell, plus any package/bay location still
        needed for an undelivered mission — placing an obstacle on these
        would either trap the agent or make a leg unsolvable."""
        protected = {self.position}
        for mission in config.MISSIONS:
            pid = mission["package_id"]
            if pid in self.delivered_ids:
                continue
            if pid != self.carrying_package:
                protected.add(mission["package_cell"])
            protected.add(mission["bay_cell"])
        return protected

    # ------------------------------------------------------------------
    # Planning
    # ------------------------------------------------------------------
    def _plan_current_leg(self):
        leg = self.legs[self.leg_index]
        log.info("")
        log.info(f"--- LEG {self.leg_index + 1}/{len(self.legs)}: {leg['label']} ---")
        log.info(f"A* search started | start={leg['start']} goal={leg['goal']} "
                 f"| h(n) = |x1-x2| + |y1-y2|")

        def on_expand(cell, g, h, f, n):
            log.info(f"    expand {cell}  g={g:<3} h={h:<3} f={f:<3} (#{n})")

        result = astar_search(self.grid, leg["start"], leg["goal"], on_expand=on_expand)

        if not result.found:
            log.info(f"!!! No path currently exists to {leg['goal']} — probably boxed in "
                     f"by user-placed obstacles. Remove one to let the agent continue.")
            self.state = Agent.STATE_BLOCKED
            return

        self.current_path = result.path
        self.path_step = 0
        self.move_progress = 0.0
        self.leg_cost = result.cost
        self.leg_nodes_expanded = result.nodes_expanded
        self.total_cost += result.cost
        self.total_nodes_expanded += result.nodes_expanded

        log.info(f"GOAL REACHED (search) | path length={len(result.path)} cells | "
                 f"path cost={result.cost} | nodes expanded={result.nodes_expanded}")
        log.info(f"Optimal path: {result.path}")
        self.state = Agent.STATE_MOVE

    # ------------------------------------------------------------------
    # Per-frame update — dt in seconds
    # ------------------------------------------------------------------
    def update(self, dt):
        if self.state == Agent.STATE_START_PAUSE:
            self._tick_pause(dt, config.START_PAUSE_MS, Agent.STATE_PLAN)

        elif self.state == Agent.STATE_PLAN:
            self._plan_current_leg()

        elif self.state == Agent.STATE_MOVE:
            self._update_move(dt)

        elif self.state == Agent.STATE_PICKUP_PAUSE:
            self._tick_pause(dt, config.PICKUP_PAUSE_MS, None, advance=True)

        elif self.state == Agent.STATE_DELIVER_PAUSE:
            self._tick_pause(dt, config.DELIVER_PAUSE_MS, None, advance=True)

        elif self.state == Agent.STATE_REPLAN_PAUSE:
            self._tick_pause(dt, config.REPLAN_PAUSE_MS, Agent.STATE_MOVE)

        # STATE_BLOCKED: idles until notify_obstacle_removed() retries it.
        # STATE_DONE: nothing to do, simulation finished.

    def _tick_pause(self, dt, duration_ms, next_state, advance=False):
        self.state_timer += dt * self.speed_multiplier
        if self.state_timer >= duration_ms / 1000:
            self.state_timer = 0.0
            if advance:
                self._advance_to_next_leg()
            else:
                self.state = next_state

    def _advance_to_next_leg(self):
        self.leg_index += 1
        if self.leg_index >= len(self.legs):
            self.state = Agent.STATE_DONE
            log.info("")
            log.info("=" * 64)
            log.info("ALL DELIVERIES COMPLETE")
            log.info(f"TOTAL PATH COST (sum of all legs):     {self.total_cost}")
            log.info(f"TOTAL NODES EXPANDED (sum of all legs): {self.total_nodes_expanded}")
            log.info("=" * 64)
        else:
            self.state = Agent.STATE_PLAN

    # ------------------------------------------------------------------
    def _update_move(self, dt):
        # Reached the end of the current path -> pickup or deliver
        if not self.current_path or self.path_step >= len(self.current_path) - 1:
            leg = self.legs[self.leg_index]
            self.position = leg["goal"]
            if leg["kind"] == "pickup":
                self.carrying_package = leg["mission"]["package_id"]
                log.info(f"Package {leg['mission']['package_id']} picked up at {leg['goal']}.")
                self.state = Agent.STATE_PICKUP_PAUSE
            else:
                log.info(f"Package {leg['mission']['package_id']} delivered to "
                         f"Bay {leg['mission']['bay_id']} at {leg['goal']}.")
                self.delivered_ids.add(leg["mission"]["package_id"])
                self.carrying_package = None
                self.state = Agent.STATE_DELIVER_PAUSE
            self.state_timer = 0.0
            return

        effective_cell_ms = config.BASE_CELL_MOVE_MS / self.speed_multiplier
        self.move_progress += dt * 1000 / effective_cell_ms
        if self.move_progress >= 1.0:
            self.move_progress = 0.0
            self.path_step += 1
            self.position = self.current_path[self.path_step]

    # ------------------------------------------------------------------
    # Called by the UI when the player clicks a cell to add/remove an
    # obstacle. This is what makes replanning genuinely interactive
    # instead of a scripted, one-shot event.
    # ------------------------------------------------------------------
    def notify_obstacle_added(self, cell):
        if self.state != Agent.STATE_MOVE or not self.current_path:
            return  # not mid-route — the next leg's A* search will see it naturally
        remaining = self.current_path[self.path_step + 1:]
        if cell not in remaining:
            return  # doesn't block the path currently being driven
        self._replan_from_here(f"user placed an obstacle at {cell}, blocking the current path")

    def notify_obstacle_removed(self, cell):
        if self.state == Agent.STATE_BLOCKED:
            log.info(f"Obstacle at {cell} removed — retrying the blocked leg...")
            self._plan_current_leg()

    def _replan_from_here(self, reason):
        goal = self.legs[self.leg_index]["goal"]
        log.info("")
        log.info(f"!!! REPLAN TRIGGERED — {reason} !!!")
        log.info(f"Replanning from current position {self.position} to {goal} ...")

        def on_expand(cell, g, h, f, n):
            log.info(f"    expand {cell}  g={g:<3} h={h:<3} f={f:<3} (#{n})")

        result = astar_search(self.grid, self.position, goal, on_expand=on_expand)

        if result.found:
            self.current_path = result.path
            self.path_step = 0
            self.move_progress = 0.0
            self.leg_nodes_expanded += result.nodes_expanded
            self.total_nodes_expanded += result.nodes_expanded
            log.info(f"REPLAN SUCCESSFUL | new path cost from here={result.cost} | "
                     f"nodes expanded this replan={result.nodes_expanded}")
            log.info(f"New path: {result.path}")
            self.state = Agent.STATE_REPLAN_PAUSE
            self.state_timer = 0.0
        else:
            log.info("!!! No path remains to the goal — parking until an obstacle "
                     "is removed.")
            self.state = Agent.STATE_BLOCKED

    # ------------------------------------------------------------------
    def render_position(self):
        """Returns a float (x, y) grid coordinate for smooth Pygame drawing."""
        if (self.state == Agent.STATE_MOVE and self.current_path
                and self.path_step < len(self.current_path) - 1):
            cx, cy = self.current_path[self.path_step]
            nx, ny = self.current_path[self.path_step + 1]
            t = self.move_progress
            return (cx + (nx - cx) * t, cy + (ny - cy) * t)
        return self.position
