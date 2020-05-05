import PySpin


def nodetesting(camera):
    nodemap = camera.GetNodeMap()
    streamnodemap = camera.GetTLStreamNodeMap()

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

    node_bufferhandling = PySpin.CEnumerationPtr(streamnodemap.GetNode("StreamBufferHandlingMode"))
    node_bufferhandling.SetIntValue(4)
    bufferhandling_status = node_bufferhandling.GetCurrentEntry().GetDisplayName()
    bhentrynumber = node_bufferhandling.GetCurrentEntry().GetValue()
    print("Buffer handling: {},{}".format(bufferhandling_status, bhentrynumber))

    node_acquisitionmode = PySpin.CEnumerationPtr(nodemap.GetNode("AcquisitionMode"))
    node_acquisitionmode.SetIntValue(1)
    acquisitionmode_status = node_acquisitionmode.GetCurrentEntry().GetDisplayName()
    acmodeentrynumber = node_acquisitionmode.GetCurrentEntry().GetValue()
    print("Acquisition Mode: {},{}".format(acquisitionmode_status, acmodeentrynumber))


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
