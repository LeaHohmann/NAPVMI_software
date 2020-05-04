import PySpin


def nodetesting(camera):
    nodemap = camera.GetNodeMap()

    node_autoexposure = PySpin.CEnumerationPtr(nodemap.GetNode("ExposureAuto"))
    #node_autoexposure.SetIntValue(2)
    autoexposure_status = node_autoexposure.GetCurrentEntry().GetDisplayName()
    print("Auto Exposure: {}".format(autoexposure_status))

    node_autogain = PySpin.CEnumerationPtr(nodemap.GetNode("GainAuto"))
    #node_autogain.SetIntValue(2)
    autogain_status = node_autogain.GetCurrentEntry().GetDisplayName()
    print("Auto Gain: {}".format(autogain_status))

    node_autoexpocomp = PySpin.CEnumerationPtr(nodemap.GetNode("pgrExposureCompensationAuto"))
    node_autoexpocomp.SetIntValue(0)
    autoexpocomp_status = node_autoexpocomp.GetCurrentEntry().GetDisplayName()
    print("Auto Exposure compensation: {}".format(autoexpocomp_status))

    node_exposuretime = PySpin.CFloatPtr(nodemap.GetNode("ExposureTime"))
    print(node_exposuretime.GetValue())
    node_exposuretime.SetValue(25000.00)
    print(node_exposuretime.GetValue())



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
