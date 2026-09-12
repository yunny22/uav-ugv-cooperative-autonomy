from uav_ugv_mission.mission_flow import MissionEvent, MissionState, advance


def test_nominal_team_mission_flow() -> None:
    state = MissionState.IDLE
    transitions = [
        MissionEvent.START,
        MissionEvent.UGV_TRIGGER_REACHED,
        MissionEvent.ARUCO_TRIGGER_DETECTED,
        MissionEvent.UAV_EXPLORATION_COMPLETE,
        MissionEvent.UGV_RENDEZVOUS_REACHED,
        MissionEvent.UAV_APPROACH_READY,
        MissionEvent.UAV_DISARMED,
    ]
    for event in transitions:
        state = advance(state, event).state
    assert state is MissionState.COMPLETE


def test_abort_stops_the_mission() -> None:
    transition = advance(MissionState.UAV_EXPLORATION, MissionEvent.ABORT)
    assert transition.state is MissionState.ABORTED
    assert transition.commands == ("UAV_ABORT", "UGV_STOP")
