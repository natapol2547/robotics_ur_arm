import time

from ur_arm import Robot

TCP = "192.168.0.104"
TCP_PORT = 2025

ROBOT = "192.168.0.11"
MOVE_PORT = 30003
GRIP_PORT = 63352

POSE_CALIBRATION = (0.00596, 0.08338)  # (x_offset, y_offset) in metres
GRAB_DOWN = -0.135                      # metres


def main():
    with Robot(
        pose_host=TCP,
        pose_port=TCP_PORT,
        move_host=ROBOT,
        move_port=MOVE_PORT,
        grip_host=ROBOT,
        grip_port=GRIP_PORT,
        pose_calibration=POSE_CALIBRATION,
    ) as robot:
        active = robot.activate_gripper(force=1)
        print("Gripper activated" if active else "Gripper was not active, now initialised")

        grabbed = False
        while not grabbed:
            coord = robot.get_pose()
            if coord is None:
                continue

            x, y = coord[0], coord[1]
            print(f"Target offset: x={x:.4f}  y={y:.4f}")

            robot.move([-y, -x, 0])
            time.sleep(0.1)

            distance = (x**2 + y**2) ** 0.5
            if distance < 0.005:
                robot.grab(grab_depth=GRAB_DOWN, settle_time=3.0)
                grabbed = True


if __name__ == "__main__":
    main()
