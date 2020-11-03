import tkinter as tk
import serial
import PySpin
import numpy
import matplotlib
import time
from tkinter import filedialog
from tkinter import messagebox
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class WavelengthGui(tk.Toplevel):


    def __init__(self,root,bnc,system,camera,nodemap,streamnodemap,exposuretime,gain,delaysvector,rootcameraframe,rootbncframe,rootstartintegration,rootstartseries,rootstartwavelength):

        tk.Toplevel.__init__(self,root)
        self.title("Acquisition: Wavelength series")

        self.protocol("WM_DELETE_WINDOW", self.closegui)

        self.bnc = bnc
        self.system = system
        self.camera = camera
        self.nodemap = nodemap
        self.exposure = exposuretime
        self.gain = gain
        self.delaysvector = delaysvector
        self.rootbncframe = rootbncframe
        self.rootcameraframe = rootcameraframe
        self.rootstartintegration = rootstartintegration
        self.rootstartseries = rootstartseries
        self.rootstartwavelength = rootstartwavelength

        self.rootbncframe.pack_forget()
        self.rootcameraframe.pack_forget()

        node_bufferhandling = PySpin.CEnumerationPtr(streamnodemap.GetNode("StreamBufferHandlingMode"))
        node_bufferhandling.SetIntValue(node_bufferhandling.GetEntryByName("NewestOnly").GetValue())

        self.erroroccurrence = False

        self.guiinit()



    def guiinit(self):

        self.leftframe = tk.Frame(self)
        self.leftframe.pack(side=tk.LEFT, padx=10)

        self.rightframe = tk.Frame(self)
        self.rightframe.pack(side=tk.LEFT, padx=10)

        self.description = tk.Message(self.leftframe, text="Series over a range of wavelengths. Please specify wavelength range, increment, number of frames per wavelength and beam-laser delay for the experiment.", font=("Helvetica",11), width=250)
        self.description.pack(side=tk.TOP, pady=10)

        self.lambdarangelabel = tk.Label(self.leftframe, text="Wavelength range in nm (min 200 - max 230):", font=("Helvetica",12))
        self.lambdarangelabel.pack(side=tk.TOP, pady=(20,5))

        self.lambdarangeframe = tk.Frame(self.leftframe)
        self.lambdarangeframe.pack(side=tk.TOP)

        self.lambdarangelower = tk.IntVar(self.lambdarangeframe, value=200)
        self.lambdarangestart = tk.Entry(self.lambdarangeframe, textvariable=self.delayrangelower, width=10)
        self.lambdarangestart.pack(side=tk.LEFT)

        self.lambdarangeupper = tk.IntVar(self.lambdarangeframe, value=230)
        self.lambdarangeend = tk.Entry(self.lambdarangeframe, textvariable=self.delayrangeupper, width=10)
        self.lambdarangeend.pack(side=tk.LEFT)

        self.incrementlabel = tk.Label(self.leftframe, text="Wavelength scanning increment in picometer:", font=("Helvetica",12))
        self.incrementlabel.pack(side=tk.TOP, pady=(40,5))

        self.increment = tk.StringVar(self.leftframe, value=10)
        self.incremententry = tk.Entry(self.leftframe, textvariable=self.increment, width=10)
        self.incremententry.pack(side=tk.TOP, pady=(0,20))

        self.framenumberlabel = tk.Label(self.leftframe, text="Number of averaged frames per wavelength:", font=("Helvetica",12))
        self.framenumberlabel.pack(side=tk.TOP, pady=(10,5))

        self.sumframes = tk.IntVar(self.leftframe, value=10)
        self.framenumber = tk.Entry(self.leftframe, textvariable=self.sumframes, width=10)
        self.framenumber.pack(side=tk.TOP, pady=(0,20))

        self.delayBlabel = tk.Label(self.leftframe, text="Beam - laser delay in microseconds (min 0 - max 2000):", font=("Helvetica",12))
        self.delayBlabel.pack(side=tk.TOP, pady=(10,5))

        self.delayB = tk.IntVar(self.leftframe, value=100)
        self.delayBentry = tk.Entry(self.leftframe, textvariable=self.delayB, width=10)
        self.delayBentry.pack(side=tk.TOP, pady=(0,20))

        self.startbutton = tk.Button(self.leftframe, text="Start Acquisition", background="green", command=self.startacquisition)
        self.startbutton.pack(side=tk.TOP, pady=(50,10))

        self.fig = matplotlib.figure.Figure(figsize=[4.6,7.2])
        self.grid = self.fig.add_gridspec(ncols=1, nrows=2)
        self.lastdelaydisplay = self.fig.add_subplot(self.grid[0,0])
        self.intensityvtime = self.fig.add_subplot(self.grid[1,0])

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.rightframe)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, expand=1, fill=tk.BOTH, pady=10)



    def startacquisition(self):

        self.node_triggermode = PySpin.CEnumerationPtr(self.nodemap.GetNode("TriggerMode"))
        self.node_triggermode.SetIntValue(1)

        try:
            self.numberofframes = int(self.framenumber.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter an integer number of frames")
            self.startbutton.configure(state=tk.NORMAL)
            return

        self.node_acquisitionmode = PySpin.CEnumerationPtr(self.nodemap.GetNode("AcquisitionMode"))
        self.node_acquisitionmode.SetIntValue(2)
        self.node_framecount = PySpin.CIntegerPtr(self.nodemap.GetNode("AcquisitionFrameCount"))
        self.node_framecount.SetValue(self.numberofframes)

        self.startbutton.configure(state=tk.DISABLED)

        self.filename = filedialog.asksaveasfilename(initialdir="C:/", title="Choose experiment file name", filetypes=(("numpy zip archive", "*.npz"),("All files", "*.*")))
        if self.filename[-4:] != ".npz":
            self.filename += ".npz"

        self.attributes("-topmost", "true")

        self.parameterfilename = self.filename[:-4] + "_parameters.txt"

        self.imageseries = {}

        self.lambdalist = []
        self.totalintensities = []

        self.currentdelay = "0.000" + str(self.delayBentry.get()) + "00000"
        inputstring = ":PULS2:DEL {}\r\n".format(self.currentdelay)
        self.bnc.write(inputstring.encode("utf-8"))
 
        self.startinpm = int(self.lambdarangestart.get())) * 1000
        self.stopinpm = int(self.lambdarangeend.get())) * 1000

        self.intensityvtime.set_xlim(self.startinpm-500, self.stopinpm+500)

        lambdascanrange = numpy.arange(self.startinpm, self.stopinpm + 1, int(self.incremententry.get()))

        for i in lambdascanrange:
            if i => 200000 and i <= 230000:
                #change the wavelength on the laser - figure this out once we have laser software
            else:
                messagebox.showerror("Error", "The entered wavelength values are out of range")
                self.startbutton.configure(state=tk.NORMAL)
                return

            time.sleep(0.100)

            self.imageloop()

            if self.erroroccurrence == True:
                break 
            
            lambdanm = str(i)[:3] + "." + str(i)[3:]
            self.imageseries[lambdanm] = self.sumimage
            self.lambdalist.append(i)
            self.totalintensities.append(numpy.sum(self.sumimage))

            self.lastdelaydisplay.clear()
            self.lastdelaydisplay.imshow(self.sumimage, cmap="gray", vmin=0)
            self.intensityvtime.clear()
            self.intensityvtime.plot(self.lambdalist, self.totalintensities)
            self.canvas.draw()
        

        if self.erroroccurrence == True:
            self.startbutton.configure(state=tk.NORMAL)
            return

        
        numpy.savez_compressed(self.filename, **self.imageseries)

        self.parameters = {"Exposure time": self.exposure, "Gain": self.gain, "Number of frames per delay": self.numberofframes, "Delay start": int(self.delayrangestart.get()), "Delay end": int(self.delayrangeend.get()), "Delay increment": int(self.incremententry.get()), "Delay A": self.delaysvector[0], "Delay B": self.currentdelay, "Delay C": self.delaysvector[1], "Delay D": self.delaysvector[2], "Delay E": self.delaysvector[3], "Delay F": self.delaysvector[4], "Delay G": self.delaysvector[5], "Delay H": self.delaysvector[6]}
        
        f = open(self.parameterfilename, "w")
        f.write(str(self.parameters))
        f.close

        messagebox.showinfo("Measurement finished", "Image has been saved under: {}, parameters under {}".format(self.filename, self.parameterfilename))



    def imageloop(self):

        self.sumimage = numpy.zeros((964,1288), int)

        self.camera.BeginAcquisition()

        for i in range(self.numberofframes):

            try:
                image_result = self.camera.GetNextImage(2000)
                image_data = image_result.GetNDArray()
                self.sumimage += image_data
                image_result.Release()

            except PySpin.SpinnakerException as ex:
                self.camera.EndAcquisition()
                self.erroroccurrence = True
                messagebox.showerror("Error","{}".format(ex))
                return
            
        try:
            self.camera.EndAcquisition()
        except PySpin.SpinnakerException:
            pass


    

    def closegui(self):

        self.nodemap = ""
        self.camera = ""

        self.rootbncframe.pack(side=tk.LEFT)
        self.rootcameraframe.pack(side=tk.LEFT)

        self.rootstartintegration.configure(state=tk.NORMAL)
        self.rootstartseries.configure(state=tk.NORMAL)
        self.rootstartwavelength.configure(state=tk.NORMAL)

        self.destroy()
