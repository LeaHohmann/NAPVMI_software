import tkinter as tk
import serial
import PySpin
from tkinter import filedialog
from tkinter import messagebox


class IntegrationGui(tk.Toplevel):


    def __init__(self,root,bnc,system,camera,nodemap,exposuretime,gain,delaysvector,rootcameraframe,rootbncframe):

        tk.Toplevel.__init__(self,root)
        self.title("Acquisition: Delay integration")

        self.protocol("WM_DELETE_WINDOW", self.closegui)

        self.bnc = bnc
        self.system = system
        self.camera = camera
        self.nodemap = nodemap
        self.exposuretime = exposuretime
        self.gain = gain
        self.delaysvector = delaysvector
        self.rootbncframe = rootbndframe
        self.rootcameraframe = rootcameraframe

        self.erroroccurrence = False

        self.guiinit()



    def guiinit(self):

        self.description = tk.Message(self, text="Integrates over a range of delays. Please specify delay range, increment and number of frames per delay.", font=("Helvetica",12))
        self.description.pack(side=tk.TOP, pady=10)

        self.delayrangelabel = tk.Label(self, text="Delay range in microseconds (min 0 - max 2000):", font=("Helvetica",12))
        self.delayrangelabel.pack(side=tk.TOP, pady=(20,5))

        self.delayrangelower = tk.IntVar(self, value=0)
        self.delayrangestart = tk.Entry(self, textvariable=self.delayrangelower, width=10)
        self.delayrangestart.pack(side=tk.LEFT)

        self.delayrangeupper = tk.IntVar(self, value=2000)
        self.delayrangeend = tk.Entry(self, textvariable=self.delayrangeupper, width=10)
        self.delayrangeend.pack(side=tk.LEFT)

        self.incrementlabel = tk.Label(self, text="Delay scanning increment:", font=("Helvetica",12))
        self.incrementlabel.pack(side=tk.TOP, pady=(40,5))

        self.increment = tk.IntVar(self, value=100)
        self.incremententry = tk.Entry(self, textvariable=self.increment, width=10)
        self.incremententry.pack(side=tk.TOP, pady=(0,20))

        self.framenumberlabel = tk.Label(self, text="Number of averaged frames per delay:", font=("Helvetica",12))
        self.framenumberlabel.pack(side=tk.TOP, pady=(10,5))

        self.sumframes = tk.IntVar(self, value=10)
        self.framenumber = tk.Entry(self, textvariable=self.sumframes, width=10)
        self.framenumber.pack(side=tk.TOP, pady=(0,20))

        self.startbutton = tk.Button(self, text="Start Acquisition", background="green", command=self.startacquisition)
        self.startbutton.pack(side=tk.TOP, pady=(50,10))



    def startacquisition(self):

        self.node_triggermode = PySpin.CEnumerationPtr(self.nodemap.GetNode("TriggerMode"))
        self.node_triggermode.SetIntValue(1)

        self.startbutton.configure(state=tk.DISABLED)

        self.filename = filedialog.asksaveasfilename(initialdir="C:/", title="Choose image file name", filetypes=(("binary numpy array file","*.npy"),("All files","*.*")))
        self.parameterfilename = filedialog.asksaveasfilename(initialdir="C:/", title="Choose parameter file name", filetypes=(("Text files","*.txt"),("All files","*.*")))

        delayscanrange = numpy.arange(self.delayrangelower, self.delayrangeupper + 1, self.increment)

        try:
            self.numberofframes = int(self.framenumber.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter an integer number of frames")
            self.startbutton.configure(state=tk.NORMAL)
            return
        
        self.integratedimage = numpy.zeros((964,1288), int)
        
        self.camera.BeginAcquisition()

        for i in delayscanrange:
            inputstring = "PULS2:DEL {}\r\n".format(i)
            self.bnc.write(inputstring.encode("utf-8"))
            lastline = self.bnc.readline().decode("utf-8")

            self.imageloop(i)
            if self.erroroccurrence == True:
                break 

            self.integratedimage += self.sumimage

        try:
            self.camera.EndAcquisition()
        except PySpin.SpinnakerException:
            pass

        if self.erroroccurrence == True:
            self.startbutton.configure(state=tk.NORMAL)
            return

        numpy.save(self.filename, self.integratedimage)

        self.parameters = {"Exposure time": self.exposure, "Gain": self.gain, "Number of frames per delay": self.numberofframes, "Delay start": self.delayrangelower, "Delay end": self.delayrangeupper, "Delay increment": self.increment, "Delay A": self.delaysvector[0], "Delay C": self.delaysvector[1], "Delay D": self.delaysvector[2], "Delay E": self.delaysvector[3], "Delay F": self.delaysvector[4], "Delay G": self.delaysvector[5], "Delay H": self.delaysvector[6]}
        
        f = open(self.parameterfilename, "w")
        f.write(str(self.parameters))
        f.close

        self.startbutton.configure(state=tk.NORMAL)

        self.messagebx.showinfo("Measurement finished", "Image has been saved under: {}, parameters under {}".format(self.filename, self.parameterfilename))



    def imageloop(self):

        self.sumimage = numpy.zeros((964,1288), int)

        for i in range(self.numberofframes):

            try:
                image_result = self.camera.GetNextImage(5000)
                image_data = image_result.GetNDArray()
                self.sumimage += image_data

            except PySpin.SpinnakerException as ex:
                self.camera.EndAcquisition()
                self.erroroccurrence = True
                messagebox.showerror("Error","{}".format(ex))
            

    
    def closegui(self):

        self.rootbncframe.pack()
        self.rootcameraframe.pack()

        self.destroy()
