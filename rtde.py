import rtde_control
import rtde_receive

# Replace with your UR5's actual IP address
ROBOT_IP = "192.168.0.11"

# 1. Connect to the Robot
# 'Receive' gets data from the robot; 'Control' sends commands to it
print("Connecting...")
rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)

# 2. Get the current TCP pose
# This returns a clean list of 6 floats: [x, y, z, rx, ry, rz]
# Note: Position is in meters [m], and rotation is in radians [rad]
current_pose = rtde_r.getActualTCPPose()
print(f"Current Pose: {current_pose}")

# 3. Move Linearly (moveL)
# Let's create a target by copying the current pose and moving up 10cm (0.1m) in the Z-axis
target_pose = current_pose.copy()
target_pose[2] -= 0.10

# Define speed (m/s) and acceleration (m/s^2)
speed = 0.5
acceleration = 0.3

# Execute the moveL command.
# By default, this is a "blocking" command, meaning Python will wait here until the move is finished.
print("Moving...")
rtde_c.moveL(target_pose, speed, acceleration)
print("Movement complete!")

# 4. Cleanly disconnect
rtde_c.disconnect()
rtde_r.disconnect()
