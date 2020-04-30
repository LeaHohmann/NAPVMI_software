import PySpin


def nodetesting(camera):
    nodemap = camera.GetNodeMap()

    node_autoexposure = PySpin.CEnumerationPtr(nodemap.GetNode("ExposureAuto"))
    node_autoexposure_continuous = node_autoexposure.GetEntryByName("Continuous")
    node_autoexposure.SetIntValue(node_autoexposure_continuous.GetValue())
    autoexposure_status = node_autoexposure.GetCurrentEntry().GetValue()
    print("Auto Exposure: {}".format(autoexposure_status))



system = PySpin.System.GetInstance()

camera = ""

cameralist = system.GetCameras()

if cameralist.GetSize() == 0:
    print("No cameras found")
    cameralist.Clear()

else:
    for cam in cameralist:
        tldevice_nodemap = cam.GetTLDeviceNodeMap()
        node_serialno = PySpin.CStringPtr(tldevice_nodemap.GetNode("DeviceSerialNumber"))
        serialno = node_serialno.ToString()
        if serialno == "18479311":
            camera = cam
            camera.Init()

    del cam
    cameralist.Clear()

    if camera == "":
        print("Camera not found")
    else:
        nodetesting(camera)
        camera.DeInit()
        del camera

system.ReleaseInstance()
