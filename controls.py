"""
Small, self-contained Pygame UI widgets — a clickable Button and a
draggable Slider — used for the Restart button and the speed slider in
the control bar. No external UI library needed; kept intentionally
lightweight for a hackathon-scoped Pygame app.
"""

import pygame
import config


class Button:
    def __init__(self, rect, label, font):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.font = font
        self.hovered = False

    def handle_mousemove(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, screen):
        color = config.COLOR_BUTTON_HOVER if self.hovered else config.COLOR_BUTTON
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        pygame.draw.rect(screen, config.COLOR_BUTTON_EDGE, self.rect, 2, border_radius=6)
        text = self.font.render(self.label, True, config.COLOR_TEXT_LIGHT)
        screen.blit(text, text.get_rect(center=self.rect.center))


class Slider:
    """Horizontal slider mapping a pixel position to a value in
    [min_value, max_value]. Click-and-drag anywhere on the track."""

    HANDLE_W = 14
    HANDLE_H = 18

    def __init__(self, rect, min_value, max_value, value, label, font, value_fmt="{:.1f}x"):
        self.rect = pygame.Rect(rect)
        self.min_value = min_value
        self.max_value = max_value
        self.value = value
        self.label = label
        self.font = font
        self.value_fmt = value_fmt
        self.dragging = False

    def _value_to_x(self, value):
        t = (value - self.min_value) / (self.max_value - self.min_value)
        return self.rect.x + int(t * self.rect.width)

    def _x_to_value(self, x):
        t = (x - self.rect.x) / self.rect.width
        t = max(0.0, min(1.0, t))
        return self.min_value + t * (self.max_value - self.min_value)

    def _handle_rect(self):
        hx = self._value_to_x(self.value)
        return pygame.Rect(hx - self.HANDLE_W // 2, self.rect.centery - self.HANDLE_H // 2,
                            self.HANDLE_W, self.HANDLE_H)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            hit_zone = self._handle_rect().inflate(10, 10)
            if hit_zone.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                self.value = self._x_to_value(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.value = self._x_to_value(event.pos[0])

    def draw(self, screen):
        label_surf = self.font.render(
            f"{self.label}: {self.value_fmt.format(self.value)}", True, config.COLOR_HUD_TEXT)
        screen.blit(label_surf, (self.rect.x, self.rect.y - 18))
        pygame.draw.rect(screen, config.COLOR_SLIDER_TRACK, self.rect, border_radius=4)
        pygame.draw.rect(screen, config.COLOR_HUD_ACCENT, self._handle_rect(), border_radius=4)
