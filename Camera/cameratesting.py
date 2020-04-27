import PySpin
import tkinter as tk
import numpy
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def quit_window(camera):
    global running
    running = False
    
    try:
        camera.EndAcquisition()
    except PySpin.SpinnakerException as ex:
        print("Didn't stop acquisition: {}".format(ex))
    
    camera.DeInit()
    global system
    system.ReleaseInstance()
    root.quit()

def acquisition(camera,nodemap):

    streamnodemap = camera.GetTLStreamNodeMap()

    node_bufferhandlingmode = PySpin.CEnumerationPtr(streamnodemap.GetNode('StreamBufferHandlingMode'))
    node_bhmode_newestonly = node_bufferhandlingmode.GetEntryByName('NewestOnly')

    if not PySpin.IsAvailable(node_bhmode_newestonly) or not PySpin.IsReadable(node_bhmode_newestonly) or not PySpin.IsWritable(node_bufferhandlingmode):
        print("Couldn't alter buffer handling mode")
        return

    node_bufferhandlingmode.SetIntValue(node_bhmode_newestonly.GetValue())
    
    node_acquisitionmode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
    node_acmode_continuous = node_acquisitionmode.GetEntryByName('Continuous')

    if not PySpin.IsAvailable(node_acmode_continuous) or not PySpin.IsReadable(node_acmode_continuous) or not PySpin.IsWritable(node_acquisitionmode):
        print("Couldn't set acquisition mode")
        return

    node_acquisitionmode.SetIntValue(node_acmode_continuous.GetValue())

    camera.BeginAcquisition()
    
    while running == True:
        try:
            image_result = camera.GetNextImage()
            image_data = image_result.GetNDArray()

            imageplot.figimage(image_data, cmap="gray")
            imageplot.clf()

            image_result.Release()

        except PySpin.SpinnakerException as ex:
            print("Error: {}".format(ex))



system = PySpin.System.GetInstance()
cameralist = system.GetCameras()
camera = ""
running = True

if cameralist.GetSize() == 0:
    print("No cameras connected")

for cam in cameralist:

    tldevice_nodemap = cam.GetTLDeviceNodeMap()
    node_serialno = PySpin.CStringPtr(tldevice_nodemap.GetNode("DeviceSerialNumber"))
    if PySpin.IsAvailable(node_serialno) and PySpin.IsReadable(node_serialno):
        serialnumber = node_serialno.ToString()
    else:
        serialnumber = "0"

    if serialnumber == "18479311":
        camera = cam
        del cam
        camera.Init()
        nodemap = camera.GetNodeMap()

    cameralist.Clear()

if camera == "":
    print("Couldn't connect to camera")

else:

    root = tk.Tk()

    imageplot = matplotlib.figure.Figure()
    
    canvas = FigureCanvasTkAgg(imageplot, master=root)
    canvas.get_tk_widget().pack(side=tk.TOP, expand=1, fill=tk.BOTH)

    start = tk.Button(root, text="Start", command=lambda:acquisition(camera,nodemap))
    start.pack(side=tk.TOP, ipadx=5, ipady=5, pady=10)

    root.protocol("WM_DELETE_WINDOW", lambda:quit_window(camera))
    root.mainloop()
    
