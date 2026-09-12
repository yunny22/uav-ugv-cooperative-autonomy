"""Launch the public mission-control and takeoff/landing integration adapters."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        DeclareLaunchArgument("marker_detection_topic", default_value="/marker_detections"),
        DeclareLaunchArgument("enable_vehicle_commands", default_value="false"),
        Node(
            package="uav_ugv_mission",
            executable="mission_controller",
            name="cooperative_mission_controller",
            parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")}],
        ),
        Node(
            package="uav_ugv_mission",
            executable="takeoff_landing",
            name="uav_takeoff_landing",
            parameters=[{
                "use_sim_time": LaunchConfiguration("use_sim_time"),
                "marker_detection_topic": LaunchConfiguration("marker_detection_topic"),
                "enable_vehicle_commands": LaunchConfiguration("enable_vehicle_commands"),
            }],
        ),
    ])
