from ur_arm import Robot, pid
from ur_arm import Camera
import numpy as np
import cv2

ROBOT_IP = "192.168.0.11"
GRAB_DOWN = -0.135  # metres

TIME_STEP = 0.5

# x: 463, y= -265
# z: 540 -> 305

def main():
    with Robot(robot_ip=ROBOT_IP, grip_force=50) as robot:
        print("Activating gripper...")
        robot.activate_gripper()

        pid_x = pid.PID(0.0002, 0, 0.00001)
        pid_y = pid.PID(0.0002, 0, 0.00001)
        pid_roll = pid.PID(0.002, 0, 0.0001)

        cam = Camera(debug=True)
        cam_width, cam_height = cam.get_cam_res()

        #around 380, 194 is the center of the block in pixel coordinate when it's right in front of the camera
        #cam res is 640 x 480
        cam_center_x = cam_width / 2
        cam_center_y = cam_height / 2

        #gripper offset from cam in pixel
        offset_mag = 75


        while True:
            _, _, _, _, _, r_z = robot.get_tcp_pose()
            block = cam.get_block_pos(np.array([100, 136, 111]), np.array([255, 245, 166]), 1000)

            if block is not None:
                pos_x, pos_y, width, height, angle = block
                print(f"Block position found: x={pos_x}, y={pos_y}, width={width}, height={height}, angle={angle}")

                #adjust the target position for the PID controller based on the block's angle to account for the gripper's offset from the camera
                pid_target_x = cam_center_x + offset_mag * np.cos(r_z - np.pi/2)
                pid_target_y = cam_center_y + offset_mag * np.sin(r_z - np.pi/2)


                off_y = pid_y.compute(pid_target_x, pos_x, TIME_STEP) 
                off_x = pid_x.compute(pid_target_y, pos_y, TIME_STEP)
                off_roll = 0

                off_roll = -1 * pid_roll.compute(0, angle, TIME_STEP)
                print(off_roll)

                if abs(off_x) < 0.01:
                    off_x = 0
                if abs(off_y) < 0.01: 
                    off_y = 0
                if abs(off_roll) < 0.001:
                    off_roll = 0


                print("r_z : ", r_z)
                print(f"Computed offsets: off_x={off_x}, off_y={off_y}, off_roll={off_roll}")

                
                robot.move_offset([off_x, off_y, 0], blocking=False)
                cv2.waitKey(int(TIME_STEP*1000)) 

            else:
                print("No block found.")



if __name__ == "__main__":
    main()