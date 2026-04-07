from ur_arm import Robot, pid
from ur_arm import Camera
import numpy as np
import cv2
import time

ROBOT_IP = "10.10.0.104"
LOWER_LAB = np.array([48, 137, 101])
UPPER_LAB = np.array([204, 180, 183])

def main():
    with Robot(robot_ip=ROBOT_IP, grip_force=50) as robot:

        while True:
            _, _, z, _, _, _ = robot.get_tcp_pose()

            if z < 0.28:
                break

            # Define velocity vector: [vx, vy, vz, vrx, vry, vrz] in m/s and rad/s
            # Example: Move straight up along the Z-axis at 5 cm/s
            velocity = [0.0, 0.0, 0.03, 0.0, 0.0, 0.0] 

            print("Starting velocity motion...")
            # Send the velocity command. The Python script continues immediately.
            robot.set_speed(velocity)

            # Your script is free to do other things here
            # For example, reading sensors, computing new velocities, etc.
            time.sleep(2.0) 

        print("Stopping robot...")
        # Safely decelerate and stop the velocity command
        robot.rtde_c.speedStop()
        robot.rtde_c.stopScript()

main()