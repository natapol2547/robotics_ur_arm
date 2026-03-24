import cv2
import numpy as np

# A required empty function for OpenCV trackbars


def nothing(x):
    pass


# 1. Create a window for the sliders
cv2.namedWindow("Trackbars")
cv2.resizeWindow("Trackbars", 400, 300)

# 2. Create sliders for Min and Max values (0 to 255)
# L = Lightness, A = Green-to-Red, B = Blue-to-Yellow
cv2.createTrackbar("L Min", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L Max", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("A Min", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("A Max", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("B Min", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("B Max", "Trackbars", 255, 255, nothing)

# Open the laptop camera (0 is usually the default built-in camera)
cap = cv2.VideoCapture(1)

print("--- INSTRUCTIONS ---")
print("1. Adjust the sliders until ONLY your block is visible in the 'Result' window.")
print("2. Press 'c' on your keyboard to print the values so you can copy them.")
print("3. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the normal BGR image to LAB color space
    lab_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

    # Read the current positions of all 6 sliders
    l_min = cv2.getTrackbarPos("L Min", "Trackbars")
    l_max = cv2.getTrackbarPos("L Max", "Trackbars")
    a_min = cv2.getTrackbarPos("A Min", "Trackbars")
    a_max = cv2.getTrackbarPos("A Max", "Trackbars")
    b_min = cv2.getTrackbarPos("B Min", "Trackbars")
    b_max = cv2.getTrackbarPos("B Max", "Trackbars")

    # Create arrays for our color boundaries
    lower_bound = np.array([l_min, a_min, b_min])
    upper_bound = np.array([l_max, a_max, b_max])

    # Create a "Mask": a black and white image where the target color is white
    mask = cv2.inRange(lab_frame, lower_bound, upper_bound)

    # Apply the mask over the original image so we only see the targeted color
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # Show the different views
    cv2.imshow("Original Camera", frame)
    cv2.imshow("Mask (Target should be white)", mask)
    cv2.imshow("Result", result)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        # Print the values clearly so you can copy and paste them into File 2
        print("\n--- COPY THESE VALUES INTO FILE 2 ---")
        print(f"LOWER_LAB = np.array([{l_min}, {a_min}, {b_min}])")
        print(f"UPPER_LAB = np.array([{l_max}, {a_max}, {b_max}])")
        print("-------------------------------------")

cap.release()
cv2.destroyAllWindows()
