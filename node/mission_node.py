#!/usr/bin/env python
import rospy, math
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import Altitude, ExtendedState, HomePosition, State, WaypointList, CommandCode, Waypoint
from mavros_msgs.srv import CommandBool, ParamGet, SetMode, WaypointClear, WaypointPush
from sensor_msgs.msg import NavSatFix, Imu
from base_node import BaseNode
from path_utils import local_to_global, build_waypoints


class MissionNode(BaseNode):
    def __init__(self, *args, **kwargs):
        super(MissionNode, self).__init__(*args, **kwargs)
        self.waypoints = []

    def setup(self):
        super(MissionNode, self).setup()
        self.clear_wps()

    def load_local_path(self, path):
        # Visualize the path in Rviz
        self.visualize_local_path(path)

        # Convert the path to global GPS coordinates
        path_global = local_to_global(path)
        rospy.loginfo(path_global)

        # Send the path as a mission to MAVROS
        self.load_waypoints(path_global)

    """
    load_waypoints()
    Convert a list of 3D points to a list of MAVLink waypoint.
    Store the mission in self.mission

    @param points: [[lat, lon, alt]] 3D points in the global coordinate system
    """
    def load_waypoints(self, path):
        waypoints = build_waypoints(path)
        self.waypoints = waypoints

    """
    visualize_local_path()
    Publish a local path to a ROS topic, in order to be visualize by the Rviz visualizer.
    @param path: [[x, y, z]] 3D path in local coordinates.
    """
    def visualize_local_path(self, path):
        rospy.loginfo(path)

    def exec_mission(self):
        self.clear_wps()
        self.send_wps(self.waypoints)

        self.set_mode('AUTO.MISSION')
        self.set_arm(True)

        while not rospy.is_shutdown():
            self.rate.sleep()
