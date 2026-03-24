from ur_arm import Robot, pid
from ur_arm import Camera
import time
import numpy as np
import cv2

ROBOT_IP = "192.168.0.11"
GRAB_DOWN = -0.135  # metres

# x: 463, y= -265
# z: 540 -> 305

def main():
    with Robot(robot_ip=ROBOT_IP, grip_force=50) as robot:
        print("Activating gripper...")
        robot.activate_gripper()

        pid_x = pid.PID(0.0002, 0, 0)
        pid_y = pid.PID(0.0002, 0, 0)
        pid_roll = pid.PID(0.0001, 0, 0)

        cam = Camera(debug=True)

        while True:
            block = cam.get_block_pos(np.array([164, 143, 102]), np.array([229, 203, 155]), 1000)
            if block is not None:
                pos_x, pos_y, width, height, angle = block
                print(f"Block position found: x={pos_x}, y={pos_y}, width={width}, height={height}, angle={angle}")
                off_y = pid_y.compute(387, pos_x, 0)
                off_x = pid_x.compute(194, pos_y, 0)
                off_roll = pid_roll.compute(0, angle, 0)

                if abs(off_x) < 0.01:
                    off_x = 0
                if abs(off_y) < 0.01: 
                    off_y = 0
                if abs(off_roll) < 0.001:
                    off_roll = 0

                print(f"Computed offsets: off_x={off_x}, off_y={off_y}, off_roll={off_roll}")

                
                robot.move_offset([off_x, off_y, 0])
                cv2.waitKey(10)  # Small delay to allow for graceful exit with 'q' key

            else:
                print("No block found.")



if __name__ == "__main__":
    main()