import tkinter as tk
from tkinter import messagebox
import serial
import PySpin
import cameramodule
import bncmodule


class Root(tk.Tk):

    def __init__(self):

        tk.Tk.__init__(self)
        self.protocol("WM_DELETE_WINDOW", self.quitgui)

        self.system = PySpin.System.GetInstance()
        self.serialnumber = "18479311"
        self.camera = ""
        self.camerastatus = "disconnected"
        self.bncstatus = "disconnected"
        self.connectionstatus = 0

        self.bncframe = tk.Frame(self)
        self.bncframe.pack(side=tk.LEFT, padx=30)
        self.connectbnc = tk.Button(self.bncframe, text="Connect to delay generator", command=self.bncconnect)
        self.connectbnc.pack(side=tk.TOP, ipadx=5, ipady=5)

        self.cameraframe = tk.Frame(self)
        self.cameraframe.pack(side=tk.LEFT, padx=30)
        self.connectcamera = tk.Button(self.cameraframe, text="Connect to camera", command=self.cameraconnect)
        self.connectcamera.pack(side=tk.TOP, ipadx=5, ipady=5)

        self.startexperimentframe = tk.Frame(self)
        self.startexperimentframe.pack(side=tk.BOTTOM, pady=20)
        self.startintegration = tk.Button(self.startexperimentframe, text="Delay integration experiment", background="green", command=self.startdelayint, state=tk.DISABLED)
        #self.startintegration.pack(side=tk.CENTER, ipadx=5, ipady=5)



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
            self.startintegration.configure(state=tk.NORMAL)



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
                self.startintegration.configure(state=tk.NORMAL)




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

        channelnumbersvector = [1,3,4,5,6,7,8]
        delaysvector = []
        for i in channelnumbersvector:
            inputstring = ":PULS{}:DEL?\r\n".format(i)
            self.bnc.write(inputstring.encode("utf-8"))
            lastline = self.bnc.readline().decode("utf-8")
            delaysvector.append(lastline[:-2])

        self.bncframe.pack_forget()
        self.cameraframe.pack_forget()



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
