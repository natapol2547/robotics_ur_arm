from pypylon import pylon
import cv2

# 1. Target the specific IP address of your Basler camera
ip_address = '10.10.1.10'
info = pylon.DeviceInfo()
info.SetPropertyValue('IpAddress', ip_address)

try:
    # 2. Create the camera object directly from the IP address
    factory = pylon.TlFactory.GetInstance()
    camera = pylon.InstantCamera(factory.CreateFirstDevice(info))

    camera.Open()

    # 3. "No Wait" Strategy: GrabStrategy_LatestImageOnly
    # This automatically drops old frames in the buffer so you only ever process the current moment.
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    # Converter to easily change the raw camera data into an OpenCV image format
    converter = pylon.ImageFormatConverter()
    converter.OutputPixelFormat = pylon.PixelType_BGR8packed
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    print(f"Successfully connected to Basler camera at {ip_address}")

    while camera.IsGrabbing():
        # Wait up to 1000ms for a frame
        grabResult = camera.RetrieveResult(
            1000, pylon.TimeoutHandling_ThrowException)

        if grabResult.GrabSucceeded():
            # Convert and extract the image array
            image = converter.Convert(grabResult)
            frame = image.GetArray()

            # Show the live feed
            cv2.imshow('Basler Continuous Feed', frame)

            # Press 'q' to exit the loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        grabResult.Release()

except pylon.GenericException as e:
    print(f"Connection Error: {e}")
    print("Tip: Ensure your computer's network adapter is on the same subnet (e.g., 10.10.0.X).")

finally:
    if 'camera' in locals() and camera.IsOpen():
        camera.StopGrabbing()
        camera.Close()
    cv2.destroyAllWindows()
