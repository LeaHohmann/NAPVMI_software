import PySpin
import tkinter as tk

def quitthecamera(system):
    global camera
    camera =""
    system.ReleaseInstance()

def cameraident(cameralist,serialnumber):

    for cam in cameralist:

        device_nodemap = cam.GetTLDeviceNodeMap()

        node_serialno = PySpin.CStringPtr(device_nodemap.GetNode("DeviceSerialNumber"))
        if PySpin.IsAvailable(node_serialno) and PySpin.IsReadable(node_serialno):
            serialno = node_serialno.ToString()
        else:
            serialno = "0"

        if serialno == serialnumber:
            global camera
            camera = cam
            message = "Connected to camera"
            print(message)
            break
    
    import pdb; pdb.set_trace()
    
    if camera == "":
        message = "Camera not found"
        print(message)

    del cam
    return message
        

def camerainit(system,serialnumber):

    cameralist = system.GetCameras()

    if cameralist.GetSize() == 0:
        message = "No cameras connected. Connect a camera and try again."
        print(message)
        cameralist.Clear()

    else:
        cameraident(cameralist,serialnumber)

    cameralist.Clear()

