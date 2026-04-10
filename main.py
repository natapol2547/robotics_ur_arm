from ur_arm import Robot, pid
from ur_arm import Camera
from ur_arm import llc
import numpy as np
import cv2


ROBOT_IP = "10.10.0.104"
LOWER_LAB = np.array([137, 136, 112])
UPPER_LAB = np.array([234, 176, 149])



def main():
    with Robot(robot_ip=ROBOT_IP, grip_force=50) as robot:

        print("Activating gripper...")
        robot.activate_gripper()
        
        robot.move([0.116, -0.3, 0.2, 0, -3.143, 0], blocking=True)  #initial position according to project spec
        cv2.waitKey(2000)  
        robot.move([0.3, -0.32, -0.085, 2.25, 2.25, 0], blocking=True)  #move above conveyor belt

        TIME_STEP = 0.001
        pid_x = pid.PID(0.001, 0.001/420, 0)
        pid_y = pid.PID(0.001, 0.0, 0.0)
        llc_x = llc.leadlagcompensator(K=0.00001, T1=0.001, T2=0.002, Ts=TIME_STEP)
        llc_y = llc.leadlagcompensator(K=0.00001, T1=0.001, T2=0.002, Ts=TIME_STEP)

        cam = Camera(debug=True)
        cam_width, cam_height = cam.get_cam_res()
        print("Camera resolution: ", (cam_width, cam_height))
        cv2.waitKey(2000)

        box_grab_count = 0


        ########################## PID + LEAD LAG COMPENSATOR CONTROL LOOP ##########################        
        while True:
            while True:
                _, _, z, _, _, _ = robot.get_tcp_pose()
                if z < 0.27:
                    break
    
                block = cam.get_block_pos(LOWER_LAB, UPPER_LAB, 5000)

                if block is not None:
                    pos_x, pos_y, width, height, angle = block
                    # print(f"Block position found: x={pos_x}, y={pos_y}, width={width}, height={height}, angle={angle}")

                    cam_center_x = cam_width / 2
                    cam_center_y = cam_height / 2
                    offset_mag = 90
                    
                    target_x = cam_center_x  
                    target_y = cam_center_y + offset_mag 

                    #yes the pos_x and pos_y are swapped, this shit is intentional
                    x_pid_output = pid_x.compute(target_y, pos_y)
                    y_pid_output = pid_y.compute(target_x, pos_x)

                    x_llc_output = llc_x.compute(target_y - pos_y)
                    y_llc_output = llc_y.compute(target_x - pos_x)

                    x_llc_output = min(0.05, max(-0.05, x_llc_output))
                    y_llc_output = min(0.05, max(-0.05, y_llc_output))

                    x_output = x_pid_output + x_llc_output
                    y_output = y_pid_output + y_llc_output
                    print(f"PID + Lead Compensator Output: x={x_output}, y={y_output}")                    

                    #high pass filter, threshold to prevent jitter
                    if abs(x_output) < 0.001:
                        x_output = 0
                    if abs(y_output) < 0.001: 
                        y_output = 0

                    # Limit speed
                    speed = [x_output, y_output, -0.05]
                    speed = [max(-0.15, min(0.15, v)) for v in speed]
                    # Test speed
                    robot.set_speed(speed)

                    cv2.waitKey(int(TIME_STEP*1000))  # Wait

                else:
                    robot.set_speed([0, 0, 0])  # Stop movement if no block is found
                    llc_x.reset()
                    llc_y.reset()
                    cv2.waitKey(10)
            
            robot.rtde_c.speedStop()
            robot.close_gripper()

            box_grab_count += 1
            print(f"Box grabbed! Total count: {box_grab_count}")
            
            robot.move_offset([0, 0, 0.3], blocking=True)  # Move up after gripping
            cv2.waitKey(3000)
            robot.open_gripper()
            
            cv2.waitKey(2500)
            

            BOX_GRAB_LIMIT = 2
            if box_grab_count >= BOX_GRAB_LIMIT:
                print(f"Grabbed {BOX_GRAB_LIMIT} boxes, ending program.")
                break
        
        
        
if __name__ == "__main__":
    main()