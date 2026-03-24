import socket
import time


class Robot:
    def __init__(
        self,
        pose_host: str,
        pose_port: int,
        move_host: str,
        move_port: int,
        grip_host: str,
        grip_port: int,
        move_accel: float = 2.0,
        move_vel: float = 10.0,
        pose_calibration: tuple[float, float] = (0.0, 0.0),
    ):
        self.move_accel = move_accel
        self.move_vel = move_vel
        self.pose_calibration = pose_calibration

        self.pose_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pose_tcp.connect((pose_host, pose_port))

        self.move_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.move_tcp.connect((move_host, move_port))

        self.grip_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.grip_tcp.connect((grip_host, grip_port))

    # ------------------------------------------------------------------
    # Pose
    # ------------------------------------------------------------------

    def get_pose(self) -> list[float] | None:
        """Read one pose frame from the streaming pose server.

        The server continuously pushes frames in the format ``#x,y#\\n``
        where x and y are values in millimetres.  Returns a calibrated
        ``[x, y]`` list in metres, or ``None`` when the frame is invalid
        (e.g. the server sends ``#,#\\n`` to signal *no target*).
        """
        raw = self.pose_tcp.recv(1024).decode().strip()
        if raw == "#,#":
            return None
        try:
            values = list(
                map(lambda v: round(float(v), 2) / 1000, raw.replace("#", "").split(","))
            )
            values[0] -= self.pose_calibration[0]
            values[1] -= self.pose_calibration[1]
            return values
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------------

    def move(self, pose: list[float]) -> None:
        """Send a *relative* move command to the robot arm using URScript.

        ``pose`` is a list of up to 6 floats ``[dx, dy, dz, rx, ry, rz]``
        (missing elements default to 0).  The command is executed as
        ``movej`` relative to the current TCP pose.
        """
        padded = list(pose) + [0.0] * (6 - len(pose))
        dx, dy, dz, rx, ry, rz = padded[:6]
        cmd = (
            f"movej(pose_add(get_actual_tcp_pose(),"
            f"p[{dx},{dy},{dz},{rx},{ry},{rz}]),"
            f"{self.move_accel},{self.move_vel},0,0)\n"
        )
        self.move_tcp.send(cmd.encode("utf-8"))

    def move_to(self, pose: list[float]) -> None:
        """Send an *absolute* move command using URScript ``movej``.

        ``pose`` must be a 6-element list ``[x, y, z, rx, ry, rz]`` in
        the robot's base frame (metres / radians).
        """
        padded = list(pose) + [0.0] * (6 - len(pose))
        x, y, z, rx, ry, rz = padded[:6]
        cmd = (
            f"movej(p[{x},{y},{z},{rx},{ry},{rz}],"
            f"{self.move_accel},{self.move_vel},0,0)\n"
        )
        self.move_tcp.send(cmd.encode("utf-8"))

    # ------------------------------------------------------------------
    # Gripper
    # ------------------------------------------------------------------

    def activate_gripper(self, force: int = 1) -> bool:
        """Initialise the gripper and open it fully.

        Sends ``GET ACT`` to check activation state, sets the force, and
        opens the fingers to position 0.  Returns ``True`` if the gripper
        was already activated before this call.
        """
        self.grip_tcp.send(b"GET ACT\n")
        response = str(self.grip_tcp.recv(10), "UTF-8")
        already_active = "1" in response
        self.grip_tcp.send(f"SET FOR {force}\n".encode())
        self.grip_tcp.send(b"SET POS 0\n")
        return already_active

    def grip(self, pos: int) -> None:
        """Set the gripper finger position.

        ``pos`` ranges from **0** (fully open) to **255** (fully closed).
        """
        pos = max(0, min(255, int(pos)))
        self.grip_tcp.send(f"SET POS {pos}\n".encode())

    def open_gripper(self) -> None:
        """Fully open the gripper (position 0)."""
        self.grip(0)

    def close_gripper(self) -> None:
        """Fully close the gripper (position 255)."""
        self.grip(255)

    # ------------------------------------------------------------------
    # Grab sequence
    # ------------------------------------------------------------------

    def grab(self, grab_depth: float = -0.135, settle_time: float = 3.0) -> None:
        """Perform a full pick sequence at the current XY position.

        1. Descend by ``grab_depth`` (negative = downward).
        2. Wait ``settle_time`` seconds for the arm to reach the target.
        3. Close the gripper.
        4. Wait 1 second for the gripper to close.
        5. Retract back up by ``-grab_depth``.
        """
        self.move([0, 0, grab_depth])
        time.sleep(settle_time)
        self.close_gripper()
        time.sleep(1.0)
        self.move([0, 0, -grab_depth])

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close all socket connections."""
        for sock in (self.pose_tcp, self.move_tcp, self.grip_tcp):
            try:
                sock.close()
            except OSError:
                pass

    def __enter__(self) -> "Robot":
        return self

    def __exit__(self, *_) -> None:
        self.close()
