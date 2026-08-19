"""
Tests for the Button and Slider widgets (controls.py).

Run with:
    python tests/test_controls.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.font.init()

from controls import Button, Slider

FONT = pygame.font.SysFont("consolas", 14)


def test_button_hover_and_click():
    btn = Button((10, 10, 100, 30), "Restart", FONT)
    assert btn.is_clicked((50, 20))
    assert not btn.is_clicked((500, 500))
    btn.handle_mousemove((50, 20))
    assert btn.hovered
    btn.handle_mousemove((500, 500))
    assert not btn.hovered
    print("test_button_hover_and_click PASSED")


def test_slider_drag_updates_value_within_range():
    slider = Slider((100, 50, 200, 8), 0.5, 3.0, 1.0, "Speed", FONT)

    slider.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(100, 50), button=1))
    assert slider.dragging
    assert slider.value == 0.5  # clicked at the very left edge of the track

    slider.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=(300, 50)))
    assert abs(slider.value - 3.0) < 1e-6  # dragged to the right edge

    slider.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(300, 50)))
    assert not slider.dragging
    print("test_slider_drag_updates_value_within_range PASSED")


def test_slider_click_outside_track_ignored():
    slider = Slider((100, 50, 200, 8), 0.5, 3.0, 1.0, "Speed", FONT)
    slider.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(900, 900), button=1))
    assert not slider.dragging
    assert slider.value == 1.0
    print("test_slider_click_outside_track_ignored PASSED")


if __name__ == "__main__":
    test_button_hover_and_click()
    test_slider_drag_updates_value_within_range()
    test_slider_click_outside_track_ignored()
    print("\nAll control widget tests passed.")
