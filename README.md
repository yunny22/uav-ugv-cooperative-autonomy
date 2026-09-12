# UAV–UGV Cooperative Autonomous System

This repository is provided for portfolio and research demonstration purposes.
No separate open-source reuse license is granted; third-party dependencies keep
their own terms.

This is a public-release **staging** repository for a ROS 2, PX4, and Gazebo
UAV–UGV cooperative autonomous mission. It preserves the personal UAV
takeoff/landing and mission-integration scope as a small, public-safe package;
team-owned UGV waypoint, UAV waypoint, and ArUco detector implementations are
represented as interfaces rather than copied source.

## Overview

The team developed subsystem functions independently, then connected them as a
single ROS 2/PX4 mission. The portfolio owner's contribution was the UAV
takeoff/landing implementation, independent validation of that sequence, and
the overall mission integration. This repository deliberately does not claim
that the UGV waypoint driver, UAV waypoint flight logic, or ArUco detector was
implemented by one person.

## Mission Scenario — Team Scope

1. The UGV drives by waypoint to Mission 2.
2. The UGV camera detects ArUco ID 0 and triggers the UAV mission.
3. The UAV takes off above the UGV and visits exploration points.
4. The UAV records ArUco information and the UAV/UGV proceed to rendezvous.
5. The UGV reaches the rendezvous position while the UAV returns toward the
   UGV top.
6. The landing sequence runs and the UAV is disarmed after landing.

The sequence is a team mission. The implementation details of the waypoint
drivers and marker detector are not included here.

## System Architecture

```text
UGV waypoint driver (team) ─┐
UAV waypoint flight (team) ─┼─> mission events ─> Mission Controller ─> subsystem commands
ArUco detector (team) ──────┘                              │
                                                            └─> UAV takeoff/landing adapter
                                                                    │
                                                                    └─> PX4 offboard commands
```

The controller exposes the mission events and commands in
[`uav_ugv_mission/mission_flow.py`](uav_ugv_mission/mission_flow.py). It is an
integration boundary, not a replacement for the three team subsystems.

## UAV Takeoff & Landing

The retained personal scope is represented by
[`uav_ugv_mission/takeoff_landing.py`](uav_ugv_mission/takeoff_landing.py).
The source evidence for the original independent validation sequence includes:

- PX4 offboard setpoint handshake and offboard-mode / arm commands,
- a takeoff position setpoint and altitude-band completion check,
- a landing-stage command gated by a fresh marker result,
- PX4 `NAV_LAND`, followed by a separately gated disarm step.

The staging adapter defaults to `enable_vehicle_commands: false`. It must not
be treated as a vehicle-ready controller without a reviewed transform chain,
vehicle safety logic, and hardware validation.

## Mission Integration

The original integrated launch connected Gazebo, the UGV mission, the UAV
mission, the ArUco detector, and the mission controller. The public release
replaces those mixed-source launches with a compact event/state adapter:

```text
UGV trigger reached → ArUco trigger enabled → UAV takeoff / waypoint mission
→ exploration complete → UGV + UAV rendezvous → UAV approach
→ marker-gated landing request → disarm event
```

This makes the integration responsibility inspectable without redistributing
team subsystem source or simulator packages.

## ArUco-assisted Landing Integration

Initial coordinate/vehicle-frame landing was not accurate enough. The landing
phase was therefore integrated with a teammate-developed
`vision_msgs/Detection3DArray` result on `/marker_detections`: a fresh matching
marker pose plus configured offset can be selected as a landing target before
the `NAV_LAND` request is issued.

The ArUco detector, marker-pose estimation, and any visual-servoing algorithm
are not included here and are not claimed as personal work. Coordinate-only
fallback is disabled by default and must be explicitly enabled in a reviewed
deployment configuration.

## My Contribution

- Implemented UAV takeoff and landing behavior.
- Validated the takeoff/landing sequence independently.
- Integrated the mission-controller flow with ROS 2/PX4 command interfaces.
- Connected independently developed UGV, UAV, and marker-detection subsystems
  into one cooperative mission sequence.

## Team Contributions

- **UGV waypoint driving:** team-developed subsystem.
- **UAV waypoint flight:** team-developed subsystem.
- **ArUco detection:** team-developed subsystem whose output is consumed by
  the landing integration.

The team has approved publication of the retained source. Contributor boundaries
are recorded in [docs/TEAM_CREDITS.md](docs/TEAM_CREDITS.md).

## Result

Source and launch evidence supports independent takeoff/landing validation and
an integrated Gazebo mission flow. This repository makes no unsupported claim
about precision-landing accuracy, repeated success rate, or hardware results.

## Limitation

Landing based only on vehicle coordinates did not provide sufficient accuracy.
The final integration depended on a fresh detector result, but detector
robustness, transform calibration, safety envelopes, and real-hardware
validation are external to this curated release.

## Repository Structure

```text
uav_ugv_mission/        Public-safe mission state, landing policy, and ROS 2 adapters
launch/                 Minimal integration and dry-run launch descriptions
config/                 Parameter template with no track coordinates
docs/                   Architecture, credits, and release-provenance records
test/                   Pure-Python state and policy tests
```

## Environment

The original development source uses ROS 2, PX4, and Gazebo. This package also
expects `px4_msgs` and `vision_msgs` in the active ROS 2 environment. Exact
versions, simulator assets, vehicle configuration, and camera calibration are
intentionally not bundled.

## How to Run

1. Create a ROS 2 workspace and place this package under `src/`.
2. Install the ROS 2 dependencies and make `px4_msgs` / `vision_msgs` available.
3. Build and source the workspace:

   ```bash
   colcon build --packages-select uav_ugv_mission
   source install/setup.bash
   ```

4. Inspect the dry-run integration graph:

   ```bash
   ros2 launch uav_ugv_mission cooperative_mission.launch.py
   ```

The launch defaults to dry-run operation. Do not enable vehicle commands or
connect PX4 hardware without reviewed transforms, safety checks, and an
approved deployment configuration.

## Team / Credits

This was a team project. The original development tree originated from a shared
utility repository, but this staging repository is a selective, parameterized
release rather than a copy of the original workspace. Team publication consent
is confirmed, and no separate open-source reuse license is granted. See
[PUBLIC_RELEASE_NOTES.md](PUBLIC_RELEASE_NOTES.md) and
[docs/TEAM_CREDITS.md](docs/TEAM_CREDITS.md).
