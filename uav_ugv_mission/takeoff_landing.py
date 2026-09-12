"""Public-safe PX4 takeoff/landing integration adapter.

This is a reduced, parameterized extraction of the personal takeoff/landing
flow: offboard setpoints precede arming; takeoff completion is reported to the
mission controller; a fresh external ArUco result can gate the request for a
landing command; landing is followed by disarm confirmation. It contains no
track coordinates, camera calibration, vehicle model, or detector algorithm.

The node starts in dry-run mode. Setting ``enable_vehicle_commands`` to true
is deliberately left to a reviewed, vehicle-specific deployment configuration.
"""

from __future__ import annotations

from typing import Optional

from rclpy.node import Node
from std_msgs.msg import String

try:
    from geometry_msgs.msg import PoseStamped
    from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand, VehicleLocalPosition
    from vision_msgs.msg import Detection3DArray
    ROS_FLIGHT_INTERFACES_AVAILABLE = True
    ROS_FLIGHT_INTERFACES_ERROR = None
except ModuleNotFoundError as error:
    # Keep the package importable for documentation and pure-logic tests when
    # PX4/vision interfaces are not installed in the active ROS environment.
    PoseStamped = OffboardControlMode = TrajectorySetpoint = VehicleCommand = VehicleLocalPosition = Detection3DArray = None
    ROS_FLIGHT_INTERFACES_AVAILABLE = False
    ROS_FLIGHT_INTERFACES_ERROR = error

from .landing_policy import LandingTarget, choose_landing_target
from .px4_control import arm_request, disarm_request, nav_land_request, offboard_mode_request


class TakeoffLandingNode(Node):
    """Expose the verified takeoff/landing sequence without a detector implementation."""

    def __init__(self) -> None:
        if not ROS_FLIGHT_INTERFACES_AVAILABLE:
            raise RuntimeError(
                "uav_takeoff_landing requires geometry_msgs, px4_msgs, and vision_msgs. "
                "Install/source those ROS 2 interfaces before running the node."
            ) from ROS_FLIGHT_INTERFACES_ERROR
        super().__init__("uav_takeoff_landing")
        self.declare_parameter("enable_vehicle_commands", False)
        self.declare_parameter("marker_detection_topic", "/marker_detections")
        self.declare_parameter("landing_target_topic", "/uav/landing_target")
        self.declare_parameter("event_topic", "/cooperative_mission/events")
        self.declare_parameter("landing_marker_id", 0)
        self.declare_parameter("marker_timeout_seconds", 2.0)
        self.declare_parameter("allow_coordinate_fallback", False)
        self.declare_parameter("takeoff_local_ned_z", -5.0)
        self.declare_parameter("takeoff_tolerance", 0.7)
        self.declare_parameter("handshake_setpoint_count", 10)

        self._enable_vehicle_commands = bool(self.get_parameter("enable_vehicle_commands").value)
        self._landing_marker_id = int(self.get_parameter("landing_marker_id").value)
        self._marker_timeout_seconds = float(self.get_parameter("marker_timeout_seconds").value)
        self._takeoff_tolerance = float(self.get_parameter("takeoff_tolerance").value)
        self._last_marker: Optional[LandingTarget] = None
        self._last_marker_time_ns: Optional[int] = None
        self._phase = "idle"

        self._event_publisher = self.create_publisher(String, self.get_parameter("event_topic").value, 10)
        self._landing_target_publisher = self.create_publisher(
            PoseStamped, self.get_parameter("landing_target_topic").value, 10
        )
        self._offboard_publisher = self.create_publisher(
            OffboardControlMode, "/fmu/in/offboard_control_mode", 10
        )
        self._setpoint_publisher = self.create_publisher(
            TrajectorySetpoint, "/fmu/in/trajectory_setpoint", 10
        )
        self._vehicle_command_publisher = self.create_publisher(
            VehicleCommand, "/fmu/in/vehicle_command", 10
        )
        self.create_subscription(
            Detection3DArray,
            self.get_parameter("marker_detection_topic").value,
            self._on_marker_detections,
            10,
        )
        self.create_subscription(VehicleLocalPosition, "/fmu/out/vehicle_local_position", self._on_local_position, 10)
        self.create_subscription(String, "/uav/mission_command", self._on_command, 10)

    def _on_command(self, message: String) -> None:
        if message.data == "UAV_TAKEOFF":
            self._phase = "takeoff"
            self._publish_offboard_position_mode()
            self._publish_takeoff_setpoint()
            self._send_request(offboard_mode_request())
            self._send_request(arm_request())
        elif message.data == "UAV_BEGIN_LANDING_SEQUENCE":
            self._phase = "landing"
            target = choose_landing_target(
                self._last_marker,
                self._marker_is_fresh(),
                fallback_target=None,
                allow_coordinate_fallback=bool(self.get_parameter("allow_coordinate_fallback").value),
            )
            if target is None:
                self.get_logger().warning("Landing remains gated: no fresh marker target")
                return
            self._publish_landing_target(target)
            self._send_request(nav_land_request())
            self._emit("UAV_LANDING_COMMAND_SENT")
        elif message.data == "UAV_DISARM":
            self._send_request(disarm_request())
            self._emit("UAV_DISARMED")

    def _on_marker_detections(self, detections: Detection3DArray) -> None:
        """Accept the team detector's selected marker pose without implementing detection."""

        for detection in detections.detections:
            for result in detection.results:
                if str(result.hypothesis.class_id) != str(self._landing_marker_id):
                    continue
                pose = result.pose.pose
                self._last_marker = LandingTarget(
                    source="teammate_aruco_detection",
                    position=(pose.position.x, pose.position.y, pose.position.z),
                )
                self._last_marker_time_ns = self.get_clock().now().nanoseconds
                return

    def _on_local_position(self, position: VehicleLocalPosition) -> None:
        """Report takeoff only after the vehicle reaches the configured altitude band."""

        if self._phase != "takeoff":
            return
        target_z = float(self.get_parameter("takeoff_local_ned_z").value)
        if position.z <= target_z + self._takeoff_tolerance:
            self._phase = "hovering"
            self._emit("UAV_TAKEOFF_COMPLETE")

    def _marker_is_fresh(self) -> bool:
        if self._last_marker_time_ns is None:
            return False
        age_seconds = (self.get_clock().now().nanoseconds - self._last_marker_time_ns) / 1e9
        return age_seconds <= self._marker_timeout_seconds

    def _publish_offboard_position_mode(self) -> None:
        if not self._enable_vehicle_commands:
            return
        message = OffboardControlMode()
        message.position = True
        message.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self._offboard_publisher.publish(message)

    def _publish_takeoff_setpoint(self) -> None:
        if not self._enable_vehicle_commands:
            return
        message = TrajectorySetpoint()
        message.position = [float("nan"), float("nan"), float(self.get_parameter("takeoff_local_ned_z").value)]
        message.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self._setpoint_publisher.publish(message)

    def _publish_landing_target(self, target: LandingTarget) -> None:
        message = PoseStamped()
        message.header.stamp = self.get_clock().now().to_msg()
        message.header.frame_id = "map"
        message.pose.position.x, message.pose.position.y, message.pose.position.z = target.position
        self._landing_target_publisher.publish(message)

    def _send_request(self, request) -> None:
        if not self._enable_vehicle_commands:
            self.get_logger().info("Dry run: PX4 command %s" % request.command)
            return
        message = VehicleCommand()
        message.command = request.command
        (
            message.param1,
            message.param2,
            message.param3,
            message.param4,
            message.param5,
            message.param6,
            message.param7,
        ) = request.params
        message.target_system = 1
        message.target_component = 1
        message.from_external = True
        message.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self._vehicle_command_publisher.publish(message)

    def _emit(self, event: str) -> None:
        self._event_publisher.publish(String(data=event))


def main() -> None:
    import rclpy

    rclpy.init()
    node = TakeoffLandingNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
