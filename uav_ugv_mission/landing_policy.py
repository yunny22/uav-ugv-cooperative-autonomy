"""Landing-target selection policy independent of ROS message types.

The original integration consumed a teammate-provided ``Detection3DArray``.
This module records that interface boundary: a fresh marker result can be used
as the landing target; coordinate-only fallback requires an explicit opt-in.
It is not a precision-landing or visual-servoing implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class LandingTarget:
    source: str
    position: Tuple[float, float, float]


def choose_landing_target(
    marker_target: Optional[LandingTarget],
    marker_is_fresh: bool,
    fallback_target: Optional[LandingTarget],
    allow_coordinate_fallback: bool = False,
) -> Optional[LandingTarget]:
    """Prefer a fresh marker target and otherwise reject unsafe implicit fallbacks."""

    if marker_target is not None and marker_is_fresh:
        return marker_target
    if allow_coordinate_fallback and fallback_target is not None:
        return fallback_target
    return None
