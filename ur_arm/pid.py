import time


class PID:
    def __init__(self, Kp: float, Ki: float, Kd: float):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.prev_error = 0.0
        self.integral = 0.0
        self.last_time = None

    def compute(self, setpoint: float, measurement: float) -> float:
        time_step = time.time() - self.last_time if self.last_time is not None else 0.0
        if time_step <= 0.0:
            self._capture_last_time()  # Capture time for the first call
            return 0.0  # Prevent division by zero or negative time step
        error = setpoint - measurement
        self.integral += error * time_step
        derivative = (error - self.prev_error) / time_step
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        self.prev_error = error
        self._capture_last_time()  # Capture time for the first call
        return output
    
    def _capture_last_time(self):
        self.last_time = time.time() if self.last_time is None else self.last_time
