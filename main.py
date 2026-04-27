from ur_arm import Robot, pid
from ur_arm import Camera
import numpy as np
import cv2


ROBOT_IP = "10.10.0.14"
LOWER_LAB = np.array([137, 136, 112])
UPPER_LAB = np.array([234, 176, 149])

BOX_GRAB_HEIGHT = 0.166
ADJUSTMENT_HEIGHT_THRESHOLD = BOX_GRAB_HEIGHT + 0.05
ADJUSTMENT_CENTER_THRESHOLD = 80
PID_GAIN = 1

def main():
    with Robot(robot_ip=ROBOT_IP, grip_force=50, move_speed=0.8) as robot:

        print("Activating gripper...")
        robot.activate_gripper()
        
        robot.move([0.116, -0.3, 0.2, 0, -3.143, 0], blocking=True)  #initial position according to project spec
        cv2.waitKey(500)  
        input("Press Enter to start the box grabbing process...")  # Wait for user input before starting
        robot.move([0.162, -0.318, 0.243, 2.276, 2.172, 0], blocking=True)  #move above conveyor belt

        SAMPLING_RATE = 0.01
        pid_x = pid.PID(0.0003, 0.0, 0.0)
        pid_y = pid.PID(0.0003, 0.0, 0.0)

        cam = Camera(debug=True)
        cam_width, cam_height = cam.get_cam_res()
        print("Camera resolution: ", (cam_width, cam_height))
        cv2.waitKey(500)


        ########################## PID CONTROL LOOP ##########################        
        while True:
            while True:
                _, _, z, _, _, _ = robot.get_tcp_pose()
                print(f"Current Z position: {z:.4f} m")
                if z < BOX_GRAB_HEIGHT:
                    break
    
                block = cam.get_block_pos(LOWER_LAB, UPPER_LAB, 5000)

                if block is not None:
                    pos_x, pos_y, _, _, _= block

                    cam_center_x = cam_width / 2
                    cam_center_y = cam_height / 2
                    offset_mag = 90
                    
                    target_x = cam_center_x  
                    target_y = cam_center_y + offset_mag 

                    #The pos_x and pos_y are swapped due to camera orientation
                    x_pid_output = pid_x.compute(target_y, pos_y)
                    y_pid_output = pid_y.compute(target_x, pos_x)

                    x_output = x_pid_output * PID_GAIN
                    y_output = y_pid_output * PID_GAIN
                          
                    #high pass filter, threshold to prevent jitter
                    if abs(x_output) < 0.001:
                        x_output = 0
                    if abs(y_output) < 0.001: 
                        y_output = 0

                    z_speed = 0
                    if z > ADJUSTMENT_HEIGHT_THRESHOLD:
                        z_speed = -0.08  # Move down if above threshold
                    elif abs(pos_x - target_x) < ADJUSTMENT_CENTER_THRESHOLD and abs(pos_y - target_y) < ADJUSTMENT_CENTER_THRESHOLD:
                        z_speed = -0.08  # Move down if centered


                    # Limit and Set Speed
                    speed = [max(-0.15, min(0.15, v)) for v in speed]
                    speed = [x_output, y_output, z_speed]
                    robot.set_speed(speed)

                    cv2.waitKey(int(SAMPLING_RATE*1000)) 

                else:
                    # Stop movement if no block is found
                    robot.set_speed([0, 0, 0])  
                    cv2.waitKey(10)
            
            # Stop the robot and close the gripper to grab the box
            robot.rtde_c.speedStop()
            robot.close_gripper()
            
            # Move up after gripping and open the gripper to release the box
            robot.move_offset([0, 0, 0.1], blocking=True)  
            cv2.waitKey(1000)
            robot.open_gripper()

            #move above conveyor belt to look for next box
            robot.move([0.162, -0.318, 0.243, 2.276, 2.172, 0], blocking=True)  
        
        
        
if __name__ == "__main__":
    main()