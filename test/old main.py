from ur_arm import Robot
from ur_arm import pid
import cv2 
import numpy as np



ROBOT_IP = "192.168.0.11"
GRAB_DOWN = -0.135  # metres

# x: 463, y= -265
# z: 540 -> 305
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

def main():
    with Robot(robot_ip=ROBOT_IP, grip_force=50) as robot:
        print("Activating gripper...")
        robot.activate_gripper()

        pid_x = pid.PID(kp=0.01, ki=0, kd=0, setpoint=387)
        pid_y = pid.PID(kp=0.01, ki=0, kd=0, setpoint=194)
        pid_roll = pid.PID(kp=0.01, ki=0, kd=0, setpoint=0)

        cam_center_x = cap.get(cv2.CAP_PROP_FRAME_WIDTH) / 2
        cam_center_y = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / 2
        
        #gripper offset from cam in pixel
        offset_mag = 100 

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break

            hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            #pink color range in HSV
            lower_pink = np.array([140, 50, 100])
            upper_pink = np.array([170, 255, 255])

            #mask and drawing contours
            mask = cv2.inRange(hsv_image, lower_pink, upper_pink)
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)

            # Get center and angle of each contour
            for contour in contours:
                # Filter out small contours by area
                area = cv2.contourArea(contour)
                if area < 10000:  # Minimum area threshold to filter noise
                    continue
                
                # Calculate moments to get center
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    # Draw circle at center
                    cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                    
                    # Get angle using ellipse fitting
                    if len(contour) >= 5:
                        try:
                            ellipse = cv2.fitEllipse(contour)
                            angle = ellipse[2]
                            
                            # Validate ellipse dimensions before drawing
                            if ellipse[1][0] > 0 and ellipse[1][1] > 0:
                                cv2.ellipse(frame, ellipse, (255, 0, 0), 2)
                            
                            # Display center and angle
                            cv2.putText(frame, f"Center: ({cx}, {cy})", (cx + 10, cy - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                            cv2.putText(frame, f"Angle: {angle:.1f}°", (cx + 10, cy + 15), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                        except cv2.error:
                            pass  # Skip this contour if ellipse fitting fails

            cv2.imshow('Contours around color', frame)

            # Wait for 1 ms; if the 'q' key is pressed, break the loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

            

        
        

        


if __name__ == "__main__":
    main()
