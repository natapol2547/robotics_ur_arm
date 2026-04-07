from ur_arm import Robot, pid
from ur_arm import Camera
import numpy as np
import cv2

ROBOT_IP = "10.10.0.104"
LOWER_LAB = np.array([48, 137, 101])
UPPER_LAB = np.array([204, 180, 183])

def main():
    with Robot(robot_ip=ROBOT_IP, grip_force=50) as robot:
        print("Activating gripper...")
        robot.activate_gripper()

        pid_x = pid.PID(0.0009375, 0.00008, 0.00001)
        pid_y = pid.PID(0.0009375, 0.00008, 0.00001)

        cam = Camera(debug=True)
        cam_width, cam_height = cam.get_cam_res()
        print("Camera resolution: ", (cam_width, cam_height))

        cam_center_x = cam_width / 2
        cam_center_y = cam_height / 2

        offset_mag = 100
        PID_DELAY = 250
        TIME_STEP = 0.4

        while True:
            _, _, z, _, _, _ = robot.get_tcp_pose()

            if z < 0.28:
                break

            print("Current Z height: ", z)
            block = cam.get_block_pos(LOWER_LAB, UPPER_LAB, 5000)

            if block is not None:
                pos_x, pos_y, width, height, angle = block
                print(f"Block position found: x={pos_x}, y={pos_y}, width={width}, height={height}, angle={angle}")

                pid_target_x = cam_center_x  
                pid_target_y = cam_center_y + offset_mag 

                #yes the pos_x and pos_y are swapped, this shit is intentional
                off_x = pid_x.compute(pid_target_y, pos_y, TIME_STEP) 
                off_y = pid_y.compute(pid_target_x, pos_x, TIME_STEP) 

                #high pass filter, threshold to prevent jitter
                if abs(off_x) < 0.001:
                    off_x = 0
                if abs(off_y) < 0.001: 
                    off_y = 0

                robot.move_offset([off_x, off_y, -0.075], blocking=False)

                # PID_MAGNITUDE = np.sqrt(off_x**2 + off_y**2)
                # PID_TIME_SCALING = 5000
                # PID_DELAY = PID_MAGNITUDE * PID_TIME_SCALING

                # print("PID Delay time: ", PID_DELAY, " ms")
                # cv2.waitKey( int(PID_DELAY + 25) ) 

                cv2.waitKey( int(TIME_STEP*1000) )

            else:
                cv2.waitKey(10)  # Wait
                print("No block found.")
        
        robot.move_offset([0, 0, 0], blocking=False)
        robot.close_gripper()
        robot.move_offset([0, 0, 0.2], blocking=True)  # Move up after gripping

if __name__ == "__main__":
    main()