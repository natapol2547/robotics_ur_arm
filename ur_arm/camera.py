

class Camera:
    def __init__(self, camera_id: int = 0):
        import cv2
        self.cap = cv2.VideoCapture(camera_id)

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to capture frame from camera.")
        return frame
    
    def get_block_pos(self):
        pass

    def release(self):
        self.cap.release()