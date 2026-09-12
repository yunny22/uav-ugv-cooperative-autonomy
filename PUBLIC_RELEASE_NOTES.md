# Public Release Notes

## Source Selection

The primary candidate is the local `utilities_pkg` working tree at Git revision
`d7d257d699719c03d46ceb4b322ea49395a34f5c` (`2026-06-04`, `yunny22`,
`Gate UGV landing on marker detection`). Its branch relation is
`master...practice/main`; the configured origins are the external
`YoungRok-SON/utilities_pkg` repository and the secondary `yunny22/practice`
repository. The source tree was already dirty in the integrated launch, UAV
waypoint mission, and generated marker CSV. It was inspected only; it was not
modified, reset, or cleaned.

Historical copies were reviewed only as divergent references and were not
merged automatically.

## Final Mission Files

The final source relation supports the integrated launch, mission controller,
independent takeoff/landing node, and team-owned waypoint/detector modules.
This public release retains a public-safe rewrite of the mission state flow,
PX4 command boundary, marker-gated landing-policy interface, and launch
templates. It is not a byte-for-byte snapshot of the shared workspace.

## Personal Contribution

- UAV takeoff implementation.
- UAV landing implementation.
- Independent takeoff/landing validation.
- ROS 2/PX4 mission integration.
- Integration of independently developed UGV, UAV, and marker subsystems into
  one cooperative mission flow.

## Team Contribution

- UGV waypoint driving.
- UAV waypoint flight.
- ArUco detection and marker-pose estimation.

These are documented as interfaces and credits, not as personal implementations.

## Provenance

| Source area | Classification | Public-release handling |
|---|---|---|
| `takeoff_land_test.py` | FINAL / PERSONAL | Behavior retained as a parameterized adapter; team publication consent is confirmed. |
| `mission_control_node.py` | FINAL / PERSONAL | Mission-event behavior retained as a reduced controller. |
| `asp_mission_stack.launch.py` | FINAL / CO-DEVELOPED | Replaced by a minimal launch template; original was an uncommitted integrated launch. |
| `waypoint_mission.py` | FINAL / TEAM | Excluded; documented through command/event boundaries. |
| UGV waypoint modules | TEAM | Excluded; documented through command/event boundaries. |
| `uav_waypoint_mission` | TEAM | Excluded; retained only as a team-scope credit. |
| ArUco tracker / `multi_tracker` | TEAM / UNKNOWN | Excluded; only the `Detection3DArray` interface is described. |
| generic PX4 helper utilities | SUPPORTING / CO-DEVELOPED | Rewritten minimally; no whole utility module copied. |
| `detected_markers.csv` | GENERATED | Excluded. |
| historical divergent copies | OBSOLETE / UNKNOWN | Not merged or copied. |

## Included

- Public-safe mission-state model and tests.
- Parameterized PX4 command-request helpers.
- Marker-gated landing-policy interface.
- ROS 2 mission-controller and takeoff/landing adapters in dry-run-by-default
  form.
- Minimal launch/config templates, architecture documentation, and attribution
  record.

## Excluded

- Generated marker CSV, results, logs, rosbag files, recordings, PX4 logs, and
  temporary runtime files.
- Track coordinates, vehicle frame names, camera calibration, machine paths,
  user-specific runtime configuration, and real mission parameter CSV files.
- UGV waypoint, UAV waypoint, and ArUco detector source.
- PX4, Gazebo, ROS 2, OpenCV, and all other vendor/runtime distributions.

## Upstream / License Review

The current public tree contains no byte-for-byte copy of the upstream
`utilities_pkg` implementation, no UGV/UAV waypoint implementation, and no
ArUco detector implementation. It is a curated rewrite containing only the
takeoff/landing and mission-integration interfaces. PX4, Gazebo, ROS 2, OpenCV
and message packages are dependencies rather than vendored source.

Team publication consent is confirmed. Package metadata is `UNLICENSED` because
this portfolio repository grants no separate open-source reuse license.
Third-party dependency terms remain in force.

## Sanitization

The release scan found no original absolute home paths, private network values,
ROS domain/DDS settings, serial-device paths, camera calibration, track
coordinates, runtime marker CSV, model weights, recordings, or vendor source.
The only email address is the non-routable release-review placeholder in package
metadata.

## Validation

Completed release checks: Python syntax compilation; six pure-Python tests;
package metadata and `colcon build`; launch-description argument generation for
both public launch files; README relative-link checks; and a public-surface scan
for original absolute paths, network values, domain/DDS configuration,
credentials, generated marker data, and large binaries. No original
machine-specific value or excluded runtime artifact is present. Hardware, PX4
SITL, and Gazebo mission runs are not part of this release validation.

## Remaining Issues

1. Review any future vehicle-specific transforms, safety parameters, simulator
   assets, or media separately before adding them.
