#! /usr/bin/env python3

import rospy
from real_robo_pkg.srv import FindWall, FindWallResponse
from real_robo_move_class import Real_robo_move

#Service Server for /findwall Service
def callback(FindWallRequest):
    print("The Service /findwall is executing")
    move_robo_object = Real_robo_move()
    move_robo_object.robo_move()
    findwall_object = FindWallResponse()
    findwall_object.wallfound = move_robo_object.final_position()
    print("The Service /findwall is finished")
    return findwall_object
        
rospy.init_node("robo_find_wall_server_node")
find_wall_server = rospy.Service("/findwall", FindWall, callback)
print("The Service /findwall is ready")
rospy.spin()
