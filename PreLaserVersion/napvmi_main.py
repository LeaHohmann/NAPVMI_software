import tkinter as tk
from tkinter import messagebox
import serial
import PySpin
import cameramodule
import bncmodule
import delayintegration
import kineticseries


class Root(tk.Tk):

    def __init__(self):

        tk.Tk.__init__(self)
        self.protocol("WM_DELETE_WINDOW", self.quitgui)

        self.title("NAP-VMI Experiment")

        self.system = PySpin.System.GetInstance()
        self.serialnumber = "18479311"
        self.camera = ""
        self.camerastatus = "disconnected"
        self.bncstatus = "disconnected"
        self.connectionstatus = 0

        self.moduleframe = tk.Frame(self)
        self.moduleframe.pack(side=tk.TOP)

        self.bncframe = tk.Frame(self.moduleframe)
        self.bncframe.pack(side=tk.LEFT, padx=30)
        self.connectbnc = tk.Button(self.bncframe, text="Connect to delay generator", command=self.bncconnect)
        self.connectbnc.pack(side=tk.TOP, ipadx=5, ipady=5, pady=(10,0))

        self.cameraframe = tk.Frame(self.moduleframe)
        self.cameraframe.pack(side=tk.LEFT, padx=30)
        self.connectcamera = tk.Button(self.cameraframe, text="Connect to camera", command=self.cameraconnect)
        self.connectcamera.pack(side=tk.TOP, ipadx=5, ipady=5, pady=(10,0))

        self.startexperimentframe = tk.Frame(self)
        self.startexperimentframe.pack(side=tk.TOP, pady=(30,10))
        self.startintegration = tk.Button(self.startexperimentframe, text="Delay integration acquisition", command=self.startdelayint, state=tk.DISABLED)
        self.startintegration.pack(side=tk.LEFT, ipadx=5, ipady=5)
        self.startseries = tk.Button(self.startexperimentframe, text="Kinetic series acquisition", command=self.startkineticseries, state=tk.DISABLED)
        self.startseries.pack(side=tk.LEFT, ipadx=5, ipady=5)



    def bncconnect(self):

        try:
            self.bnc = serial.Serial("COM5", baudrate=115200, bytesize=8, parity="N", stopbits=1, timeout=1)
        except:
            messagebox.showerror("Error", "Could not connect to BNC. Check connection, port number and baudrate and retry")
            return

        self.connectbnc.destroy()
        self.bncstatus = "connected"
        self.bncinit()
        
        self.connectionstatus += 1
        if self.connectionstatus == 2:
            self.startintegration.configure(state=tk.NORMAL, background="green")
            self.startseries.configure(state=tk.NORMAL, background="green")



    def bncinit(self):

        self.bncgui = bncmodule.DelayApp(self.bncframe, self.bnc)



    def cameraconnect(self):

        self.cameralist = self.system.GetCameras()
        
        if self.cameralist.GetSize() == 0:
            messagebox.showerror("Error", "No cameras connected. Connect a camera and try again")
            self.cameralist.Clear()
            return
        else:
            self.cameraident()
            self.cameralist.Clear()

        if self.camera == "":
            messagebox.showerror("Error", "Camera 18479311 not found. Connect the camera and retry.")
            return
        else:
            self.camerastatus = "connected"
            self.connectcamera.destroy()
            self.camerainit()

            self.connectionstatus += 1
            if self.connectionstatus == 2:
                self.startintegration.configure(state=tk.NORMAL, background="green")
                self.startseries.configure(state=tk.NORMAL, background="green")




    def cameraident(self):

        for cam in self.cameralist:
            tldevice_nodemap = cam.GetTLDeviceNodeMap()
            serialno = PySpin.CStringPtr(tldevice_nodemap.GetNode("DeviceSerialNumber")).ToString()
            del tldevice_nodemap

            if serialno == self.serialnumber:
                self.camera = cam
                self.camera.Init()
                break

            del cam




    def camerainit(self):

        self.cameragui = cameramodule.CameraApp(self.cameraframe,self.system,self.camera)




    def startdelayint(self):

        try:
            self.camera.BeginAcquisition()
            self.camera.EndAcquisition()

        except PySpin.SpinnakerException:
            messagebox.showerror("Error", "Camera is already streaming. Stop current acquisition and try again.")
            return
        
        self.checkdelays()

        exposure = self.cameragui.node_exposuretime.GetValue()
        gain = self.cameragui.node_gain.GetValue()

        self.startintegration.configure(state=tk.DISABLED)
        self.startseries.configure(state=tk.DISABLED)

        self.delayintegrationgui = delayintegration.IntegrationGui(self,self.bnc,self.system,self.camera,self.cameragui.nodemap, self.cameragui.streamnodemap, exposure,gain,self.delaysvector,self.cameraframe,self.bncframe,self.startintegration, self.startseries)




    def startkineticseries(self):

        try:
            self.camera.BeginAcquisition()
            self.camera.EndAcquisition()

        except PySpin.SpinnakerException:
            messagebox.showerror("Error", "Camera is already streaming. Stop current acquisition and try again.")
            return

        
        self.checkdelays()
        
        exposure = self.cameragui.node_exposuretime.GetValue()
        gain = self.cameragui.node_gain.GetValue()

        self.startseries.configure(state=tk.DISABLED)
        self.startintegration.configure(state=tk.DISABLED)

        self.kineticseriesgui = kineticseries.SeriesGui(self, self.bnc, self.system, self.camera, self.cameragui.nodemap, self.cameragui.streamnodemap, exposure, gain, self.delaysvector, self.cameraframe, self.bncframe, self.startintegration, self.startseries)




    def checkdelays(self):

        channelnumbersvector = [1,3,4,5,6,7,8]
        self.delaysvector = []
        for i in channelnumbersvector:
            inputstring = ":PULS{}:DEL?\r\n".format(i)
            self.bnc.write(inputstring.encode("utf-8"))
            lastline = self.bnc.readline().decode("utf-8")
            self.delaysvector.append(lastline[:-2])




    def quitgui(self):

        if self.camerastatus == "connected" and self.cameragui.startlive["text"] == "Stop":
            messagebox.showerror("Error", "Acquisition running. Please stop acquisition before closing.")
            return
        if self.camerastatus == "connected" and self.cameragui.summedlive["text"] == "Stop":
            messagebox.showerror("Error", "Acquisition running. Please stop acquisition before closing.")
            return
        
        try:
            self.bncgui.quitapp()
        except:
            pass

        if self.bncstatus == "connected":
            self.bnc.close()

        if self.camerastatus == "connected":
            self.cameragui.quit_cameraapp()
            self.camera.DeInit()

        self.camera = ""
        self.system.ReleaseInstance()
        self.quit()




root = Root()
root.mainloop()
