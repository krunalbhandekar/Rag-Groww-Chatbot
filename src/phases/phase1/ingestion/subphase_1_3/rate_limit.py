"""Subphase 1.3 — sequential spacing between requests (concurrency cap = 1)."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class SequentialRateLimit:
    """At most one in-flight request; sleep `delay_s` before each request after the first."""

    delay_s: float = 1.0
    _first: bool = field(default=True, init=False, repr=False)

    def wait_turn(self) -> None:
        if self._first:
            self._first = False
            return
        if self.delay_s > 0:
            time.sleep(self.delay_s)

    def reset(self) -> None:
        self._first = True
