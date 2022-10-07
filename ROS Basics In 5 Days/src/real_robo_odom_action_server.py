#! /usr/bin/env python3

import time
import math
import threading
import rospy
import actionlib
from real_robo_pkg.msg import OdomRecordFeedback, OdomRecordResult, OdomRecordAction
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point32


class OdomActionServerClass(object):
    _feedback = OdomRecordFeedback()
    _result = OdomRecordResult()

    #Upon class object being created, threads initialized to start the action server
    #and to /odom topic watchdog of the turtlebot
    def __init__(self):
        self.oldodomx = 0
        self.oldodomy = 0
        self.oldodomz = 0
        self.odom = Odometry()
        self.odomdata = Point32
        self.t2 = threading.Thread(target=self.record_odom)
        time.sleep(1)
        self.t1 = threading.Thread(target=self.start)
        self.t1.start()
        self.t2.start()
        self.success = False

        #initializing feedback and result data objects to later publish
        self._feedback.current_total = 0
        self._result.list_of_odoms = []

    #Function to start action server
    def start(self):
        self._as = actionlib.SimpleActionServer("/record_odom", OdomRecordAction, self.goal_callback,False)
        self._as.start()
        rospy.loginfo("/record_odom action server is ready")

    #Function called when /record_odom action server is called
    def goal_callback(self, goal):
        #helper variables
        r = rospy.Rate(1)

        #initializing feedback and result data objects to later publish
        self._feedback.current_total = 0
        self._result.list_of_odoms = []

        #Alerting User to Execution
        rospy.loginfo("/record_odom action server executing")
        while True:
            if self._as.is_preempt_requested():
                rospy.loginfo('The goal has been cancelled/preempted')
                # the following line, sets the client in preempted state (goal cancelled)
                self._as.set_preempted()
                self.success = False
                break

            distx = abs(self.odomdata.x - self.oldodomx)
            disty = abs(self.odomdata.y - self.oldodomy)
            
            self._feedback.current_total += (math.sqrt(distx**2+disty**2)) 
            self._as.publish_feedback(self._feedback)
            self._result.list_of_odoms.append(self.odomdata)

            #Debug log to show pose
            #rospy.loginfo("x:{} y:{}".format(self.odomdata.x, self.odomdata.y))
            
            if self._feedback.current_total > 5 and self.odomdata.x < 0.4 and self.odomdata.y < 0.7 and self.odomdata.x > 0 and self.odomdata.y > 0.4:
                break
            self.oldodomx = self.odomdata.x
            self.oldodomy = self.odomdata.y
            self.oldodomz = self.odomdata.z
            r.sleep()
        print("Finished")
        self._as.set_succeeded(self._result)
        
    #Function called by /odom subscriber constantly updating odomdata.x,y,and zs
    def sub_callback(self, data):
        self.odomdata.x = data.pose.pose.position.x
        self.odomdata.y = data.pose.pose.position.y
        self.odomdata.z = data.pose.pose.orientation.z


    def record_odom(self):
        odom_sub = rospy.Subscriber("/odom", Odometry, self.sub_callback, queue_size=1)


if __name__ == "__main__":
    rospy.init_node("real_robo_odom_action_server")
    OdomActionServerClass()
    rospy.spin()