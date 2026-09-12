# Cooperative Mission Architecture

## Integration Contract

The public package models a high-level contract between independently developed
subsystems. It retains no source for UGV path following, UAV waypoint planning,
or ArUco detection.

| Producer | Event / output | Consumer | Meaning |
|---|---|---|---|
| UGV waypoint subsystem | `UGV_TRIGGER_REACHED` | Mission Controller | UGV reached the mission trigger location. |
| ArUco detector | `ARUCO_TRIGGER_DETECTED` and `/marker_detections` | Mission Controller / landing adapter | Start condition and marker-pose input. |
| UAV waypoint subsystem | `UAV_EXPLORATION_COMPLETE` | Mission Controller | Exploration portion has completed. |
| UGV waypoint subsystem | `UGV_RENDEZVOUS_REACHED` | Mission Controller | UGV is ready for UAV return. |
| UAV approach logic | `UAV_APPROACH_READY` | Mission Controller | UAV can begin a landing sequence. |
| Landing safety monitor | `UAV_DISARMED` | Mission Controller | Landing/disarm completion has been confirmed. |

## PX4 Command Boundary

The takeoff/landing adapter keeps the following command boundary explicit:

```text
Offboard setpoint → select offboard mode → arm → takeoff altitude condition
→ fresh marker target → NAV_LAND request → independently confirmed disarm
```

`/marker_detections` is a team detector interface. The original code consumed a
matching fresh `Detection3DArray` pose and configurable offset when selecting a
landing target. This does not establish authorship of the detector or prove a
marker-centered visual-servoing controller.

## Deployment Boundary

The curated code has no track coordinates, calibration data, vehicle frame
names, camera configuration, PX4/Gazebo distribution, bags, generated marker
CSV, or hardware logs. A future approved deployment must provide reviewed
transform, safety, and parameter configuration externally.
