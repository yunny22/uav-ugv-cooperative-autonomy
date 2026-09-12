from uav_ugv_mission.landing_policy import LandingTarget, choose_landing_target


def test_fresh_team_marker_is_preferred() -> None:
    marker = LandingTarget("teammate_aruco_detection", (1.0, 2.0, 3.0))
    fallback = LandingTarget("coordinate_fallback", (9.0, 9.0, 9.0))
    assert choose_landing_target(marker, True, fallback) is marker


def test_stale_marker_does_not_implicitly_fallback() -> None:
    marker = LandingTarget("teammate_aruco_detection", (1.0, 2.0, 3.0))
    fallback = LandingTarget("coordinate_fallback", (9.0, 9.0, 9.0))
    assert choose_landing_target(marker, False, fallback) is None


def test_explicit_coordinate_fallback_is_opt_in() -> None:
    fallback = LandingTarget("coordinate_fallback", (9.0, 9.0, 9.0))
    assert choose_landing_target(None, False, fallback, True) is fallback
