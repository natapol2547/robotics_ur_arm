import cv2

# Construct the stream URL with your credentials
# Note: The exact path (like /stream) depends on your specific routing software
stream_url = "rtsp://admin:CUgerenga@10.10.1.10:2024/stream"

cap = cv2.VideoCapture(stream_url)

# Set the buffer size to 1 to always get the latest frame (no waiting/lag)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap.isOpened():
    print("Cannot open the stream. Double-check the URL path and server.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab the frame.")
        break

    cv2.imshow('Camera Stream', frame)

    # Press 'q' to quit the continuous loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
