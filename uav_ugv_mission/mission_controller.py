"""ROS 2 adapter for the team-level UAV–UGV mission sequence.

It does not contain UGV waypoint tracking, UAV waypoint generation, or ArUco
detection. Those subsystems publish events and consume commands through the
topics configured by the launch file.
"""

from __future__ import annotations

from rclpy.node import Node
from std_msgs.msg import String

from .mission_flow import MissionEvent, MissionState, advance


class MissionController(Node):
    """Translate subsystem events into high-level mission commands."""

    def __init__(self) -> None:
        super().__init__("cooperative_mission_controller")
        self.declare_parameter("event_topic", "/cooperative_mission/events")
        self.declare_parameter("uav_command_topic", "/uav/mission_command")
        self.declare_parameter("ugv_command_topic", "/ugv/mission_command")
        self.declare_parameter("aruco_command_topic", "/aruco/mission_command")
        self.state = MissionState.IDLE

        self._uav_commands = self.create_publisher(String, self.get_parameter("uav_command_topic").value, 10)
        self._ugv_commands = self.create_publisher(String, self.get_parameter("ugv_command_topic").value, 10)
        self._aruco_commands = self.create_publisher(String, self.get_parameter("aruco_command_topic").value, 10)
        self.create_subscription(String, self.get_parameter("event_topic").value, self._on_event, 10)

    def _on_event(self, message: String) -> None:
        try:
            event = MissionEvent(message.data)
        except ValueError:
            self.get_logger().warning("Ignoring unknown mission event: %s" % message.data)
            return

        transition = advance(self.state, event)
        if transition.state is self.state and not transition.commands:
            self.get_logger().debug("Ignored %s in %s" % (event.value, self.state.value))
            return
        self.state = transition.state
        for command in transition.commands:
            self._publish_command(command)
        self.get_logger().info("Mission state: %s" % self.state.value)

    def _publish_command(self, command: str) -> None:
        message = String(data=command)
        if command.startswith("UAV_"):
            self._uav_commands.publish(message)
        elif command.startswith("UGV_"):
            self._ugv_commands.publish(message)
        else:
            self._aruco_commands.publish(message)


def main() -> None:
    import rclpy

    rclpy.init()
    node = MissionController()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
