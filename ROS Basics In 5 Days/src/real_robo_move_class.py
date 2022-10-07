#! /usr/bin/env python

import threading
import time
from geometry_msgs.msg import Twist
import rospy
from sensor_msgs.msg import LaserScan

class Real_robo_move():
    def __init__(self):
        self.real_robo_publisher = rospy.Publisher("/cmd_vel", Twist, queue_size=1)
        self.cmd = Twist()
        self.ctrl_c = False
        self.rate = rospy.Rate(1)
        self.wall_found = False

    #Laser Data Callback
    def callback(self, data):
        self.laser_data = data.ranges
        self.laser_min = min(self.laser_data)
        #print("F: {} Min:{}".format(self.laser_data[360],self.laser_min))

    #Function Container to hold Subscriber to Laser Data
    def laser(self):
        rospy.Subscriber("/scan", LaserScan, self.callback)
    
    #Function initializes threads running laser_data watchdog and findwall function
    def robo_move(self):
        self.t1 = threading.Thread(target=self.laser)
        self.t2 = threading.Thread(target=self.find_wall)
        self.t1.start()
        time.sleep(2)
        self.t2.start()
        while not self.wall_found:
            pass
        return
    
    #Function rotates counterclockwise until it finds wall (or closest object) then moves forward until
    #0.3 meters from the object
    def find_wall(self):
        rospy.loginfo("Entering find_wall")
        while ((self.laser_min + 0.02) <= self.laser_data[360] or (self.laser_min - 0.02) >= self.laser_data[360]):
            self.cmd.angular.z = 0.2
            self.cmd.linear.x = 0
            self.real_robo_publisher.publish(self.cmd)
            rospy.loginfo("1")
        while self.laser_data[360] >= 0.3:
            self.cmd.angular.z = 0
            self.cmd.linear.x = .1
            self.real_robo_publisher.publish(self.cmd)
            rospy.loginfo("2")
        self.cmd.linear.x = 0
        self.cmd.angular.z = 0
        self.real_robo_publisher.publish(self.cmd)
        rospy.loginfo("3")
        rospy.loginfo("Exiting find_wall")
        time.sleep(2)
        self.wall_found = True
        return

    #Function rotates counterclockwise until wall is on right side
    def final_position(self):
        rospy.loginfo("Entering final position")
        while not (self.laser_min + 0.02) >= self.laser_data[180] and (self.laser_min - 0.02) <= self.laser_data[180]: 
            self.cmd.angular.z = 0.2
            self.real_robo_publisher.publish(self.cmd)
            rospy.loginfo("4")
        self.cmd.angular.z = 0
        self.real_robo_publisher.publish(self.cmd)
        rospy.loginfo("5")
        time.sleep(2)
        rospy.loginfo("Exiting final position")
        return(True)

