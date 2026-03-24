from ur_arm import Robot

ROBOT_IP = "10.10.0.61"
GRAB_DOWN = -0.135  # metres


def main():
    with Robot(robot_ip=ROBOT_IP, grip_force=50) as robot:
        print("Activating gripper...")
        robot.activate_gripper()

        pose = robot.get_tcp_pose()
        print(f"Current TCP pose: {pose}")
        robot.grab(grab_depth=GRAB_DOWN)


if __name__ == "__main__":
    main()
