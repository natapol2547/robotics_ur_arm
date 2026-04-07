from ur_arm import Robot
import numpy as np


ROBOT_IP = "10.10.0.50"


INITIALIZING_POS = [0.116, -0.3, 0.2, 0, -np.pi, 0]
STARTING_POS = [0.15, - 0.325, 0.2 , 2.26, 2.26, 0]

MAX_DOWN = -0.1
PIXEL_TO_M = 0.15 / 700

def main():
    with Robot(robot_ip=ROBOT_IP, grip_force=50) as robot:
        print("Activating gripper...")
        robot.activate_gripper()
        robot.grip(0)

        robot.move(INITIALIZING_POS, blocking=True)
        robot.move(STARTING_POS, blocking=True)



        
        dPx = -50 #block cen - cam center in pixel
        dPy = -80 #block cen - cam center in pixel
        block_angle = -10

        x, y, z, r_x, r_y, r_z = robot.get_tcp_pose()

        abs_cam_center = [x + 0.18, y]
        abs_block_center = [abs_cam_center[0] + PIXEL_TO_M * dPy, abs_cam_center[1] + PIXEL_TO_M * dPx]

        ARM_MOVE_TIME = 2 #time for the arm to move to the target position
        CONVEYER_SPEED = 0.02 #conervator speed in m/s

        target_pos = [abs_block_center[0] - ARM_MOVE_TIME * CONVEYER_SPEED , abs_block_center[1], MAX_DOWN, 2.26, 2.26, np.radians(block_angle)]


        print(f"Current TCP pose: {[x, y, z, r_x, r_y, r_z]}")
        print(f"Moving to target position: {target_pos}")
        # robot.move(target_pos, blocking=True)
        # robot.grip(255)


          
    
if __name__ == "__main__":
    main()