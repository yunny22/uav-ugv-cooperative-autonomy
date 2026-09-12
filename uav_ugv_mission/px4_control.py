"""Small PX4 command helpers kept free of vehicle-specific configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class VehicleCommandRequest:
    command: int
    params: Tuple[float, float, float, float, float, float, float] = (0.0,) * 7


def arm_request() -> VehicleCommandRequest:
    """Return the PX4 arm command request."""

    return VehicleCommandRequest(command=400, params=(1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))


def offboard_mode_request() -> VehicleCommandRequest:
    """Return the PX4 command request that selects external offboard mode."""

    return VehicleCommandRequest(command=176, params=(1.0, 6.0, 0.0, 0.0, 0.0, 0.0, 0.0))


def disarm_request() -> VehicleCommandRequest:
    """Return the PX4 disarm command request."""

    return VehicleCommandRequest(command=400, params=(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))


def nav_land_request() -> VehicleCommandRequest:
    """Return the PX4 navigation-land command request."""

    return VehicleCommandRequest(command=21)
