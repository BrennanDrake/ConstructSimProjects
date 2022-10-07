#! /usr/bin/env python3
import rospy
from sensor_msgs.msg import LaserScan

def callback(data):
    print("540:{} 360:{} 180:{}".format(data.ranges[540],data.ranges[360],data.ranges[180]))

rospy.init_node("laser_test")
sub = rospy.Subscriber("/scan", LaserScan,  callback)
rospy.spin()