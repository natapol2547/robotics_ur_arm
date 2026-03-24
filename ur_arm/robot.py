import rtde_control
import rtde_receive

from .robotiq_gripper import RobotiqGripper


class Robot:
    def __init__(
        self,
        robot_ip: str,
        grip_port: int = 63352,
        move_speed: float = 0.5,
        move_accel: float = 0.3,
        grip_speed: int = 255,
        grip_force: int = 50,
    ):
        self.move_speed = move_speed
        self.move_accel = move_accel
        self.grip_speed = grip_speed
        self.grip_force = grip_force

        self.rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        self.rtde_c = rtde_control.RTDEControlInterface(robot_ip)

        self.gripper = RobotiqGripper()
        self.gripper.connect(robot_ip, grip_port)

    # ------------------------------------------------------------------
    # Robot arm — RTDE
    # ------------------------------------------------------------------

    def get_tcp_pose(self) -> list[float]:
        """Return the current TCP pose ``[x, y, z, rx, ry, rz]`` via RTDE."""
        return self.rtde_r.getActualTCPPose()

    def move(self, pose: list[float], blocking: bool = True) -> None:
        """Move to an absolute TCP pose ``[x, y, z, rx, ry, rz]`` using moveL.

        Set ``blocking=False`` for continuous tracking loops where the next
        command should interrupt the current one.
        """
        padded = list(pose) + [0.0] * (6 - len(pose))
        self.rtde_c.moveL(padded[:6], self.move_speed, self.move_accel)

    def move_offset(self, offset: list[float], blocking: bool = True) -> None:
        """Move by a Cartesian offset relative to the current TCP pose.

        ``offset`` is ``[dx, dy, dz]`` (or up to 6 elements); missing
        elements default to 0.  Rotation components of the current pose
        are preserved.
        """
        current = self.rtde_r.getActualTCPPose()
        target = [c + (offset[i] if i < len(offset) else 0.0) for i, c in enumerate(current)]
        self.rtde_c.moveL(target, self.move_speed, self.move_accel)

    # ------------------------------------------------------------------
    # Gripper — RobotiqGripper
    # ------------------------------------------------------------------

    def activate_gripper(self) -> None:
        """Activate and auto-calibrate the gripper (blocks until ready)."""
        self.gripper.activate()

    def grip(self, pos: int) -> None:
        """Move gripper to ``pos`` (0 = open, 255 = closed) and wait."""
        self.gripper.move_and_wait_for_pos(pos, self.grip_speed, self.grip_force)

    def open_gripper(self) -> None:
        """Fully open the gripper and wait."""
        self.grip(self.gripper.get_open_position())

    def close_gripper(self) -> None:
        """Fully close the gripper and wait."""
        self.grip(self.gripper.get_closed_position())

    # ------------------------------------------------------------------
    # Grab sequence
    # ------------------------------------------------------------------

    def grab(self, grab_depth: float = -0.135) -> None:
        """Perform a full pick at the current XY position.

        1. Descend by ``grab_depth`` (negative = down).
        2. Close the gripper (blocking — waits until gripped).
        3. Retract back up.
        """
        self.move_offset([0, 0, grab_depth])
        self.close_gripper()
        self.move_offset([0, 0, -grab_depth])

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Disconnect from the robot arm and gripper."""
        self.rtde_c.disconnect()
        self.rtde_r.disconnect()
        self.gripper.disconnect()

    def __enter__(self) -> "Robot":
        return self

    def __exit__(self, *_) -> None:
        self.close()
