#! /usr/bin/env python3

import threading
import time
import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from real_robo_pkg.srv import FindWall, FindWallRequest
from real_robo_pkg.msg import OdomRecordAction, OdomRecordGoal
#OdomRecordResult, OdomRecordFeedback
import actionlib

class Real_Robo_Control():
    def __init__(self):
        self.cmd = Twist()
        self.x = 0
        self.data = LaserScan()
        self.pub = rospy.Publisher("/cmd_vel", Twist, queue_size=1)
        rospy.on_shutdown(self.shutdownhook)
        self.rate = rospy.Rate(1)

    def shutdownhook(self):
        # works better than the rospy.is_shutdown()
        t1.join()
        t2.join()
        t3.join()
        exit = rospy.Publisher("/cmd_vel", Twist, queue_size=1)
        self.cmd.angular.z = 0
        self.cmd.linear.x = 0
        exit.publish(self.cmd)
        rospy.loginfo("closed")
        self.ctrl_c = True

    #Function called by /scan subscriber
    def callback(self, data):
        self.data = data.ranges
        self.data_min = self.data.index(min(self.data))
        rospy.loginfo_once("laser data being published")

    #Control Function for wall following behavior
    def ctrl_logic(self):
        rospy.loginfo("Entered ctrl_logic")
        while True:
            #if self.data[360] > 0.5 and self.data_min < 170:
               # self.cmd.angular.z = -0.2
              #  self.cmd.linear.x = 0.1
             #   rospy.loginfo("R Turn")
             #   self.pub.publish(self.cmd)
           # elif self.data[360] > 0.5 and self.data_min > 190:
           #     self.cmd.angular.z = 0.2
           #     self.cmd.linear.x = 0.1
           #     rospy.loginfo("L Turn")
           #     self.pub.publish(self.cmd)
            if self.data[360] > 0.5 and self.data[180] < 0.3 and self.data[180] > 0.2:
                self.cmd.angular.z = 0.0
                self.cmd.linear.x = 0.1
                #rospy.loginfo("F")
                self.pub.publish(self.cmd)
                rospy.loginfo("2.1")
            elif self.data[360] > 0.5 and self.data[180] > 0.275:
                self.cmd.angular.z = -0.125
                self.cmd.linear.x = 0.1
                #rospy.loginfo("R")
                self.pub.publish(self.cmd)
                rospy.loginfo("2.2")
            elif self.data[360] > 0.5 and self.data[180] < 0.225:
                self.cmd.angular.z = 0.125
                self.cmd.linear.x = 0.1
                #rospy.loginfo("L")
                self.pub.publish(self.cmd)
                rospy.loginfo("2.3")
            elif self.data[360] < .5:
                self.cmd.angular.z = .4
                self.cmd.linear.x = 0.05
                #print("Corner")
                self.pub.publish(self.cmd)
                rospy.loginfo("2.4")

    #Function calls /findwall service and then starts the publisher for movement commands the subscriber for laser data
    #and starts threads that simultaneously call the odometry recording action and the follow following behavior
    def control(self):
        rospy.wait_for_service("/findwall")
        findwall_service = rospy.ServiceProxy("/findwall", FindWall)
        findwall_object = FindWallRequest()
        result = findwall_service(findwall_object)
        if result.wallfound or self.x == 1:
            self.x += 1
            rospy.loginfo(result)
            t1.start()
            self.sub = rospy.Subscriber("/scan", LaserScan,  self.callback)
            time.sleep(2)
            t3.start()
        #rospy.spin()
        
        
    #Feedback from odometry recording (Total Distance Traveled)
    def feedback_callback(self,feedback):
        self.total_odom = feedback
        rospy.loginfo(self.total_odom)

    #Action Client Function
    def odom(self):
        #Helper Variables
        #PENDING = 0
        #ACTIVE = 1
        DONE = 2
        #WARN = 3
        #ERROR = 4
        
        client = actionlib.SimpleActionClient("/record_odom", OdomRecordAction)
        client.wait_for_server()

        goal = OdomRecordGoal()
        client.send_goal(goal, feedback_cb= self.feedback_callback)
        state_result = client.get_state()

        while state_result < DONE:
            rate.sleep()
            state_result = client.get_state()
        rospy.loginfo("/record_odom finished")

if __name__ == "__main__":
    rospy.init_node("robo_control_node")
    rate = rospy.Rate(1)
    real_robo_obj = Real_Robo_Control()
    t1 = threading.Thread(target=real_robo_obj.odom)
    t2 = threading.Thread(target=real_robo_obj.control)
    t3 = threading.Thread(target=real_robo_obj.ctrl_logic)
    t2.start()




