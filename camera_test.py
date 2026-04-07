import cv2

CAMERA_IP = '10.10.1.10'
CAMERA_PORT = '2024'
PASSWORD = 'CUgerenga'

camera_url = f"rtsp://admin:{PASSWORD}@{CAMERA_IP}:{CAMERA_PORT}/"
print(f"Connecting to camera at: {camera_url}")

cap = cv2.VideoCapture(camera_url)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame.")
        break

    # Display the frame
    cv2.imshow('Ethernet Camera', frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
