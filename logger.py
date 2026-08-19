"""
Real-time decision logger for the warehouse agent.

Every line is (a) printed to the console with an elapsed-time stamp and
(b) captured into an in-memory ring buffer that the Pygame renderer reads
from to draw the live "Decision Log" panel inside the application window
itself — so the whole demo (grid + log) lives in one window.
"""

import logging
import time
import collections

_start_time = time.time()
_log_buffer = collections.deque(maxlen=500)


class ElapsedFormatter(logging.Formatter):
    def format(self, record):
        record.elapsed = time.time() - _start_time
        return super().format(record)


class InMemoryHandler(logging.Handler):
    """Feeds formatted log lines into the ring buffer the UI reads from."""

    def emit(self, record):
        if not record.getMessage().strip():
            return  # skip blank spacer lines — the panel is dense enough
        _log_buffer.append(self.format(record))


def get_log_buffer():
    """Returns the deque of formatted log lines for on-screen rendering."""
    return _log_buffer


def clear_log_buffer():
    """Wipes the on-screen log — used by the Restart button."""
    _log_buffer.clear()


def get_logger():
    logger = logging.getLogger("warehouse_agent")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    formatter = ElapsedFormatter("[t=%(elapsed)6.2fs] %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    memory_handler = InMemoryHandler()
    memory_handler.setFormatter(formatter)
    logger.addHandler(memory_handler)

    logger.propagate = False
    return logger
