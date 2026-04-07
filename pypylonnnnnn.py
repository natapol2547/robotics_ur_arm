from pypylon import pylon

dc = pylon.DeviceInfo()
dc.SetDeviceClass("BaslerGTC/Basler/GenTL_Producer_for_Basler_blaze_101_cameras")
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice(dc))
camera.Open()

camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        pylonDataContainer = grabResult.GetDataContainer()

        for componentIndex in range(pylonDataContainer.DataComponentCount):

            pylonDataComponent = pylonDataContainer.GetDataComponent(componentIndex)
            if pylonDataComponent.ComponentType == pylon.ComponentType_Intensity:
                intensity = pylonDataComponent.Array
                _2d_intensity = intensity.reshape(pylonDataComponent.Height, pylonDataComponent.Width)

            pylonDataComponent.Release()

    grabResult.Release()

camera.StopGrabbing()