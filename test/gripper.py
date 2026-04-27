from ur_arm import robotiq_gripper
import time

# Replace with your UR5's actual IP address
ROBOT_IP = "192.168.0.11"

print("Connecting to gripper...")
# Initialize the gripper and connect to the dedicated Robotiq port
gripper = robotiq_gripper.RobotiqGripper()
gripper.connect(ROBOT_IP, 63352)

# 1. Activation
# The gripper needs to "calibrate" itself every time it boots up.
print("Activating gripper...")
gripper.activate()

# 2. Define our Grip Parameters (0-255 scale)
grip_speed = 255  # Fast
grip_strength = 50  # Gentle grip so we don't crush anything

# 3. Control Position
print("Opening gripper fully...")
# move_and_wait_for_pos pauses the script until the gripper finishes moving
gripper.move_and_wait_for_pos(0, grip_speed, grip_strength)
time.sleep(1)

print("Closing gripper halfway...")
gripper.move_and_wait_for_pos(127, grip_speed, grip_strength)
time.sleep(1)

print("Closing gripper completely...")
gripper.move_and_wait_for_pos(255, grip_speed, grip_strength)

print("Done!")
gripper.disconnect()
