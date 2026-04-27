import cv2
import numpy as np


class Camera:
    def __init__(self, camera_id: int = 0, debug: bool = False):
        self.cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.debug = debug

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to capture frame from camera.")
        return frame

    def get_block_pos(self, lower_lab: list[int], upper_lab: list[int], min_area_pixels: int = 1000):
        frame = self.get_frame()
        # Convert the video feed to LAB color space
        lab_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

        # Apply the color limits to create our black and white mask
        mask = cv2.inRange(lab_frame, lower_lab, upper_lab)

        # Optional cleanup step: this removes tiny "dots" of noise in the background
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=2)

        # 3. Find outlines (contours/blobs) of the white shapes in the mask
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        valid_contours = []

        # 4. Filter out any blobs that are too small
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > min_area_pixels:
                valid_contours.append(cnt)

        # 5. If we found at least one large enough blob...
        if len(valid_contours) > 0:

            # Grab only the biggest blob (in case there are multiple objects of the same color)
            biggest_contour = max(valid_contours, key=cv2.contourArea)

            # Draw the tightest rotating box around our shape
            # This returns: (center_x, center_y), (width, height), angle
            rect = cv2.minAreaRect(biggest_contour)
            center, dimensions, angle = rect

            # Convert the center coordinates to whole numbers (pixels)
            center_x, center_y = int(center[0]), int(center[1])

            # Normalize so that block_y is always the longer side and block_x the shorter.
            # minAreaRect angle is in (-90, 0]: the 'width' edge points in that direction.
            # If height > width, the longer axis is perpendicular → shift angle by +90 to keep
            # the reported angle as the orientation of the longer (Y) side, giving range (-90, 90].
            w, h = dimensions
            if h < w:
                block_x, block_y = int(w), int(h)
                angle = angle + 90
            else:
                block_x, block_y = int(h), int(w)

            # Get the 4 corners of our rotated box so we can draw it
            box = cv2.boxPoints(rect)
            box = np.int32(box)

            if self.debug:

                # Get the 4 corners of our rotated box so we can draw it
                box = cv2.boxPoints(rect)
                box = np.int32(box)

                # Draw the green outline around the block
                cv2.drawContours(frame, [box], 0, (0, 255, 0), 2)

                # Draw a tiny red dot exactly in the middle
                cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

                # Create text showing the block dimensions and tilt angle
                text = f"X:{block_x} Y:{block_y} | Angle:{int(angle)}"

                # Put the text on the video feed next to the block
                cv2.putText(frame, text, (center_x - 80, center_y - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                # Show the final video feeds
                cv2.imshow("Block Detector Tracker", frame)

            return center_x, center_y, block_x, block_y, angle

        return None
    
    def get_cam_res(self):
        return self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def release(self):
        self.cap.release()
