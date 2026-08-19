"""
Pygame rendering for the warehouse grid, forklift, packages, bays and HUD.
Kept separate from simulation logic (agent.py, astar.py) so the algorithm
stays fully UI-agnostic and unit-testable.
"""

import pygame
import config


class Renderer:
    def __init__(self, screen, grid):
        self.screen = screen
        self.grid = grid
        self.font_hud = pygame.font.SysFont("consolas,menlo,monospace", 20, bold=True)
        self.font_hud_small = pygame.font.SysFont("consolas,menlo,monospace", 13)
        self.font_cell = pygame.font.SysFont("consolas,menlo,monospace", 13, bold=True)
        self.font_log = pygame.font.SysFont("consolas,menlo,monospace", 12)
        self.font_log_header = pygame.font.SysFont("consolas,menlo,monospace", 13, bold=True)

    # ------------------------------------------------------------------
    def cell_to_px(self, cell_x, cell_y):
        return (cell_x * config.CELL_SIZE, cell_y * config.CELL_SIZE + config.HUD_HEIGHT)

    def draw_grid(self):
        for y in range(self.grid.rows):
            for x in range(self.grid.cols):
                px, py = self.cell_to_px(x, y)
                rect = pygame.Rect(px, py, config.CELL_SIZE, config.CELL_SIZE)
                base = config.COLOR_FLOOR if (x + y) % 2 == 0 else config.COLOR_FLOOR_ALT
                pygame.draw.rect(self.screen, base, rect)
                pygame.draw.rect(self.screen, config.COLOR_GRID_LINE, rect, 1)

        for y in range(self.grid.rows):
            for x in range(self.grid.cols):
                if self.grid.is_static_wall((x, y)):
                    self._draw_shelf(x, y)

        for cell in self.grid.dynamic_obstacles:
            self._draw_obstacle(*cell)

    def _draw_shelf(self, x, y):
        px, py = self.cell_to_px(x, y)
        rect = pygame.Rect(px + 3, py + 3, config.CELL_SIZE - 6, config.CELL_SIZE - 6)
        pygame.draw.rect(self.screen, config.COLOR_SHELF, rect, border_radius=4)
        pygame.draw.rect(self.screen, config.COLOR_SHELF_EDGE, rect, 2, border_radius=4)
        for i in range(1, 3):
            ly = py + 3 + i * (config.CELL_SIZE - 6) // 3
            pygame.draw.line(self.screen, config.COLOR_SHELF_EDGE,
                              (px + 5, ly), (px + config.CELL_SIZE - 5, ly), 1)

    def _draw_obstacle(self, x, y):
        px, py = self.cell_to_px(x, y)
        rect = pygame.Rect(px + 4, py + 4, config.CELL_SIZE - 8, config.CELL_SIZE - 8)
        pygame.draw.rect(self.screen, config.COLOR_OBSTACLE_NEW, rect, border_radius=6)
        pygame.draw.rect(self.screen, (140, 30, 30), rect, 2, border_radius=6)
        label = self.font_cell.render("!", True, (255, 255, 255))
        self.screen.blit(label, label.get_rect(center=rect.center))

    def draw_packages(self, missions, delivered_ids, carrying_id):
        for m in missions:
            if m["package_id"] == carrying_id or m["package_id"] in delivered_ids:
                continue
            x, y = m["package_cell"]
            px, py = self.cell_to_px(x, y)
            rect = pygame.Rect(px + 12, py + 12, config.CELL_SIZE - 24, config.CELL_SIZE - 24)
            pygame.draw.rect(self.screen, config.COLOR_PACKAGE, rect, border_radius=3)
            pygame.draw.rect(self.screen, config.COLOR_PACKAGE_EDGE, rect, 2, border_radius=3)
            label = self.font_cell.render(m["package_id"], True, (255, 255, 255))
            self.screen.blit(label, label.get_rect(center=rect.center))

    def draw_bays(self, missions, delivered_ids):
        for m in missions:
            x, y = m["bay_cell"]
            px, py = self.cell_to_px(x, y)
            rect = pygame.Rect(px + 2, py + 2, config.CELL_SIZE - 4, config.CELL_SIZE - 4)
            filled = m["package_id"] in delivered_ids
            color = config.COLOR_BAY if filled else (255, 255, 255)
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            pygame.draw.rect(self.screen, config.COLOR_BAY_EDGE, rect, 2, border_radius=5)
            text_color = (255, 255, 255) if filled else config.COLOR_BAY_EDGE
            label = self.font_cell.render(f"Bay{m['bay_id']}", True, text_color)
            self.screen.blit(label, label.get_rect(center=rect.center))

    def draw_path_preview(self, path, step):
        if not path:
            return
        for i, cell in enumerate(path):
            x, y = cell
            px, py = self.cell_to_px(x, y)
            color = config.COLOR_VISITED if i <= step else config.COLOR_PATH
            center = (px + config.CELL_SIZE // 2, py + config.CELL_SIZE // 2)
            pygame.draw.circle(self.screen, color, center, 4)

    def draw_forklift(self, fx, fy, carrying):
        px = fx * config.CELL_SIZE + config.CELL_SIZE // 2
        py = fy * config.CELL_SIZE + config.CELL_SIZE // 2 + config.HUD_HEIGHT
        body = pygame.Rect(0, 0, config.CELL_SIZE - 16, config.CELL_SIZE - 20)
        body.center = (px, py)
        pygame.draw.rect(self.screen, config.COLOR_FORKLIFT, body, border_radius=6)
        pygame.draw.rect(self.screen, config.COLOR_FORKLIFT_EDGE, body, 2, border_radius=6)
        pygame.draw.line(self.screen, config.COLOR_FORKLIFT_EDGE,
                          (body.left - 6, body.top + 4), (body.left, body.top + 4), 3)
        pygame.draw.line(self.screen, config.COLOR_FORKLIFT_EDGE,
                          (body.left - 6, body.bottom - 4), (body.left, body.bottom - 4), 3)
        if carrying:
            box = pygame.Rect(0, 0, 14, 14)
            box.center = (px, py - 2)
            pygame.draw.rect(self.screen, config.COLOR_PACKAGE, box, border_radius=2)
            pygame.draw.rect(self.screen, config.COLOR_PACKAGE_EDGE, box, 1, border_radius=2)

    def draw_hud(self, agent):
        rect = pygame.Rect(0, 0, config.WINDOW_WIDTH, config.HUD_HEIGHT)
        pygame.draw.rect(self.screen, config.COLOR_HUD_BG, rect)

        leg = agent.legs[agent.leg_index] if agent.leg_index < len(agent.legs) else None
        leg_text = leg["label"] if leg else "All missions complete"
        title = self.font_hud.render(
            f"Leg {min(agent.leg_index + 1, len(agent.legs))}/{len(agent.legs)}: {leg_text}",
            True, config.COLOR_HUD_TEXT)
        self.screen.blit(title, (14, 8))

        stats = (f"Leg cost:{agent.leg_cost}  Leg nodes:{agent.leg_nodes_expanded}  "
                 f"Total cost:{agent.total_cost}  Total nodes:{agent.total_nodes_expanded}")
        stats_surf = self.font_hud_small.render(stats, True, config.COLOR_HUD_ACCENT)
        self.screen.blit(stats_surf, (14, 38))

    def draw_state_banner(self, text):
        surf = self.font_hud.render(text, True, config.COLOR_TEXT_DARK)
        bg_rect = surf.get_rect()
        bg_rect.center = (config.GRID_AREA_WIDTH // 2,
                           config.HUD_HEIGHT + config.GRID_AREA_HEIGHT // 2)
        bg_rect.inflate_ip(40, 24)
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, border_radius=10)
        pygame.draw.rect(self.screen, config.COLOR_HUD_ACCENT, bg_rect, 3, border_radius=10)
        self.screen.blit(surf, surf.get_rect(center=bg_rect.center))

    # ------------------------------------------------------------------
    # Live decision-log panel — renders the same lines that go to the
    # console, inside the application window itself.
    # ------------------------------------------------------------------
    def draw_log_panel(self, log_lines):
        panel_x = config.GRID_AREA_WIDTH
        panel_rect = pygame.Rect(panel_x, config.HUD_HEIGHT,
                                  config.LOG_PANEL_WIDTH, config.GRID_AREA_HEIGHT)
        pygame.draw.rect(self.screen, config.COLOR_LOG_BG, panel_rect)

        header_rect = pygame.Rect(panel_x, config.HUD_HEIGHT,
                                   config.LOG_PANEL_WIDTH, config.LOG_HEADER_HEIGHT)
        pygame.draw.rect(self.screen, config.COLOR_LOG_HEADER_BG, header_rect)
        header_label = self.font_log_header.render(
            "LIVE DECISION LOG", True, config.COLOR_LOG_SECTION)
        self.screen.blit(header_label, (panel_x + 10, config.HUD_HEIGHT + 6))

        line_h = 15
        text_top = config.HUD_HEIGHT + config.LOG_HEADER_HEIGHT + 5
        panel_bottom = config.HUD_HEIGHT + config.GRID_AREA_HEIGHT
        available_h = panel_bottom - text_top
        max_lines = max(1, available_h // line_h)

        visible = list(log_lines)[-max_lines:]
        max_text_width = config.LOG_PANEL_WIDTH - 20
        y = text_top
        for line in visible:
            color = self._classify_log_color(line)
            line = self._truncate_to_width(line, self.font_log, max_text_width)
            surf = self.font_log.render(line, True, color)
            self.screen.blit(surf, (panel_x + 10, y))
            y += line_h

        pygame.draw.line(self.screen, config.COLOR_GRID_LINE,
                          (panel_x, 0), (panel_x, panel_bottom), 2)

    @staticmethod
    def _classify_log_color(line):
        if "!!!" in line:
            return config.COLOR_LOG_WARNING
        if any(k in line for k in ("REPLAN SUCCESSFUL", "delivered", "picked up",
                                    "GOAL REACHED", "ALL DELIVERIES COMPLETE")):
            return config.COLOR_LOG_SUCCESS
        if any(k in line for k in ("===", "---", "LEG ")):
            return config.COLOR_LOG_SECTION
        if "expand" in line:
            return config.COLOR_LOG_DIM
        return config.COLOR_LOG_TEXT

    @staticmethod
    def _truncate_to_width(text, font, max_width):
        if font.size(text)[0] <= max_width:
            return text
        while text and font.size(text + "...")[0] > max_width:
            text = text[:-1]
        return text + "..."

    # ------------------------------------------------------------------
    # Bottom control bar background + hint text. The Restart button and
    # speed Slider (controls.py) draw themselves on top of this.
    # ------------------------------------------------------------------
    def draw_control_bar_background(self):
        rect = pygame.Rect(0, config.HUD_HEIGHT + config.GRID_AREA_HEIGHT,
                            config.WINDOW_WIDTH, config.CONTROL_BAR_HEIGHT)
        pygame.draw.rect(self.screen, config.COLOR_CONTROL_BG, rect)
        pygame.draw.line(self.screen, config.COLOR_GRID_LINE,
                          (0, rect.top), (config.WINDOW_WIDTH, rect.top), 2)

    def draw_hint_text(self, text, pos):
        surf = self.font_hud_small.render(text, True, config.COLOR_HINT_TEXT)
        self.screen.blit(surf, pos)
