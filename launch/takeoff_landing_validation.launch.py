"""Dry-run launch for validating the ROS interface and landing gate wiring."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription([
        DeclareLaunchArgument("marker_detection_topic", default_value="/marker_detections"),
        Node(
            package="uav_ugv_mission",
            executable="takeoff_landing",
            name="uav_takeoff_landing_validation",
            parameters=[{
                "enable_vehicle_commands": False,
                "marker_detection_topic": LaunchConfiguration("marker_detection_topic"),
            }],
        ),
    ])
