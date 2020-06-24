import tkinter as tk
import serial
import PySpin
import numpy
import matplotlib
from tkinter import filedialog
from tkinter import messagebox
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class IntegrationGui(tk.Toplevel):


    def __init__(self,root,bnc,system,camera,nodemap,streamnodemap,exposuretime,gain,delaysvector,rootcameraframe,rootbncframe,rootstartintegration, rootstartseries):

        tk.Toplevel.__init__(self,root)
        self.title("Acquisition: Delay integration")

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

        self.rootbncframe.pack_forget()
        self.rootcameraframe.pack_forget()

        self.erroroccurrence = False

        node_bufferhandling = PySpin.CEnumerationPtr(streamnodemap.GetNode("StreamBufferHandlingMode"))
        node_bufferhandling.SetIntValue(node_bufferhandling.GetEntryByName("NewestOnly").GetValue())

        self.guiinit()



    def guiinit(self):
        
        self.leftframe = tk.Frame(self)
        self.leftframe.pack(side=tk.LEFT, padx=10)

        self.rightframe = tk.Frame(self)
        self.rightframe.pack(side=tk.LEFT, padx=10)

        self.description = tk.Message(self.leftframe, text="Integrates over a range of delays. Please specify delay range, increment and number of frames per delay.", font=("Helvetica",11), width=250)
        self.description.pack(side=tk.TOP, pady=10)

        self.delayrangelabel = tk.Label(self.leftframe, text="Delay range in microseconds (min 0 - max 2000):", font=("Helvetica",12))
        self.delayrangelabel.pack(side=tk.TOP, pady=(20,5))

        self.delayrangeframe = tk.Frame(self.leftframe)
        self.delayrangeframe.pack(side=tk.TOP)

        self.delayrangelower = tk.IntVar(self.delayrangeframe, value=0)
        self.delayrangestart = tk.Entry(self.delayrangeframe, textvariable=self.delayrangelower, width=10)
        self.delayrangestart.pack(side=tk.LEFT)

        self.delayrangeupper = tk.IntVar(self.delayrangeframe, value=2000)
        self.delayrangeend = tk.Entry(self.delayrangeframe, textvariable=self.delayrangeupper, width=10)
        self.delayrangeend.pack(side=tk.LEFT)

        self.incrementlabel = tk.Label(self.leftframe, text="Delay scanning increment:", font=("Helvetica",12))
        self.incrementlabel.pack(side=tk.TOP, pady=(40,5))

        self.increment = tk.IntVar(self.leftframe, value=100)
        self.incremententry = tk.Entry(self.leftframe, textvariable=self.increment, width=10)
        self.incremententry.pack(side=tk.TOP, pady=(0,20))

        self.framenumberlabel = tk.Label(self.leftframe, text="Number of averaged frames per delay:", font=("Helvetica",12))
        self.framenumberlabel.pack(side=tk.TOP, pady=(10,5))

        self.sumframes = tk.IntVar(self.leftframe, value=10)
        self.framenumber = tk.Entry(self.leftframe, textvariable=self.sumframes, width=10)
        self.framenumber.pack(side=tk.TOP, pady=(0,20))

        self.startbutton = tk.Button(self.leftframe, text="Start Acquisition", background="green", command=self.startacquisition)
        self.startbutton.pack(side=tk.TOP, pady=(50,10))

        self.fig = matplotlib.figure.Figure(figsize=[4.6,7.2])
        self.grid = self.fig.add_gridspec(ncols=1, nrows=2)
        self.integrateddisplay = self.fig.add_subplot(self.grid[0,0])
        self.lastdelaydisplay = self.fig.add_subplot(self.grid[1,0])

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.rightframe)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, expand=1, fill=tk.BOTH, pady=10)



    def startacquisition(self):

        self.node_triggermode = PySpin.CEnumerationPtr(self.nodemap.GetNode("TriggerMode"))
        self.node_triggermode.SetIntValue(0)

        self.startbutton.configure(state=tk.DISABLED)

        self.filename = filedialog.asksaveasfilename(initialdir="C:/", title="Choose image file name", filetypes=(("binary numpy array file","*.npy"),("All files","*.*")))
        if self.filename[-4:] != ".npy":
            self.filename += ".npy"

        self.attributes("-topmost", "true")

        self.parameterfilename = self.filename[:-4] + "_parameters.txt"

        delayscanrange = numpy.arange(int(self.delayrangestart.get()), int(self.delayrangeend.get()) + 1, int(self.incremententry.get()))

        try:
            self.numberofframes = int(self.framenumber.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter an integer number of frames")
            self.startbutton.configure(state=tk.NORMAL)
            return
        
        self.integratedimage = numpy.zeros((964,1288), int)

        for i in delayscanrange:
            if i < 1000:
                currentdelay = "0.000" + str(i) + "00000"
            elif i<= 2000:
                currentdelay = "0.00" + str(i) + "00000"
            else:
                messagebox.showerror("Error", "Maximum delay is 2000us")
                self.startbutton.configure(state=tk.NORMAL)
                return
            inputstring = ":PULS2:DEL {}\r\n".format(currentdelay)
            self.bnc.write(inputstring.encode("utf-8"))
            lastline = self.bnc.readline().decode("utf-8")

            self.imageloop()

            if self.erroroccurrence == True:
                break 

            self.integratedimage += self.sumimage

            self.integrateddisplay.clear()
            self.integrateddisplay.imshow(self.integratedimage, cmap="gray", vmin=0)
            self.lastdelaydisplay.clear()
            self.lastdelaydisplay.imshow(self.sumimage, cmap="gray", vmin=0)
            self.canvas.draw()
        
        if self.erroroccurrence == True:
            self.startbutton.configure(state=tk.NORMAL)
            return

        numpy.save(self.filename, self.integratedimage)

        self.parameters = {"Exposure time": self.exposure, "Gain": self.gain, "Number of frames per delay": str(self.numberofframes), "Delay start": int(self.delayrangestart.get()), "Delay end": int(self.delayrangeend.get()), "Delay increment": int(self.incremententry.get()), "Delay A": self.delaysvector[0], "Delay C": self.delaysvector[1], "Delay D": self.delaysvector[2], "Delay E": self.delaysvector[3], "Delay F": self.delaysvector[4], "Delay G": self.delaysvector[5], "Delay H": self.delaysvector[6]}
        
        f = open(self.parameterfilename, "w")
        f.write(str(self.parameters))
        f.close

        messagebox.showinfo("Measurement finished", "Image has been saved under: {}, parameters under {}".format(self.filename, self.parameterfilename))



    def imageloop(self):

        self.sumimage = numpy.zeros((964,1288), int)

        self.camera.BeginAcquisition()

        for i in range(self.numberofframes):

            try:
                image_result = self.camera.GetNextImage(5000)
                image_data = image_result.GetNDArray()
                self.sumimage += image_data

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

        self.destroy()
