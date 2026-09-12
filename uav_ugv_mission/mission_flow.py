"""Pure mission-flow model used by the ROS 2 integration adapter.

This module intentionally models commands and state transitions only. UGV
waypoint following, UAV waypoint flight, and ArUco detection remain external,
team-developed subsystems connected through documented ROS interfaces.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class MissionState(str, Enum):
    IDLE = "idle"
    UGV_TO_TRIGGER = "ugv_to_trigger"
    WAIT_FOR_UAV_TRIGGER = "wait_for_uav_trigger"
    UAV_EXPLORATION = "uav_exploration"
    RENDEZVOUS = "rendezvous"
    LANDING_SEQUENCE = "landing_sequence"
    COMPLETE = "complete"
    ABORTED = "aborted"


class MissionEvent(str, Enum):
    START = "MISSION_START"
    UGV_TRIGGER_REACHED = "UGV_TRIGGER_REACHED"
    ARUCO_TRIGGER_DETECTED = "ARUCO_TRIGGER_DETECTED"
    UAV_TAKEOFF_COMPLETE = "UAV_TAKEOFF_COMPLETE"
    UAV_EXPLORATION_COMPLETE = "UAV_EXPLORATION_COMPLETE"
    UGV_RENDEZVOUS_REACHED = "UGV_RENDEZVOUS_REACHED"
    UAV_APPROACH_READY = "UAV_APPROACH_READY"
    UAV_DISARMED = "UAV_DISARMED"
    ABORT = "ABORT"


@dataclass(frozen=True)
class Transition:
    """A transition and commands sent to external team subsystems."""

    state: MissionState
    commands: Tuple[str, ...] = ()


def advance(state: MissionState, event: MissionEvent) -> Transition:
    """Advance the cooperative mission for one verified integration event.

    Unexpected events are ignored. Hardware-specific timeouts, geofences,
    coordinate transforms, and vehicle safety checks must remain in the
    deployment configuration and vehicle-side safety system.
    """

    if event is MissionEvent.ABORT:
        return Transition(MissionState.ABORTED, ("UAV_ABORT", "UGV_STOP"))
    if state is MissionState.IDLE and event is MissionEvent.START:
        return Transition(MissionState.UGV_TO_TRIGGER, ("UGV_GO_TO_MISSION_2",))
    if state is MissionState.UGV_TO_TRIGGER and event is MissionEvent.UGV_TRIGGER_REACHED:
        return Transition(MissionState.WAIT_FOR_UAV_TRIGGER, ("ARUCO_TRIGGER_ENABLE",))
    if state is MissionState.WAIT_FOR_UAV_TRIGGER and event is MissionEvent.ARUCO_TRIGGER_DETECTED:
        return Transition(MissionState.UAV_EXPLORATION, ("UAV_TAKEOFF", "UAV_START_WAYPOINT_MISSION"))
    if state is MissionState.UAV_EXPLORATION and event is MissionEvent.UAV_TAKEOFF_COMPLETE:
        return Transition(MissionState.UAV_EXPLORATION)
    if state is MissionState.UAV_EXPLORATION and event is MissionEvent.UAV_EXPLORATION_COMPLETE:
        return Transition(MissionState.RENDEZVOUS, ("UGV_GO_TO_RENDEZVOUS", "UAV_GO_TO_RENDEZVOUS"))
    if state is MissionState.RENDEZVOUS and event is MissionEvent.UGV_RENDEZVOUS_REACHED:
        return Transition(MissionState.RENDEZVOUS, ("UAV_RETURN_TOWARD_UGV", "ARUCO_LANDING_ENABLE"))
    if state is MissionState.RENDEZVOUS and event is MissionEvent.UAV_APPROACH_READY:
        return Transition(MissionState.LANDING_SEQUENCE, ("UAV_BEGIN_LANDING_SEQUENCE",))
    if state is MissionState.LANDING_SEQUENCE and event is MissionEvent.UAV_DISARMED:
        return Transition(MissionState.COMPLETE, ("UGV_STOP",))
    return Transition(state)
