from uav_ugv_mission.px4_control import arm_request, disarm_request, nav_land_request, offboard_mode_request


def test_px4_command_requests_are_explicit() -> None:
    assert offboard_mode_request().command == 176
    assert offboard_mode_request().params[:2] == (1.0, 6.0)
    assert arm_request().command == 400
    assert arm_request().params[0] == 1.0
    assert disarm_request().command == 400
    assert disarm_request().params[0] == 0.0
    assert nav_land_request().command == 21
