from setuptools import find_packages, setup


package_name = "uav_ugv_mission"


setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", [
            "launch/cooperative_mission.launch.py",
            "launch/takeoff_landing_validation.launch.py",
        ]),
        ("share/" + package_name + "/config", ["config/mission_example.yaml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Public release staging",
    maintainer_email="release-review-required@example.invalid",
    description="Public-safe UAV–UGV mission-integration staging package.",
    license="LicenseRef-Pending-Review",
    entry_points={
        "console_scripts": [
            "mission_controller = uav_ugv_mission.mission_controller:main",
            "takeoff_landing = uav_ugv_mission.takeoff_landing:main",
        ],
    },
)
